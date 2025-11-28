# app/services/storage/firestore_manager.py
import uuid
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from google.cloud.firestore import Client
from firebase_admin import firestore
from app.core.database import get_firestore_db
from app.models.search import SearchSession, SearchStatus, PaperSearchRequest
from app.models.paper import Paper, PaperAnalysis, PaperWithAnalysis
from app.models.chat import ChatMessage, MessageRole

logger = logging.getLogger(__name__)

class FirestoreSessionManager:
    """Manages research sessions in Firestore"""

    def __init__(self, db: Client = None):
        self.db = db or get_firestore_db()

    async def create_session(self, user_id: str, search_request: PaperSearchRequest) -> str:
        """Create a new research session"""
        try:
            session_id = str(uuid.uuid4())

            session_data = {
                'session_id': session_id,
                'user_id': user_id,
                'query': search_request.query,
                'sources': [source.value for source in search_request.sources],
                'max_results': search_request.max_results,
                'sort_by': search_request.sort_by.value,
                'date_range': search_request.date_range.dict() if search_request.date_range else None,
                'generate_analysis': search_request.generate_analysis,
                'status': SearchStatus.PENDING.value,
                'results_count': 0,
                'error_message': None,
                'created_at': firestore.SERVER_TIMESTAMP,
                'completed_at': None,
                'gcs_pdf_path': None
            }

            # Store in user's research_sessions subcollection
            await self._async_set_document(
                f'users/{user_id}/research_sessions/{session_id}',
                session_data
            )

            logger.info(f"Created session {session_id} for user {user_id}")
            return session_id

        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise

    async def update_session_status(
        self,
        user_id: str,
        session_id: str,
        status: SearchStatus,
        error_message: Optional[str] = None,
        results_count: Optional[int] = None,
        gcs_pdf_path: Optional[str] = None
    ):
        """Update session status"""
        try:
            update_data = {
                'status': status.value,
                'updated_at': firestore.SERVER_TIMESTAMP
            }

            if error_message is not None:
                update_data['error_message'] = error_message

            if results_count is not None:
                update_data['results_count'] = results_count

            if gcs_pdf_path is not None:
                update_data['gcs_pdf_path'] = gcs_pdf_path

            if status == SearchStatus.COMPLETED:
                update_data['completed_at'] = firestore.SERVER_TIMESTAMP

            await self._async_update_document(
                f'users/{user_id}/research_sessions/{session_id}',
                update_data
            )

            logger.info(f"Updated session {session_id} status to {status.value}")

        except Exception as e:
            logger.error(f"Error updating session status: {e}")
            raise

    async def get_session(self, user_id: str, session_id: str) -> Optional[SearchSession]:
        """Get a specific session"""
        try:
            doc = await self._async_get_document(
                f'users/{user_id}/research_sessions/{session_id}'
            )

            if not doc.exists:
                return None

            data = doc.to_dict()
            return self._doc_to_search_session(data)

        except Exception as e:
            logger.error(f"Error getting session: {e}")
            return None

    async def get_user_sessions(
        self,
        user_id: str,
        limit: int = 20,
        status_filter: Optional[SearchStatus] = None
    ) -> List[SearchSession]:
        """Get user's sessions with optional filtering"""
        try:
            query = self.db.collection('users').document(user_id).collection('research_sessions')

            if status_filter:
                query = query.where('status', '==', status_filter.value)

            query = query.order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit)

            docs = await self._async_query(query)
            sessions = []

            for doc in docs:
                try:
                    session = self._doc_to_search_session(doc.to_dict())
                    sessions.append(session)
                except Exception as e:
                    logger.warning(f"Error parsing session document: {e}")
                    continue

            return sessions

        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            return []

    async def store_papers(self, user_id: str, session_id: str, papers: List[PaperWithAnalysis]):
        """Store papers and their analyses for a session"""
        try:
            batch = self.db.batch()

            for paper_with_analysis in papers:
                paper = paper_with_analysis.paper
                analysis = paper_with_analysis.analysis

                # Store paper data
                paper_data = {
                    'id': paper.id,
                    'title': paper.title,
                    'abstract': paper.abstract,
                    'authors': paper.authors,
                    'published': paper.published,
                    'pdf_url': paper.pdf_url,
                    'source': paper.source.value,
                    'doi': paper.doi,
                    'citation_count': paper.citation_count,
                    'venue': paper.venue,
                    'keywords': paper.keywords,
                    'stored_at': firestore.SERVER_TIMESTAMP
                }

                paper_ref = self.db.collection('users').document(user_id)\
                    .collection('research_sessions').document(session_id)\
                    .collection('papers').document(paper.id)

                batch.set(paper_ref, paper_data)

                # Store analysis if available
                if analysis:
                    analysis_data = {
                        'paper_id': analysis.paper_id,
                        'summary': analysis.summary,
                        'strengths': analysis.strengths,
                        'weaknesses': analysis.weaknesses,
                        'research_gaps': analysis.research_gaps,
                        'future_scope': analysis.future_scope,
                        'key_contributions': analysis.key_contributions,
                        'methodology': analysis.methodology,
                        'main_findings': analysis.main_findings,
                        'generated_at': analysis.generated_at
                    }

                    analysis_ref = paper_ref.collection('analysis').document('ai_analysis')
                    batch.set(analysis_ref, analysis_data)

            await self._async_commit_batch(batch)
            logger.info(f"Stored {len(papers)} papers for session {session_id}")

        except Exception as e:
            logger.error(f"Error storing papers: {e}")
            raise

    async def get_session_papers(self, user_id: str, session_id: str) -> List[PaperWithAnalysis]:
        """Get papers and their analyses for a session"""
        try:
            papers_ref = self.db.collection('users').document(user_id)\
                .collection('research_sessions').document(session_id)\
                .collection('papers')

            docs = await self._async_query(papers_ref)
            papers_with_analysis = []

            for doc in docs:
                try:
                    paper_data = doc.to_dict()
                    paper = self._doc_to_paper(paper_data)

                    # Get analysis if available
                    analysis_ref = doc.reference.collection('analysis').document('ai_analysis')
                    analysis_doc = await self._async_get_document_ref(analysis_ref)

                    analysis = None
                    if analysis_doc.exists:
                        analysis_data = analysis_doc.to_dict()
                        analysis = self._doc_to_analysis(analysis_data)

                    papers_with_analysis.append(PaperWithAnalysis(
                        paper=paper,
                        analysis=analysis
                    ))

                except Exception as e:
                    logger.warning(f"Error parsing paper document: {e}")
                    continue

            return papers_with_analysis

        except Exception as e:
            logger.error(f"Error getting session papers: {e}")
            return []

    async def store_chat_message(
        self,
        user_id: str,
        session_id: str,
        role: MessageRole,
        content: str,
        papers_context: List[str] = None
    ) -> str:
        """Store a chat message"""
        try:
            message_id = str(uuid.uuid4())

            message_data = {
                'message_id': message_id,
                'session_id': session_id,
                'role': role.value,
                'content': content,
                'papers_context': papers_context or [],
                'timestamp': firestore.SERVER_TIMESTAMP,
                'metadata': {}
            }

            await self._async_set_document(
                f'users/{user_id}/research_sessions/{session_id}/chat_messages/{message_id}',
                message_data
            )

            logger.info(f"Stored chat message {message_id} for session {session_id}")
            return message_id

        except Exception as e:
            logger.error(f"Error storing chat message: {e}")
            raise

    async def get_chat_history(self, user_id: str, session_id: str, limit: int = 50) -> List[ChatMessage]:
        """Get chat history for a session"""
        try:
            query = self.db.collection('users').document(user_id)\
                .collection('research_sessions').document(session_id)\
                .collection('chat_messages')\
                .order_by('timestamp', direction=firestore.Query.ASCENDING)\
                .limit(limit)

            docs = await self._async_query(query)
            messages = []

            for doc in docs:
                try:
                    message_data = doc.to_dict()
                    message = self._doc_to_chat_message(message_data)
                    messages.append(message)
                except Exception as e:
                    logger.warning(f"Error parsing chat message: {e}")
                    continue

            return messages

        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            return []

    # Helper methods for async Firestore operations
    async def _async_set_document(self, path: str, data: Dict):
        """Async wrapper for setting document"""
        import asyncio
        loop = asyncio.get_event_loop()
        ref = self.db.document(path)
        return await loop.run_in_executor(None, ref.set, data)

    async def _async_update_document(self, path: str, data: Dict):
        """Async wrapper for updating document"""
        import asyncio
        loop = asyncio.get_event_loop()
        ref = self.db.document(path)
        return await loop.run_in_executor(None, ref.update, data)

    async def _async_get_document(self, path: str):
        """Async wrapper for getting document"""
        import asyncio
        loop = asyncio.get_event_loop()
        ref = self.db.document(path)
        return await loop.run_in_executor(None, ref.get)

    async def _async_get_document_ref(self, ref):
        """Async wrapper for getting document by reference"""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, ref.get)

    async def _async_query(self, query):
        """Async wrapper for executing query"""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, query.get)

    async def _async_commit_batch(self, batch):
        """Async wrapper for committing batch"""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, batch.commit)

    # Helper methods for data conversion
    def _doc_to_search_session(self, data: Dict) -> SearchSession:
        """Convert Firestore document to SearchSession"""
        from app.models.search import DateRange

        date_range = None
        if data.get('date_range'):
            date_range_data = data['date_range']
            date_range = DateRange(
                start=date_range_data.get('start'),
                end=date_range_data.get('end')
            )

        return SearchSession(
            session_id=data['session_id'],
            user_id=data['user_id'],
            query=data['query'],
            sources=[PaperSource(s) for s in data['sources']],
            max_results=data['max_results'],
            sort_by=SortBy(data['sort_by']),
            date_range=date_range,
            status=SearchStatus(data['status']),
            results_count=data.get('results_count', 0),
            error_message=data.get('error_message'),
            created_at=data['created_at'],
            completed_at=data.get('completed_at'),
            gcs_pdf_path=data.get('gcs_pdf_path')
        )

    def _doc_to_paper(self, data: Dict) -> Paper:
        """Convert Firestore document to Paper"""
        from app.models.paper import PaperSource

        return Paper(
            id=data['id'],
            title=data['title'],
            abstract=data['abstract'],
            authors=data['authors'],
            published=data['published'],
            pdf_url=data.get('pdf_url'),
            source=PaperSource(data['source']),
            doi=data.get('doi'),
            citation_count=data.get('citation_count'),
            venue=data.get('venue'),
            keywords=data.get('keywords', [])
        )

    def _doc_to_analysis(self, data: Dict) -> PaperAnalysis:
        """Convert Firestore document to PaperAnalysis"""
        return PaperAnalysis(
            paper_id=data['paper_id'],
            summary=data['summary'],
            strengths=data.get('strengths', []),
            weaknesses=data.get('weaknesses', []),
            research_gaps=data.get('research_gaps', []),
            future_scope=data.get('future_scope', []),
            key_contributions=data.get('key_contributions', []),
            methodology=data.get('methodology', ''),
            main_findings=data.get('main_findings', []),
            generated_at=data['generated_at']
        )

    def _doc_to_chat_message(self, data: Dict) -> ChatMessage:
        """Convert Firestore document to ChatMessage"""
        return ChatMessage(
            message_id=data['message_id'],
            session_id=data['session_id'],
            role=MessageRole(data['role']),
            content=data['content'],
            papers_context=data.get('papers_context', []),
            timestamp=data['timestamp'],
            metadata=data.get('metadata', {})
        )