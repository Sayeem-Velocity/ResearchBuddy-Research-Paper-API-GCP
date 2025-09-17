# app/models/chat.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    """Message role in chat"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    """Individual chat message"""
    message_id: str = Field(..., description="Unique message identifier")
    session_id: str = Field(..., description="Session this message belongs to")
    role: MessageRole = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    papers_context: List[str] = Field(default_factory=list, description="Paper IDs referenced in context")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        use_enum_values = True

class ChatRequest(BaseModel):
    """Request to send a chat message"""
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    include_papers: List[str] = Field(default_factory=list, description="Paper IDs to include in context")

class ChatResponse(BaseModel):
    """Response from chat"""
    message_id: str = Field(..., description="Message identifier")
    response: str = Field(..., description="Assistant response")
    papers_referenced: List[str] = Field(default_factory=list, description="Papers referenced in response")
    timestamp: datetime = Field(..., description="Response timestamp")

class ChatHistory(BaseModel):
    """Chat history for a session"""
    session_id: str = Field(..., description="Session identifier")
    messages: List[ChatMessage] = Field(default_factory=list, description="List of messages")
    total_messages: int = Field(default=0, description="Total number of messages")

class ChatSession(BaseModel):
    """Chat session information"""
    session_id: str = Field(..., description="Session identifier")
    user_id: str = Field(..., description="User who owns the session")
    title: Optional[str] = Field(None, description="Session title")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session creation time")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="Last activity timestamp")
    message_count: int = Field(default=0, description="Number of messages in session")
    papers_available: List[str] = Field(default_factory=list, description="Papers available for context")