"""
ORIONIS API v1 - Agent Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.security import get_current_token
from app.services.auth_service import AuthService
from app.services.agent_service import AgentService
from app.schemas.schemas import AgentResponse, AgentRunRequest, AgentRunResponse

router = APIRouter(prefix="/agents", tags=["Agents"])


async def get_user_context(token: str, db: AsyncSession):
    """Helper to get user and tenant from token"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    return user.id, user.current_tenant.id if user.current_tenant else None


@router.get("", response_model=List[AgentResponse])
async def get_agents(
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Get all agents"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = AgentService(db)
    return await service.get_all_agents()


@router.get("/status")
async def get_agents_status(
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Get status of all agents"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = AgentService(db)
    return await service.get_agents_status()


@router.get("/{agent_name}", response_model=AgentResponse)
async def get_agent(
    agent_name: str,
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific agent"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = AgentService(db)
    agent = await service.get_agent(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent


@router.post("/run", response_model=AgentRunResponse)
async def run_agent(
    data: AgentRunRequest,
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Execute an agent task"""
    user_id, tenant_id = await get_user_context(token, db)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="No tenant context")
    
    service = AgentService(db)
    return await service.run_agent(data.agent_name, tenant_id, user_id, data.input_data)
