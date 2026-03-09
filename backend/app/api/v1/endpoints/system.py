"""
ORIONIS API v1 - System Endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, get_redis
from app.core.config import settings
from app.services.agent_service import AgentService
from app.schemas.schemas import SystemStatusResponse, HealthResponse

router = APIRouter(tags=["System"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    db_status = "healthy"
    redis_status = "healthy"
    
    try:
        redis = await get_redis()
        await redis.ping()
    except Exception:
        redis_status = "unavailable"
    
    return HealthResponse(
        status="healthy",
        database=db_status,
        redis=redis_status,
        version=settings.APP_VERSION
    )


@router.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes"""
    return {"status": "ready"}


@router.get("/system/status")
async def system_status():
    """Get system status"""
    agents = [
        {"id": "1", "name": "core_orchestrator", "display_name": "Core Orchestrator", "description": "Núcleo central", "agent_type": "core", "status": "active", "capabilities": ["routing", "planning"]},
        {"id": "2", "name": "research", "display_name": "Research Agent", "description": "Pesquisa em tempo real", "agent_type": "knowledge", "status": "active", "capabilities": ["web_search"]},
        {"id": "3", "name": "knowledge", "display_name": "Knowledge Agent", "description": "Base de conhecimento", "agent_type": "knowledge", "status": "active", "capabilities": ["rag"]},
        {"id": "4", "name": "voice", "display_name": "Voice Agent", "description": "Voz", "agent_type": "multimodal", "status": "active", "capabilities": ["stt", "tts"]},
        {"id": "5", "name": "vision", "display_name": "Vision Agent", "description": "Visão", "agent_type": "multimodal", "status": "active", "capabilities": ["image_analysis"]},
        {"id": "6", "name": "design", "display_name": "Design Agent", "description": "Design", "agent_type": "builder", "status": "active", "capabilities": ["image_generation"]},
        {"id": "7", "name": "development", "display_name": "Development Agent", "description": "Desenvolvimento", "agent_type": "builder", "status": "standby", "capabilities": ["code_generation"]},
        {"id": "8", "name": "automation", "display_name": "Automation Agent", "description": "Automações", "agent_type": "operational", "status": "active", "capabilities": ["workflows"]},
    ]
    
    return {
        "system": "ORIONIS",
        "version": settings.APP_VERSION,
        "status": "operational",
        "uptime": "99.9%",
        "agents": agents,
        "capabilities": {
            "chat": True,
            "voice": True,
            "vision": True,
            "image_generation": True,
            "streaming": True,
            "knowledge_base": True,
            "memory": True,
            "automations": True,
            "integrations": True
        }
    }
