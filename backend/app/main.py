"""
ORIONIS - Main Application
Orion Intelligent System v3.0

Enterprise-grade AI Operating System with:
- Multi-tenant architecture
- Multi-modal AI (Chat, Voice, Vision, Image Gen)
- Knowledge Base & Memory
- Automations & Integrations
- White-label support
"""
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from app.core.config import settings
from app.core.database import init_db, close_db, mongo_db
from app.api.v1.router import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("🚀 Starting ORIONIS v3.0...")
    
    # Initialize database (commented for MongoDB-only mode)
    # await init_db()
    
    logger.info("✅ ORIONIS is ready")
    yield
    
    logger.info("🔄 Shutting down ORIONIS...")
    await close_db()
    logger.info("👋 ORIONIS shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="ORIONIS API",
    description="Orion Intelligent System - Enterprise AI Operating System",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        }
    )


# Include API v1 router
app.include_router(api_router, prefix="/api/v1")


# ============== LEGACY API ROUTES (MongoDB-based, for backward compatibility) ==============

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import uuid
import httpx
import base64
import json
import asyncio

legacy_router = APIRouter(prefix="/api")


# Legacy Models
class LegacyChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    image_base64: Optional[str] = None


class LegacySessionRequest(BaseModel):
    session_id: str


class LegacyImageRequest(BaseModel):
    prompt: str


class LegacyVisionRequest(BaseModel):
    image_base64: str
    question: Optional[str] = "Descreva detalhadamente esta imagem."


class LegacyTTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "nova"


# Helper to get user from token/cookie
async def get_legacy_user(request: Request):
    session_token = request.cookies.get("session_token")
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ")[1]
    
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session = await mongo_db.user_sessions.find_one({"session_token": session_token}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    expires_at = session["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")
    
    user = await mongo_db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


# Root
@legacy_router.get("/")
async def legacy_root():
    return {"message": "ORIONIS API v3.0 - Orion Intelligent System"}


# Health
@legacy_router.get("/health")
async def legacy_health():
    return {"status": "online", "system": "ORIONIS", "version": "3.0"}


# System Status
@legacy_router.get("/system/status")
async def legacy_system_status():
    agents = [
        {"name": "Core Orchestrator", "status": "active", "type": "core"},
        {"name": "Research Agent", "status": "active", "type": "knowledge"},
        {"name": "Knowledge Agent", "status": "active", "type": "knowledge"},
        {"name": "Voice Agent", "status": "active", "type": "multimodal"},
        {"name": "Vision Agent", "status": "active", "type": "multimodal"},
        {"name": "Design Agent", "status": "active", "type": "builder"},
        {"name": "Development Agent", "status": "standby", "type": "builder"},
        {"name": "Sales Agent", "status": "standby", "type": "operational"},
        {"name": "Operations Agent", "status": "standby", "type": "operational"},
    ]
    
    return {
        "system": "ORIONIS",
        "version": "3.0",
        "status": "operational",
        "uptime": "99.9%",
        "agents": agents,
        "capabilities": {
            "chat": True,
            "voice": True,
            "vision": True,
            "image_generation": True,
            "streaming": True
        }
    }


# Auth Session Exchange
@legacy_router.post("/auth/session")
async def legacy_auth_session(request: LegacySessionRequest, response: Response):
    try:
        async with httpx.AsyncClient() as http_client:
            resp = await http_client.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": request.session_id},
                timeout=10.0
            )
            if resp.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid session")
            
            data = resp.json()
    except httpx.RequestError as e:
        logger.error(f"Auth request failed: {e}")
        raise HTTPException(status_code=500, detail="Authentication service unavailable")
    
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    existing_user = await mongo_db.users.find_one({"email": data["email"]}, {"_id": 0})
    
    if existing_user:
        user_id = existing_user["user_id"]
        await mongo_db.users.update_one(
            {"email": data["email"]},
            {"$set": {"name": data["name"], "picture": data.get("picture")}}
        )
    else:
        user_doc = {
            "user_id": user_id,
            "email": data["email"],
            "name": data["name"],
            "picture": data.get("picture"),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await mongo_db.users.insert_one(user_doc)
    
    session_token = data.get("session_token", str(uuid.uuid4()))
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    session_doc = {
        "session_id": str(uuid.uuid4()),
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await mongo_db.user_sessions.insert_one(session_doc)
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7*24*60*60,
        path="/"
    )
    
    user = await mongo_db.users.find_one({"user_id": user_id}, {"_id": 0})
    return user


# Auth Me
@legacy_router.get("/auth/me")
async def legacy_auth_me(request: Request):
    user = await get_legacy_user(request)
    return user


# Auth Logout
@legacy_router.post("/auth/logout")
async def legacy_auth_logout(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if session_token:
        await mongo_db.user_sessions.delete_many({"session_token": session_token})
    
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Logged out successfully"}


# Chat
@legacy_router.post("/chat")
async def legacy_chat(request: Request, data: LegacyChatRequest):
    from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
    
    user = await get_legacy_user(request)
    
    api_key = settings.EMERGENT_LLM_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="LLM API key not configured")
    
    # Get or create conversation
    if data.conversation_id:
        conv = await mongo_db.conversations.find_one(
            {"conversation_id": data.conversation_id, "user_id": user["user_id"]},
            {"_id": 0}
        )
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
        conversation_id = data.conversation_id
    else:
        conversation_id = str(uuid.uuid4())
        title = data.message[:50] + "..." if len(data.message) > 50 else data.message
        conv_doc = {
            "conversation_id": conversation_id,
            "user_id": user["user_id"],
            "title": title,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await mongo_db.conversations.insert_one(conv_doc)
    
    # Save user message
    user_msg_doc = {
        "message_id": str(uuid.uuid4()),
        "conversation_id": conversation_id,
        "user_id": user["user_id"],
        "role": "user",
        "content": data.message,
        "content_type": "text",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await mongo_db.messages.insert_one(user_msg_doc)
    
    # Get history
    history = await mongo_db.messages.find(
        {"conversation_id": conversation_id},
        {"_id": 0}
    ).sort("created_at", 1).to_list(50)
    
    system_message = """Você é a ORIONIS — Orion Intelligent System — um sistema operacional de inteligência artificial universal.

Sua persona: Inteligente, direta, proativa, precisa. Você não pergunta o que já entende. Você age, entrega e informa.

Princípios de resposta:
- Seja direta e precisa — sem rodeios
- Entregue resultado, não promessa
- Nunca diga "não posso" — diga o que pode fazer

Tom: Sistema de alta performance. Inteligente, confiante, eficiente."""
    
    chat = LlmChat(
        api_key=api_key,
        session_id=conversation_id,
        system_message=system_message
    ).with_model("openai", "gpt-4o")
    
    for msg in history[:-1]:
        if msg["role"] == "user":
            chat.add_user_message(msg["content"])
        else:
            chat.add_assistant_message(msg["content"])
    
    if data.image_base64:
        user_message = UserMessage(
            text=data.message,
            file_contents=[ImageContent(image_base64=data.image_base64)]
        )
    else:
        user_message = UserMessage(text=data.message)
    
    try:
        response_text = await chat.send_message(user_message)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
    
    # Save assistant message
    assistant_msg_doc = {
        "message_id": str(uuid.uuid4()),
        "conversation_id": conversation_id,
        "user_id": user["user_id"],
        "role": "assistant",
        "content": response_text,
        "content_type": "text",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await mongo_db.messages.insert_one(assistant_msg_doc)
    
    # Update conversation
    await mongo_db.conversations.update_one(
        {"conversation_id": conversation_id},
        {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {
        "conversation_id": conversation_id,
        "message": response_text,
        "role": "assistant"
    }


# Conversations
@legacy_router.get("/conversations")
async def legacy_get_conversations(request: Request):
    user = await get_legacy_user(request)
    conversations = await mongo_db.conversations.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).sort("updated_at", -1).to_list(100)
    return conversations


@legacy_router.get("/conversations/{conversation_id}/messages")
async def legacy_get_messages(conversation_id: str, request: Request):
    user = await get_legacy_user(request)
    conv = await mongo_db.conversations.find_one(
        {"conversation_id": conversation_id, "user_id": user["user_id"]},
        {"_id": 0}
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = await mongo_db.messages.find(
        {"conversation_id": conversation_id},
        {"_id": 0}
    ).sort("created_at", 1).to_list(1000)
    return messages


@legacy_router.delete("/conversations/{conversation_id}")
async def legacy_delete_conversation(conversation_id: str, request: Request):
    user = await get_legacy_user(request)
    result = await mongo_db.conversations.delete_one(
        {"conversation_id": conversation_id, "user_id": user["user_id"]}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    await mongo_db.messages.delete_many({"conversation_id": conversation_id})
    return {"message": "Conversation deleted"}


# Voice Transcribe
@legacy_router.post("/voice/transcribe")
async def legacy_voice_transcribe(file: UploadFile = File(...), request: Request = None):
    from emergentintegrations.llm.openai import OpenAISpeechToText
    import io
    
    user = await get_legacy_user(request)
    
    api_key = settings.EMERGENT_LLM_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    try:
        audio_content = await file.read()
        stt = OpenAISpeechToText(api_key=api_key)
        
        audio_file = io.BytesIO(audio_content)
        audio_file.name = file.filename or "audio.webm"
        
        response = await stt.transcribe(
            file=audio_file,
            model="whisper-1",
            response_format="json"
        )
        
        return {"text": response.text}
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


# Voice Speak
@legacy_router.post("/voice/speak")
async def legacy_voice_speak(data: LegacyTTSRequest, request: Request):
    from emergentintegrations.llm.openai import OpenAITextToSpeech
    
    user = await get_legacy_user(request)
    
    api_key = settings.EMERGENT_LLM_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    try:
        tts = OpenAITextToSpeech(api_key=api_key)
        audio_bytes = await tts.generate_speech(
            text=data.text[:500],
            model="tts-1",
            voice=data.voice,
            response_format="mp3"
        )
        
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        return {"audio_base64": audio_base64}
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")


# Vision Analyze
@legacy_router.post("/vision/analyze")
async def legacy_vision_analyze(data: LegacyVisionRequest, request: Request):
    from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
    
    user = await get_legacy_user(request)
    
    api_key = settings.EMERGENT_LLM_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    try:
        chat = LlmChat(
            api_key=api_key,
            session_id=str(uuid.uuid4()),
            system_message="Você é um assistente de análise de imagens. Analise imagens de forma detalhada e precisa."
        ).with_model("openai", "gpt-4o")
        
        user_message = UserMessage(
            text=data.question,
            file_contents=[ImageContent(image_base64=data.image_base64)]
        )
        
        response = await chat.send_message(user_message)
        return {"analysis": response}
    except Exception as e:
        logger.error(f"Vision analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# Image Generate
@legacy_router.post("/image/generate")
async def legacy_image_generate(data: LegacyImageRequest, request: Request):
    from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration
    
    user = await get_legacy_user(request)
    
    api_key = settings.EMERGENT_LLM_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    try:
        image_gen = OpenAIImageGeneration(api_key=api_key)
        images = await image_gen.generate_images(
            prompt=data.prompt,
            model="gpt-image-1",
            number_of_images=1
        )
        
        if images and len(images) > 0:
            image_base64 = base64.b64encode(images[0]).decode('utf-8')
            return {"image_base64": image_base64}
        else:
            raise HTTPException(status_code=500, detail="No image was generated")
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


# Include legacy router
app.include_router(legacy_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
