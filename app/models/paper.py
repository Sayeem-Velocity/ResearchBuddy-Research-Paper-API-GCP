# app/models/paper.py
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class PaperSource(str, Enum):
    """Supported paper sources"""
    ARXIV = "arxiv"
    GOOGLE_SCHOLAR = "google_scholar"
    PUBMED = "pubmed"
    IEEE = "ieee"

class SortBy(str, Enum):
    """Sorting options for papers"""
    RELEVANCE = "relevance"
    RECENT = "recent"
    CITED = "cited"

class Paper(BaseModel):
    """Core paper model"""
    id: str = Field(..., description="Unique paper identifier")
    title: str = Field(..., description="Paper title")
    abstract: str = Field(..., description="Paper abstract/summary")
    authors: List[str] = Field(default_factory=list, description="List of authors")
    published: str = Field(..., description="Publication date (ISO format)")
    pdf_url: Optional[str] = Field(None, description="URL to PDF")
    source: PaperSource = Field(..., description="Source of the paper")
    doi: Optional[str] = Field(None, description="Digital Object Identifier")
    citation_count: Optional[int] = Field(None, description="Number of citations")
    venue: Optional[str] = Field(None, description="Publication venue")
    keywords: List[str] = Field(default_factory=list, description="Paper keywords")

    class Config:
        use_enum_values = True

class PaperAnalysis(BaseModel):
    """AI-generated paper analysis"""
    paper_id: str = Field(..., description="Reference to paper")
    summary: str = Field(..., description="AI-generated summary")
    strengths: List[str] = Field(default_factory=list, description="Paper strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Paper weaknesses")
    research_gaps: List[str] = Field(default_factory=list, description="Identified research gaps")
    future_scope: List[str] = Field(default_factory=list, description="Future research directions")
    key_contributions: List[str] = Field(default_factory=list, description="Key contributions")
    methodology: str = Field("", description="Methodology overview")
    main_findings: List[str] = Field(default_factory=list, description="Main findings")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")

class PaperWithAnalysis(BaseModel):
    """Paper with complete analysis"""
    paper: Paper
    analysis: Optional[PaperAnalysis] = None