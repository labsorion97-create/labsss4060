"""
ORIONIS API v1 - Chat Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.security import get_current_token
from app.services.auth_service import AuthService
from app.services.chat_service import ChatService
from app.schemas.schemas import (
    ChatRequest, ChatResponse, ConversationCreate, ConversationUpdate,
    ConversationResponse, MessageResponse
)

router = APIRouter(prefix="/chat", tags=["Chat"])


async def get_user_context(token: str, db: AsyncSession):
    """Helper to get user and tenant from token"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(token)
    return user.id, user.current_tenant.id if user.current_tenant else None


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Get all conversations"""
    user_id, tenant_id = await get_user_context(token, db)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="No tenant context")
    
    service = ChatService(db)
    return await service.get_conversations(tenant_id, user_id)


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    data: ConversationCreate,
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Create a new conversation"""
    user_id, tenant_id = await get_user_context(token, db)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="No tenant context")
    
    service = ChatService(db)
    conversation = await service.create_conversation(tenant_id, user_id, data)
    return ConversationResponse.model_validate(conversation)


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific conversation"""
    user_id, tenant_id = await get_user_context(token, db)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="No tenant context")
    
    service = ChatService(db)
    conversation = await service.get_conversation(conversation_id, tenant_id, user_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return ConversationResponse.model_validate(conversation)


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Delete a conversation"""
    user_id, tenant_id = await get_user_context(token, db)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="No tenant context")
    
    service = ChatService(db)
    deleted = await service.delete_conversation(conversation_id, tenant_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"success": True, "message": "Conversation deleted"}


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Get messages for a conversation"""
    user_id, tenant_id = await get_user_context(token, db)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="No tenant context")
    
    service = ChatService(db)
    return await service.get_messages(conversation_id, tenant_id, user_id)


@router.post("", response_model=ChatResponse)
async def send_message(
    data: ChatRequest,
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Send a chat message"""
    user_id, tenant_id = await get_user_context(token, db)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="No tenant context")
    
    service = ChatService(db)
    return await service.send_message(tenant_id, user_id, data)


@router.post("/stream")
async def stream_message(
    data: ChatRequest,
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Stream a chat message response"""
    user_id, tenant_id = await get_user_context(token, db)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="No tenant context")
    
    service = ChatService(db)
    return StreamingResponse(
        service.stream_message(tenant_id, user_id, data),
        media_type="text/event-stream"
    )
