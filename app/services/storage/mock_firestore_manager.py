# app/services/storage/mock_firestore_manager.py
import uuid
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import json
import os
from app.models.search import SearchSession, SearchStatus, PaperSearchRequest
from app.models.paper import Paper, PaperAnalysis, PaperWithAnalysis, PaperSource, SortBy
from app.models.chat import ChatMessage, MessageRole

logger = logging.getLogger(__name__)

class MockFirestoreSessionManager:
    """Mock Firestore session manager using local JSON files"""

    def __init__(self, db=None):
        self.data_dir = ".mock_firestore_data"
        self.sessions_file = os.path.join(self.data_dir, "sessions.json")
        self.papers_file = os.path.join(self.data_dir, "papers.json")
        self.chat_file = os.path.join(self.data_dir, "chat_messages.json")

        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)

        # Initialize empty files if they don't exist
        for file_path in [self.sessions_file, self.papers_file, self.chat_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump({}, f)

        logger.info("Mock Firestore session manager initialized")

    def _load_json(self, file_path: str) -> Dict:
        """Load JSON data from file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading {file_path}: {e}")
            return {}

    def _save_json(self, file_path: str, data: Dict):
        """Save JSON data to file with comprehensive serialization"""
        try:
            def safe_serialize(obj):
                """Recursively convert any object to JSON-serializable format"""
                if obj is None:
                    return None
                elif hasattr(obj, 'value'):  # Enum
                    return obj.value
                elif hasattr(obj, 'isoformat'):  # datetime
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    return {str(k): safe_serialize(v) for k, v in obj.items()}
                elif isinstance(obj, (list, tuple)):
                    return [safe_serialize(item) for item in obj]
                elif isinstance(obj, (str, int, float, bool)):
                    return obj
                else:
                    return str(obj)

            serialized_data = safe_serialize(data)
            with open(file_path, 'w') as f:
                json.dump(serialized_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving {file_path}: {e}")
            raise

    async def create_session(self, user_id: str, search_request: PaperSearchRequest) -> str:
        """Create a new research session"""
        try:
            session_id = str(uuid.uuid4())

            # Convert enum sources to strings
            sources_list = []
            for source in search_request.sources:
                if hasattr(source, 'value'):
                    sources_list.append(source.value)
                else:
                    sources_list.append(str(source))

            session_data = {
                'session_id': session_id,
                'user_id': user_id,
                'query': search_request.query,
                'sources': sources_list,
                'max_results': search_request.max_results,
                'sort_by': search_request.sort_by.value if hasattr(search_request.sort_by, 'value') else str(search_request.sort_by),
                'date_range': search_request.date_range.dict() if search_request.date_range else None,
                'generate_analysis': search_request.generate_analysis,
                'status': 'pending',  # Use string directly
                'results_count': 0,
                'error_message': None,
                'created_at': datetime.utcnow().isoformat(),
                'completed_at': None,
                'gcs_pdf_path': None
            }

            # Load existing sessions
            sessions_data = self._load_json(self.sessions_file)

            # Store session
            if user_id not in sessions_data:
                sessions_data[user_id] = {}
            sessions_data[user_id][session_id] = session_data

            # Save to file
            self._save_json(self.sessions_file, sessions_data)

            logger.info(f"Created mock session {session_id} for user {user_id}")
            return session_id

        except Exception as e:
            logger.error(f"Error creating mock session: {e}")
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
            sessions_data = self._load_json(self.sessions_file)

            if user_id in sessions_data and session_id in sessions_data[user_id]:
                session = sessions_data[user_id][session_id]
                # Convert status enum to string
                if hasattr(status, 'value'):
                    session['status'] = status.value
                else:
                    session['status'] = str(status)
                session['updated_at'] = datetime.utcnow().isoformat()

                if error_message is not None:
                    session['error_message'] = error_message
                if results_count is not None:
                    session['results_count'] = results_count
                if gcs_pdf_path is not None:
                    session['gcs_pdf_path'] = gcs_pdf_path
                if status == SearchStatus.COMPLETED:
                    session['completed_at'] = datetime.utcnow().isoformat()

                self._save_json(self.sessions_file, sessions_data)
                logger.info(f"Updated mock session {session_id} status to {status.value}")

        except Exception as e:
            logger.error(f"Error updating mock session status: {e}")
            raise

    async def get_session(self, user_id: str, session_id: str) -> Optional[SearchSession]:
        """Get a specific session"""
        try:
            sessions_data = self._load_json(self.sessions_file)

            if user_id not in sessions_data or session_id not in sessions_data[user_id]:
                return None

            session_data = sessions_data[user_id][session_id]
            return self._dict_to_search_session(session_data)

        except Exception as e:
            logger.error(f"Error getting mock session: {e}")
            return None

    async def get_user_sessions(
        self,
        user_id: str,
        limit: int = 20,
        status_filter: Optional[SearchStatus] = None
    ) -> List[SearchSession]:
        """Get user's sessions with optional filtering"""
        try:
            sessions_data = self._load_json(self.sessions_file)

            if user_id not in sessions_data:
                return []

            user_sessions = sessions_data[user_id]
            sessions = []

            for session_data in user_sessions.values():
                try:
                    if status_filter and session_data.get('status') != status_filter.value:
                        continue

                    session = self._dict_to_search_session(session_data)
                    sessions.append(session)
                except Exception as e:
                    logger.warning(f"Error parsing mock session: {e}")
                    continue

            # Sort by created_at descending and limit
            sessions.sort(key=lambda x: x.created_at, reverse=True)
            return sessions[:limit]

        except Exception as e:
            logger.error(f"Error getting mock user sessions: {e}")
            return []

    async def store_papers(self, user_id: str, session_id: str, papers: List[PaperWithAnalysis]):
        """Store papers and their analyses for a session"""
        try:
            papers_data = self._load_json(self.papers_file)

            session_key = f"{user_id}_{session_id}"
            papers_data[session_key] = []

            for paper_with_analysis in papers:
                paper = paper_with_analysis.paper
                analysis = paper_with_analysis.analysis

                # Safely convert all fields to JSON-serializable types
                def safe_convert(value):
                    """Convert enum or any object to string safely"""
                    if hasattr(value, 'value'):  # Enum with .value
                        return value.value
                    elif value is None:
                        return None
                    else:
                        return str(value)

                paper_entry = {
                    'paper': {
                        'id': str(paper.id),
                        'title': str(paper.title),
                        'abstract': str(paper.abstract),
                        'authors': [str(author) for author in paper.authors],
                        'published': str(paper.published),
                        'pdf_url': str(paper.pdf_url) if paper.pdf_url else None,
                        'source': safe_convert(paper.source),
                        'doi': str(paper.doi) if paper.doi else None,
                        'citation_count': paper.citation_count,
                        'venue': str(paper.venue) if paper.venue else None,
                        'keywords': [str(kw) for kw in paper.keywords] if paper.keywords else []
                    },
                    'analysis': {
                        'paper_id': str(analysis.paper_id),
                        'summary': str(analysis.summary),
                        'strengths': [str(s) for s in analysis.strengths],
                        'weaknesses': [str(w) for w in analysis.weaknesses],
                        'research_gaps': [str(g) for g in analysis.research_gaps],
                        'future_scope': [str(f) for f in analysis.future_scope],
                        'key_contributions': [str(k) for k in analysis.key_contributions],
                        'methodology': str(analysis.methodology),
                        'main_findings': [str(m) for m in analysis.main_findings],
                        'generated_at': analysis.generated_at.isoformat()
                    } if analysis else None,
                    'stored_at': datetime.utcnow().isoformat()
                }

                papers_data[session_key].append(paper_entry)

            self._save_json(self.papers_file, papers_data)
            logger.info(f"Stored {len(papers)} papers for mock session {session_id}")

        except Exception as e:
            logger.error(f"Error storing mock papers: {e}")
            raise

    async def get_session_papers(self, user_id: str, session_id: str) -> List[PaperWithAnalysis]:
        """Get papers and their analyses for a session"""
        try:
            papers_data = self._load_json(self.papers_file)
            session_key = f"{user_id}_{session_id}"

            if session_key not in papers_data:
                return []

            papers_with_analysis = []

            for paper_entry in papers_data[session_key]:
                try:
                    paper_data = paper_entry['paper']
                    analysis_data = paper_entry.get('analysis')

                    # Convert paper data
                    paper = Paper(
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

                    # Convert analysis data if available
                    analysis = None
                    if analysis_data:
                        analysis = PaperAnalysis(
                            paper_id=analysis_data['paper_id'],
                            summary=analysis_data['summary'],
                            strengths=analysis_data.get('strengths', []),
                            weaknesses=analysis_data.get('weaknesses', []),
                            research_gaps=analysis_data.get('research_gaps', []),
                            future_scope=analysis_data.get('future_scope', []),
                            key_contributions=analysis_data.get('key_contributions', []),
                            methodology=analysis_data.get('methodology', ''),
                            main_findings=analysis_data.get('main_findings', []),
                            generated_at=datetime.fromisoformat(analysis_data['generated_at'])
                        )

                    papers_with_analysis.append(PaperWithAnalysis(
                        paper=paper,
                        analysis=analysis
                    ))

                except Exception as e:
                    logger.warning(f"Error parsing mock paper entry: {e}")
                    continue

            return papers_with_analysis

        except Exception as e:
            logger.error(f"Error getting mock session papers: {e}")
            return []

    def _dict_to_search_session(self, data: Dict) -> SearchSession:
        """Convert dictionary to SearchSession"""
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
            created_at=datetime.fromisoformat(data['created_at']),
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            gcs_pdf_path=data.get('gcs_pdf_path')
        )