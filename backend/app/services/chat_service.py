"""
ORIONIS Chat Service
"""
from datetime import datetime, timezone
from typing import Optional, List, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import json
import asyncio

from app.models.models import Conversation, Message, MessageRole, Tenant, AIModelSettings
from app.schemas.schemas import ChatRequest, ChatResponse, ConversationCreate, ConversationResponse, MessageResponse
from app.core.config import settings


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_conversations(self, tenant_id: str, user_id: str, limit: int = 50) -> List[ConversationResponse]:
        """Get all conversations for a user"""
        result = await self.db.execute(
            select(Conversation)
            .where(and_(Conversation.tenant_id == tenant_id, Conversation.user_id == user_id))
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )
        conversations = result.scalars().all()
        return [ConversationResponse.model_validate(c) for c in conversations]
    
    async def get_conversation(self, conversation_id: str, tenant_id: str, user_id: str) -> Optional[Conversation]:
        """Get a specific conversation"""
        result = await self.db.execute(
            select(Conversation).where(
                and_(
                    Conversation.id == conversation_id,
                    Conversation.tenant_id == tenant_id,
                    Conversation.user_id == user_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def create_conversation(self, tenant_id: str, user_id: str, data: ConversationCreate) -> Conversation:
        """Create a new conversation"""
        # Get AI settings
        result = await self.db.execute(
            select(AIModelSettings).where(AIModelSettings.tenant_id == tenant_id)
        )
        ai_settings = result.scalar_one_or_none()
        model = data.model or (ai_settings.primary_model if ai_settings else "gpt-4o")
        
        conversation = Conversation(
            tenant_id=tenant_id,
            user_id=user_id,
            title=data.title,
            system_prompt=data.system_prompt,
            model=model
        )
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation
    
    async def delete_conversation(self, conversation_id: str, tenant_id: str, user_id: str) -> bool:
        """Delete a conversation"""
        conversation = await self.get_conversation(conversation_id, tenant_id, user_id)
        if not conversation:
            return False
        
        await self.db.delete(conversation)
        await self.db.commit()
        return True
    
    async def get_messages(self, conversation_id: str, tenant_id: str, user_id: str, limit: int = 100) -> List[MessageResponse]:
        """Get messages for a conversation"""
        conversation = await self.get_conversation(conversation_id, tenant_id, user_id)
        if not conversation:
            return []
        
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        messages = result.scalars().all()
        return [MessageResponse.model_validate(m) for m in messages]
    
    async def add_message(
        self,
        conversation_id: str,
        role: MessageRole,
        content: str,
        content_type: str = "text",
        agent_name: Optional[str] = None,
        tokens_prompt: int = 0,
        tokens_completion: int = 0
    ) -> Message:
        """Add a message to a conversation"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            content_type=content_type,
            agent_name=agent_name,
            tokens_prompt=tokens_prompt,
            tokens_completion=tokens_completion
        )
        self.db.add(message)
        
        # Update conversation
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if conversation:
            conversation.total_messages += 1
            conversation.total_tokens += tokens_prompt + tokens_completion
            conversation.updated_at = datetime.now(timezone.utc)
        
        await self.db.commit()
        await self.db.refresh(message)
        return message
    
    async def send_message(
        self,
        tenant_id: str,
        user_id: str,
        request: ChatRequest
    ) -> ChatResponse:
        """Send a message and get AI response"""
        from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
        
        # Get or create conversation
        if request.conversation_id:
            conversation = await self.get_conversation(request.conversation_id, tenant_id, user_id)
            if not conversation:
                raise ValueError("Conversation not found")
        else:
            title = request.message[:50] + "..." if len(request.message) > 50 else request.message
            conversation = await self.create_conversation(
                tenant_id, user_id,
                ConversationCreate(title=title)
            )
        
        # Get AI settings
        result = await self.db.execute(
            select(AIModelSettings).where(AIModelSettings.tenant_id == tenant_id)
        )
        ai_settings = result.scalar_one_or_none()
        
        # Get tenant for AI persona
        result = await self.db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = result.scalar_one_or_none()
        
        # Build system message
        ai_name = tenant.ai_name if tenant else "ORIONIS"
        ai_persona = tenant.ai_persona if tenant else None
        
        system_message = f"""Você é a {ai_name} — um sistema operacional de inteligência artificial universal.

Sua persona: Inteligente, direta, proativa, precisa. Você não pergunta o que já entende. Você age, entrega e informa.

Princípios de resposta:
- Seja direta e precisa — sem rodeios desnecessários
- Entregue resultado, não promessa de resultado
- Nunca diga "não posso" — diga o que pode fazer e como

{ai_persona or ''}"""
        
        # Save user message
        await self.add_message(
            conversation.id,
            MessageRole.USER,
            request.message
        )
        
        # Get conversation history
        messages_history = await self.get_messages(conversation.id, tenant_id, user_id, limit=20)
        
        # Initialize chat
        model = ai_settings.primary_model if ai_settings else "gpt-4o"
        temperature = ai_settings.temperature if ai_settings else 0.7
        
        chat = LlmChat(
            api_key=settings.EMERGENT_LLM_KEY,
            session_id=conversation.id,
            system_message=system_message
        ).with_model("openai", model)
        
        # Add history
        for msg in messages_history[:-1]:
            if msg.role == MessageRole.USER:
                chat.add_user_message(msg.content)
            else:
                chat.add_assistant_message(msg.content)
        
        # Create user message
        if request.image_base64:
            user_message = UserMessage(
                text=request.message,
                file_contents=[ImageContent(image_base64=request.image_base64)]
            )
        else:
            user_message = UserMessage(text=request.message)
        
        # Get response
        response_text = await chat.send_message(user_message)
        
        # Save assistant message
        await self.add_message(
            conversation.id,
            MessageRole.ASSISTANT,
            response_text,
            agent_name="Core"
        )
        
        return ChatResponse(
            conversation_id=conversation.id,
            message=response_text,
            agent_name="Core"
        )
    
    async def stream_message(
        self,
        tenant_id: str,
        user_id: str,
        request: ChatRequest
    ) -> AsyncGenerator[str, None]:
        """Stream a message response"""
        # For now, get full response and stream it
        response = await self.send_message(tenant_id, user_id, request)
        
        # Simulate streaming
        chunk_size = 10
        for i in range(0, len(response.message), chunk_size):
            chunk = response.message[i:i+chunk_size]
            yield f"data: {json.dumps({'chunk': chunk, 'conversation_id': response.conversation_id})}\n\n"
            await asyncio.sleep(0.02)
        
        yield f"data: {json.dumps({'done': True, 'conversation_id': response.conversation_id})}\n\n"
