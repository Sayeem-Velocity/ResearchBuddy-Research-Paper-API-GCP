# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints import search_mock, chat

api_router = APIRouter()

api_router.include_router(
    search_mock.router,
    prefix="/papers",
    tags=["papers"]
)

api_router.include_router(
    chat.router,
    prefix="/papers",
    tags=["chat"]
)