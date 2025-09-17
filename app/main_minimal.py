# app/main_minimal.py - Minimal FastAPI app for testing without dependencies
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Starting up Research Paper API (Minimal)...")
    yield
    logger.info("Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Research Paper Analysis API (Minimal)",
    description="API for searching, analyzing, and querying research papers",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Research Paper API is running (minimal)", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/test/config")
async def test_config():
    return {
        "project_id": settings.project_id,
        "environment": settings.environment,
        "api_prefix": settings.api_v1_prefix
    }

# Run with: uvicorn app.main_minimal:app --reload