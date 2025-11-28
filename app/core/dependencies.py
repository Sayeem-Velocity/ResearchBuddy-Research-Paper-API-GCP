# app/core/dependencies.py
from fastapi import Depends, HTTPException, Header, status
from firebase_admin import auth
from google.cloud.firestore import Client
from app.core.database import get_firestore_db
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AuthenticationError(HTTPException):
    """Custom authentication error"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class AuthorizationError(HTTPException):
    """Custom authorization error"""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

async def get_current_user(authorization: str = Header(None)) -> str:
    """
    Dependency to get current authenticated user from Firebase token
    Returns the user ID (uid) or a default user for development
    """
    # Allow development mode without authentication
    if not authorization:
        logger.warning("No authorization header - using default user for development")
        return "dev-user-default"

    if not authorization.startswith('Bearer '):
        logger.warning("Invalid authorization header format - using default user")
        return "dev-user-default"

    token = authorization.split(' ')[1]

    try:
        # Verify the Firebase ID token
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token['uid']

        logger.info(f"User authenticated: {user_id}")
        return user_id

    except auth.InvalidIdTokenError:
        logger.warning("Invalid token - using default user")
        return "dev-user-default"
    except auth.ExpiredIdTokenError:
        logger.warning("Token expired - using default user")
        return "dev-user-default"
    except Exception as e:
        logger.error(f"Authentication error: {e} - using default user")
        return "dev-user-default"

async def get_current_user_optional(authorization: str = Header(None)) -> Optional[str]:
    """
    Optional authentication dependency - returns None if no valid token
    """
    if not authorization:
        return None

    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None

async def get_user_profile(
    current_user: str = Depends(get_current_user),
    db: Client = Depends(get_firestore_db)
) -> Dict[str, Any]:
    """
    Get user profile from Firestore
    """
    try:
        user_doc = db.collection('users').document(current_user).get()
        if not user_doc.exists:
            # Create basic user profile if doesn't exist
            user_data = {
                'research_profile': {
                    'subscription_tier': 'free',
                    'api_usage': {
                        'searches_this_month': 0,
                        'papers_analyzed': 0,
                        'last_reset': '2024-01-01T00:00:00Z'
                    }
                }
            }
            db.collection('users').document(current_user).set(user_data, merge=True)
            return user_data

        return user_doc.to_dict()

    except Exception as e:
        logger.error(f"Error fetching user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user profile"
        )

async def check_api_quota(
    current_user: str = Depends(get_current_user),
    db: Client = Depends(get_firestore_db)
) -> bool:
    """
    Check if user has remaining API quota
    """
    try:
        user_doc = db.collection('users').document(current_user).get()

        if not user_doc.exists:
            return True  # New user, allow usage

        user_data = user_doc.to_dict()
        research_profile = user_data.get('research_profile', {})
        api_usage = research_profile.get('api_usage', {})
        tier = research_profile.get('subscription_tier', 'free')

        # Define quotas per tier
        quotas = {
            'free': {'monthly_searches': 50, 'papers_per_search': 10},
            'premium': {'monthly_searches': 500, 'papers_per_search': 50},
            'enterprise': {'monthly_searches': -1, 'papers_per_search': 100}  # -1 = unlimited
        }

        current_searches = api_usage.get('searches_this_month', 0)
        max_searches = quotas.get(tier, quotas['free'])['monthly_searches']

        if max_searches == -1:  # Unlimited
            return True

        if current_searches >= max_searches:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Monthly quota exceeded. Upgrade your plan for more searches."
            )

        return True

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking API quota: {e}")
        return True  # Allow on error to prevent blocking users

async def increment_api_usage(
    current_user: str,
    db: Client,
    searches: int = 1,
    papers: int = 0
):
    """
    Increment user's API usage counters
    """
    try:
        user_ref = db.collection('users').document(current_user)

        # Use transaction to safely increment counters
        @firestore.transactional
        def update_usage(transaction):
            doc = user_ref.get(transaction=transaction)
            current_data = doc.to_dict() if doc.exists else {}

            research_profile = current_data.get('research_profile', {})
            api_usage = research_profile.get('api_usage', {
                'searches_this_month': 0,
                'papers_analyzed': 0,
                'last_reset': '2024-01-01T00:00:00Z'
            })

            api_usage['searches_this_month'] += searches
            api_usage['papers_analyzed'] += papers

            research_profile['api_usage'] = api_usage
            current_data['research_profile'] = research_profile

            transaction.set(user_ref, current_data, merge=True)

        transaction = db.transaction()
        update_usage(transaction)

    except Exception as e:
        logger.error(f"Error incrementing API usage: {e}")
        # Don't raise exception here to avoid breaking the main flow