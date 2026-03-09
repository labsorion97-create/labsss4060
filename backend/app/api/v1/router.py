"""
ORIONIS API v1 Router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, chat, voice, vision, image, settings, agents, system

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(chat.router)
api_router.include_router(voice.router)
api_router.include_router(vision.router)
api_router.include_router(image.router)
api_router.include_router(settings.router)
api_router.include_router(agents.router)
api_router.include_router(system.router)
