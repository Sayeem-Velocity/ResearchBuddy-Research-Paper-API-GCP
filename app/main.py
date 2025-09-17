# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
    logger.info("Starting up Research Paper API...")
    # Initialize connections here
    yield
    # Cleanup
    logger.info("Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Research Paper Analysis API",
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

# Include API routes
from app.api.v1.router import api_router
app.include_router(api_router, prefix=settings.api_v1_prefix)

@app.get("/")
async def root():
    return {"message": "Research Paper API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Run with: uvicorn app.main:app --reload