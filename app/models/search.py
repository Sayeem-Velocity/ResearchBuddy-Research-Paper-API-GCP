# app/models/search.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum
from app.models.paper import PaperSource, SortBy, PaperWithAnalysis

class SearchStatus(str, Enum):
    """Search session status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DateRange(BaseModel):
    """Date range for filtering papers"""
    start: Optional[date] = Field(None, description="Start date (YYYY-MM-DD)")
    end: Optional[date] = Field(None, description="End date (YYYY-MM-DD)")

    @validator('end')
    def end_after_start(cls, v, values):
        if v and values.get('start') and v < values['start']:
            raise ValueError('End date must be after start date')
        return v

class PaperSearchRequest(BaseModel):
    """Request model for paper search"""
    query: str = Field(..., min_length=3, max_length=500, description="Search query")
    sources: List[PaperSource] = Field(
        default=[PaperSource.ARXIV, PaperSource.GOOGLE_SCHOLAR],
        description="Sources to search"
    )
    max_results: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of results"
    )
    sort_by: SortBy = Field(default=SortBy.RELEVANCE, description="Sort order")
    date_range: Optional[DateRange] = Field(None, description="Publication date range")
    generate_analysis: bool = Field(default=True, description="Whether to generate AI analysis")

    @validator('sources')
    def sources_not_empty(cls, v):
        if not v:
            raise ValueError('At least one source must be specified')
        return v

class SearchSession(BaseModel):
    """Search session model"""
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User who created the session")
    query: str = Field(..., description="Search query")
    sources: List[PaperSource] = Field(..., description="Sources searched")
    max_results: int = Field(..., description="Maximum results requested")
    sort_by: SortBy = Field(..., description="Sort order")
    date_range: Optional[DateRange] = Field(None, description="Date range filter")
    status: SearchStatus = Field(default=SearchStatus.PENDING, description="Current status")
    results_count: int = Field(default=0, description="Number of results found")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    gcs_pdf_path: Optional[str] = Field(None, description="Path to generated PDF in GCS")

    class Config:
        use_enum_values = True

class SearchResponse(BaseModel):
    """Response model for paper search"""
    session_id: str = Field(..., description="Session identifier")
    status: SearchStatus = Field(..., description="Current status")
    message: str = Field(..., description="Status message")

class SearchResults(BaseModel):
    """Complete search results"""
    session: SearchSession
    papers: List[PaperWithAnalysis] = Field(default_factory=list, description="Found papers with analysis")

class SearchStatusResponse(BaseModel):
    """Response for search status check"""
    session_id: str = Field(..., description="Session identifier")
    status: SearchStatus = Field(..., description="Current status")
    query: str = Field(..., description="Search query")
    sources: List[PaperSource] = Field(..., description="Sources being searched")
    progress: Optional[Dict[str, Any]] = Field(None, description="Progress information")
    results_count: int = Field(default=0, description="Number of results found")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")