# app/api/v1/endpoints/search.py
import asyncio
import logging
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional
from google.cloud.firestore import firestore
from app.core.dependencies import get_current_user, check_api_quota, increment_api_usage
from app.core.database import get_firestore_db
from app.models.search import (
    PaperSearchRequest, SearchResponse, SearchStatusResponse,
    SearchResults, SearchStatus
)
from app.models.paper import PaperWithAnalysis
from app.services.paper_search.aggregator import PaperSearchAggregator
from app.services.llm.vertex_ai import VertexAIService
from app.services.storage.firestore_manager import FirestoreSessionManager
from google.cloud.firestore import Client

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
search_aggregator = PaperSearchAggregator()
vertex_ai_service = VertexAIService()

@router.post("/search", response_model=SearchResponse)
async def search_papers(
    search_request: PaperSearchRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user),
    _: bool = Depends(check_api_quota),
    db: Client = Depends(get_firestore_db)
):
    """
    Start a new paper search across multiple sources
    """
    try:
        session_manager = FirestoreSessionManager(db)

        # Create new session
        session_id = await session_manager.create_session(current_user, search_request)

        # Start background search task
        background_tasks.add_task(
            process_search_task,
            session_id=session_id,
            user_id=current_user,
            search_request=search_request,
            db=db
        )

        # Increment API usage
        await increment_api_usage(current_user, db, searches=1)

        logger.info(f"Started search session {session_id} for user {current_user}")

        return SearchResponse(
            session_id=session_id,
            status=SearchStatus.PROCESSING,
            message="Search started successfully. Check status for progress."
        )

    except Exception as e:
        logger.error(f"Error starting search: {e}")
        raise HTTPException(status_code=500, detail="Failed to start search")

@router.get("/search/status/{session_id}", response_model=SearchStatusResponse)
async def get_search_status(
    session_id: str,
    current_user: str = Depends(get_current_user),
    db: Client = Depends(get_firestore_db)
):
    """
    Get the status of a search session
    """
    try:
        session_manager = FirestoreSessionManager(db)
        session = await session_manager.get_session(current_user, session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return SearchStatusResponse(
            session_id=session.session_id,
            status=session.status,
            results_count=session.results_count,
            error_message=session.error_message,
            created_at=session.created_at,
            completed_at=session.completed_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting search status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get search status")

@router.get("/search/results/{session_id}", response_model=SearchResults)
async def get_search_results(
    session_id: str,
    current_user: str = Depends(get_current_user),
    db: Client = Depends(get_firestore_db)
):
    """
    Get the results of a completed search session
    """
    try:
        session_manager = FirestoreSessionManager(db)

        # Get session info
        session = await session_manager.get_session(current_user, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get papers with analysis
        papers_with_analysis = await session_manager.get_session_papers(current_user, session_id)

        return SearchResults(
            session=session,
            papers=papers_with_analysis
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting search results: {e}")
        raise HTTPException(status_code=500, detail="Failed to get search results")

@router.get("/sessions", response_model=List[SearchStatusResponse])
async def get_user_sessions(
    limit: int = 20,
    status_filter: Optional[SearchStatus] = None,
    current_user: str = Depends(get_current_user),
    db: Client = Depends(get_firestore_db)
):
    """
    Get user's search sessions
    """
    try:
        session_manager = FirestoreSessionManager(db)
        sessions = await session_manager.get_user_sessions(
            current_user,
            limit=limit,
            status_filter=status_filter
        )

        return [
            SearchStatusResponse(
                session_id=session.session_id,
                status=session.status,
                results_count=session.results_count,
                error_message=session.error_message,
                created_at=session.created_at,
                completed_at=session.completed_at
            )
            for session in sessions
        ]

    except Exception as e:
        logger.error(f"Error getting user sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user sessions")

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: str = Depends(get_current_user),
    db: Client = Depends(get_firestore_db)
):
    """
    Delete a search session and its data
    """
    try:
        session_manager = FirestoreSessionManager(db)

        # Verify session exists and belongs to user
        session = await session_manager.get_session(current_user, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Delete session (this will delete the entire subcollection tree)
        await session_manager._async_set_document(
            f'users/{current_user}/research_sessions/{session_id}',
            {"deleted": True, "deleted_at": firestore.SERVER_TIMESTAMP}
        )

        logger.info(f"Deleted session {session_id} for user {current_user}")
        return {"message": "Session deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete session")

# Background task functions
async def process_search_task(
    session_id: str,
    user_id: str,
    search_request: PaperSearchRequest,
    db: Client
):
    """
    Background task to process the search request
    """
    session_manager = FirestoreSessionManager(db)

    try:
        logger.info(f"Processing search task for session {session_id}")

        # Update status to processing
        await session_manager.update_session_status(
            user_id, session_id, SearchStatus.PROCESSING
        )

        # Perform the search
        papers = await search_aggregator.search_all_sources(
            query=search_request.query,
            sources=search_request.sources,
            max_results=search_request.max_results,
            date_range=search_request.date_range.dict() if search_request.date_range else None,
            sort_by=search_request.sort_by
        )

        if not papers:
            await session_manager.update_session_status(
                user_id, session_id, SearchStatus.COMPLETED,
                error_message="No papers found for the given query"
            )
            return

        logger.info(f"Found {len(papers)} papers for session {session_id}")

        # Generate analysis if requested
        papers_with_analysis = []
        if search_request.generate_analysis:
            logger.info(f"Generating analysis for {len(papers)} papers")
            analyses = await vertex_ai_service.analyze_papers_batch(papers)

            # Match papers with their analyses
            analysis_map = {analysis.paper_id: analysis for analysis in analyses}

            for paper in papers:
                analysis = analysis_map.get(paper.id)
                papers_with_analysis.append(PaperWithAnalysis(
                    paper=paper,
                    analysis=analysis
                ))
        else:
            papers_with_analysis = [
                PaperWithAnalysis(paper=paper, analysis=None)
                for paper in papers
            ]

        # Store papers and analyses
        await session_manager.store_papers(user_id, session_id, papers_with_analysis)

        # Update session as completed
        await session_manager.update_session_status(
            user_id, session_id, SearchStatus.COMPLETED,
            results_count=len(papers)
        )

        # Update API usage for papers analyzed
        if search_request.generate_analysis:
            await increment_api_usage(user_id, db, searches=0, papers=len(papers))

        logger.info(f"Completed search task for session {session_id}")

    except Exception as e:
        logger.error(f"Error in search task for session {session_id}: {e}")

        # Update session as failed
        await session_manager.update_session_status(
            user_id, session_id, SearchStatus.FAILED,
            error_message=str(e)
        )