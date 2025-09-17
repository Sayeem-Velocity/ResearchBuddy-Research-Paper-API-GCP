# app/models/user.py
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SubscriptionTier(str, Enum):
    """User subscription tiers"""
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class ApiUsage(BaseModel):
    """API usage tracking"""
    searches_this_month: int = Field(default=0, description="Number of searches this month")
    papers_analyzed: int = Field(default=0, description="Number of papers analyzed")
    last_reset: datetime = Field(default_factory=datetime.utcnow, description="Last usage reset date")
    total_searches: int = Field(default=0, description="Total searches all time")
    total_papers: int = Field(default=0, description="Total papers analyzed all time")

class ResearchProfile(BaseModel):
    """User's research profile"""
    subscription_tier: SubscriptionTier = Field(default=SubscriptionTier.FREE, description="Subscription level")
    api_usage: ApiUsage = Field(default_factory=ApiUsage, description="API usage statistics")
    research_interests: List[str] = Field(default_factory=list, description="Research areas of interest")
    preferred_sources: List[str] = Field(default_factory=list, description="Preferred paper sources")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Profile creation date")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        use_enum_values = True

class UserProfile(BaseModel):
    """Complete user profile"""
    user_id: str = Field(..., description="Unique user identifier")
    email: Optional[EmailStr] = Field(None, description="User email")
    display_name: Optional[str] = Field(None, description="Display name")
    research_profile: ResearchProfile = Field(default_factory=ResearchProfile, description="Research-specific profile")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Account creation date")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    is_active: bool = Field(default=True, description="Whether account is active")

class UserUsageStats(BaseModel):
    """User usage statistics"""
    user_id: str = Field(..., description="User identifier")
    current_month: ApiUsage = Field(..., description="Current month usage")
    quota_limits: Dict[str, int] = Field(..., description="Quota limits for user tier")
    quota_remaining: Dict[str, int] = Field(..., description="Remaining quota")
    next_reset: datetime = Field(..., description="Next quota reset date")

class UserSessionSummary(BaseModel):
    """Summary of user's research sessions"""
    user_id: str = Field(..., description="User identifier")
    total_sessions: int = Field(default=0, description="Total number of sessions")
    active_sessions: int = Field(default=0, description="Currently active sessions")
    recent_sessions: List[Dict[str, Any]] = Field(default_factory=list, description="Recent session summaries")
    total_papers_found: int = Field(default=0, description="Total papers found across all sessions")
    favorite_sources: List[str] = Field(default_factory=list, description="Most used sources")