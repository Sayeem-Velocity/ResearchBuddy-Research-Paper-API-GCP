# app/core/mock_dependencies.py
from fastapi import HTTPException, status
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class MockAuthenticationError(HTTPException):
    """Mock authentication error"""
    def __init__(self, detail: str = "Mock authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_mock_current_user(authorization: str = None) -> str:
    """
    Mock dependency to get current authenticated user
    Returns a test user ID for development
    """
    # For testing, we'll accept any authorization header or return a default user
    if authorization and authorization.startswith('Bearer '):
        # Extract a simple user ID from the token for testing
        token = authorization.split(' ')[1]
        if token == 'test-token':
            return 'test-user-123'
        elif token == 'demo-token':
            return 'demo-user-456'
        else:
            # For any other token, return a generic test user
            return f'user-{hash(token) % 1000}'

    # If no authorization header, return default test user
    return 'default-test-user'

async def get_mock_current_user_optional(authorization: str = None) -> Optional[str]:
    """
    Mock optional authentication dependency
    """
    try:
        return await get_mock_current_user(authorization)
    except HTTPException:
        return None

async def get_mock_user_profile(current_user: str = None) -> Dict[str, Any]:
    """
    Mock user profile data
    """
    if not current_user:
        current_user = await get_mock_current_user()

    return {
        'user_id': current_user,
        'research_profile': {
            'subscription_tier': 'premium',  # Give premium for testing
            'api_usage': {
                'searches_this_month': 5,
                'papers_analyzed': 25,
                'last_reset': '2024-01-01T00:00:00Z'
            }
        },
        'preferences': {
            'default_sources': ['arxiv', 'pubmed'],
            'max_results_per_search': 20
        }
    }

async def check_mock_api_quota(current_user: str = None) -> bool:
    """
    Mock API quota check - always returns True for testing
    """
    if not current_user:
        current_user = await get_mock_current_user()

    logger.info(f"Mock quota check for user {current_user} - PASSED")
    return True

async def increment_mock_api_usage(
    current_user: str,
    db=None,
    searches: int = 1,
    papers: int = 0
):
    """
    Mock API usage increment - just logs for testing
    """
    logger.info(f"Mock usage increment for user {current_user}: +{searches} searches, +{papers} papers")

def get_mock_firestore_db():
    """
    Mock Firestore database - returns None as our mock services don't need it
    """
    return None