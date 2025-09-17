# app/core/database.py
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore import Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class FirebaseConnection:
    """Firebase connection manager"""

    _db: Client = None
    _app = None

    @classmethod
    def initialize(cls):
        """Initialize Firebase connection"""
        if cls._app is None:
            try:
                # Initialize Firebase Admin SDK
                cred = credentials.Certificate(settings.google_application_credentials)
                cls._app = firebase_admin.initialize_app(cred, {
                    'projectId': settings.project_id
                })
                logger.info(f"Firebase initialized for project: {settings.project_id}")

                # Initialize Firestore client
                cls._db = firestore.client()
                logger.info("Firestore client initialized")

            except Exception as e:
                logger.error(f"Failed to initialize Firebase: {e}")
                raise

    @classmethod
    def get_db(cls) -> Client:
        """Get Firestore database client"""
        if cls._db is None:
            cls.initialize()
        return cls._db

    @classmethod
    def close(cls):
        """Close Firebase connection"""
        if cls._app:
            firebase_admin.delete_app(cls._app)
            cls._app = None
            cls._db = None
            logger.info("Firebase connection closed")

# Global database instance
def get_firestore_db() -> Client:
    """Dependency function to get Firestore database"""
    return FirebaseConnection.get_db()

# Initialize on import
try:
    FirebaseConnection.initialize()
except Exception as e:
    logger.warning(f"Failed to initialize Firebase on import: {e}")