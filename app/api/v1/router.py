# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints import search

api_router = APIRouter()

api_router.include_router(
    search.router,
    prefix="/papers",
    tags=["papers"]
)