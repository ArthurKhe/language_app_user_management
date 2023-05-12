from fastapi import APIRouter

from api.v1.endpoints import users, category, channel

api_router = APIRouter()

api_router.include_router(users.router, prefix="", tags=["users"])
api_router.include_router(category.router, prefix="", tags=["categories"])
api_router.include_router(channel.router, prefix="", tags=["channels"])
