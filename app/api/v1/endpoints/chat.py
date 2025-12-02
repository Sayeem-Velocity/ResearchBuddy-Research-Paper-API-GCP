# app/api/v1/endpoints/chat.py
import uuid
import logging
import json
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict
from datetime import datetime

from app.core.mock_dependencies import get_mock_current_user, get_mock_firestore_db
from app.core.config import settings
from app.models.chat import ChatRequest, ChatResponse, ChatMessage, MessageRole, ChatHistory
from app.models.paper import Paper

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize the appropriate AI service based on configuration
def get_vertex_ai_service():
    """Get the appropriate Vertex AI service based on API key availability"""
    if settings.vertex_ai_api_key:
        try:
            from app.services.llm.vertex_ai import VertexAIService
            logger.info("Using real VertexAIService with Gemini 1.5 Flash")
            return VertexAIService()
        except Exception as e:
            logger.warning(f"Failed to initialize VertexAIService: {e}, falling back to mock")
    
    from app.services.llm.mock_vertex_ai import MockVertexAIService
    logger.info("Using MockVertexAIService")
    return MockVertexAIService()

vertex_ai_service = get_vertex_ai_service()

from app.services.storage.mock_firestore_manager import MockFirestoreSessionManager
_mock_session_manager = MockFirestoreSessionManager()

# Chat history storage
CHAT_HISTORY_DIR = Path(".mock_firestore_data/chat_history")
CHAT_HISTORY_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/{paper_id:path}/chat", response_model=ChatResponse)
async def chat_with_paper(
    paper_id: str,
    chat_request: ChatRequest,
    current_user: str = Depends(get_mock_current_user),
    db = Depends(get_mock_firestore_db)
):
    """
    Chat with a specific paper using AI
    """
    try:
        # Decode the paper_id if it's URL encoded
        from urllib.parse import unquote
        decoded_paper_id = unquote(paper_id)
        
        logger.info(f"Chat request for paper {decoded_paper_id} from user {current_user}")
        
        # Try to find the paper in any session
        paper = await _find_paper_by_id(current_user, decoded_paper_id)
        
        if not paper:
            logger.warning(f"Paper {decoded_paper_id} not found for user {current_user}")
            # Return a helpful response even if paper not found
            return ChatResponse(
                message_id=str(uuid.uuid4()),
                response="I apologize, but I couldn't find the specific paper in our system. However, I can try to answer your question based on general knowledge. What would you like to know?",
                papers_referenced=[],
                timestamp=datetime.utcnow()
            )
        
        # Load existing chat history
        chat_history = _load_chat_history(current_user, decoded_paper_id)
        
        # Generate response using AI service
        response_text = await vertex_ai_service.chat_with_paper(
            message=chat_request.message,
            paper=paper,
            chat_history=chat_history
        )
        
        # Create message IDs
        user_message_id = str(uuid.uuid4())
        assistant_message_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        # Save user message to history
        user_message = ChatMessage(
            message_id=user_message_id,
            session_id=decoded_paper_id,
            role=MessageRole.USER,
            content=chat_request.message,
            papers_context=[decoded_paper_id],
            timestamp=timestamp
        )
        
        # Save assistant message to history
        assistant_message = ChatMessage(
            message_id=assistant_message_id,
            session_id=decoded_paper_id,
            role=MessageRole.ASSISTANT,
            content=response_text,
            papers_context=[decoded_paper_id],
            timestamp=timestamp
        )
        
        # Append to history and save
        chat_history.append(user_message.dict())
        chat_history.append(assistant_message.dict())
        _save_chat_history(current_user, decoded_paper_id, chat_history)
        
        return ChatResponse(
            message_id=assistant_message_id,
            response=response_text,
            papers_referenced=[decoded_paper_id],
            timestamp=timestamp
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.get("/{paper_id:path}/chat/history")
async def get_chat_history(
    paper_id: str,
    current_user: str = Depends(get_mock_current_user),
    db = Depends(get_mock_firestore_db)
):
    """
    Get chat history for a paper
    """
    try:
        from urllib.parse import unquote
        decoded_paper_id = unquote(paper_id)
        
        # Load chat history
        messages = _load_chat_history(current_user, decoded_paper_id)
        
        return ChatHistory(
            session_id=decoded_paper_id,
            messages=[ChatMessage(**msg) for msg in messages],
            total_messages=len(messages)
        )
        
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat history")


def _get_chat_history_file(user_id: str, paper_id: str) -> Path:
    """Get the chat history file path for a specific user and paper"""
    # Create a safe filename from paper_id
    safe_id = paper_id.replace('/', '_').replace(':', '_').replace('?', '_')
    filename = f"{user_id}_{safe_id}.json"
    return CHAT_HISTORY_DIR / filename


def _load_chat_history(user_id: str, paper_id: str) -> List[Dict]:
    """Load chat history from file"""
    try:
        history_file = _get_chat_history_file(user_id, paper_id)
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Error loading chat history: {e}")
        return []


def _save_chat_history(user_id: str, paper_id: str, messages: List[Dict]):
    """Save chat history to file"""
    try:
        history_file = _get_chat_history_file(user_id, paper_id)
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, indent=2, default=str)
        logger.info(f"Saved chat history: {len(messages)} messages")
    except Exception as e:
        logger.error(f"Error saving chat history: {e}")


async def _find_paper_by_id(user_id: str, paper_id: str) -> Optional[Paper]:
    """Helper function to find a paper by ID across all sessions"""
    try:
        # Load papers data
        papers_data = _mock_session_manager._load_json(_mock_session_manager.papers_file)
        
        # Search through all user sessions
        for session_key, papers_list in papers_data.items():
            if not session_key.startswith(user_id):
                continue
                
            for paper_entry in papers_list:
                paper_data = paper_entry.get('paper', {})
                if paper_data.get('id') == paper_id:
                    # Reconstruct Paper object
                    from app.models.paper import PaperSource
                    return Paper(
                        id=paper_data['id'],
                        title=paper_data['title'],
                        abstract=paper_data['abstract'],
                        authors=paper_data['authors'],
                        published=paper_data['published'],
                        pdf_url=paper_data.get('pdf_url'),
                        source=PaperSource(paper_data['source']),
                        doi=paper_data.get('doi'),
                        citation_count=paper_data.get('citation_count'),
                        venue=paper_data.get('venue'),
                        keywords=paper_data.get('keywords', [])
                    )
        
        return None
        
    except Exception as e:
        logger.error(f"Error finding paper: {e}")
        return None
