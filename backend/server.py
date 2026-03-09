from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Request, Response, Depends
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import httpx
import base64
import json
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="ORIONIS API", version="3.0")

# Create router with /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============== MODELS ==============

class User(BaseModel):
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Message(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    user_id: str
    role: str  # user, assistant
    content: str
    content_type: str = "text"  # text, image, audio
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Conversation(BaseModel):
    conversation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str = "Nova Conversa"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    image_base64: Optional[str] = None

class VoiceTranscribeResponse(BaseModel):
    text: str
    language: Optional[str] = None

class ImageGenerateRequest(BaseModel):
    prompt: str

class ImageAnalyzeRequest(BaseModel):
    image_base64: str
    question: Optional[str] = "Descreva detalhadamente esta imagem."

# ============== AUTH HELPERS ==============

async def get_current_user(request: Request) -> User:
    """Get current user from session token"""
    session_token = request.cookies.get("session_token")
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ")[1]
    
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session = await db.user_sessions.find_one({"session_token": session_token}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    expires_at = session["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")
    
    user = await db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return User(**user)

async def get_optional_user(request: Request) -> Optional[User]:
    """Get current user if authenticated, otherwise None"""
    try:
        return await get_current_user(request)
    except HTTPException:
        return None

# ============== AUTH ENDPOINTS ==============

class SessionRequest(BaseModel):
    session_id: str

@api_router.post("/auth/session")
async def exchange_session(request: SessionRequest, response: Response):
    """Exchange session_id from OAuth for session data"""
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
    existing_user = await db.users.find_one({"email": data["email"]}, {"_id": 0})
    
    if existing_user:
        user_id = existing_user["user_id"]
        await db.users.update_one(
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
        await db.users.insert_one(user_doc)
    
    session_token = data.get("session_token", str(uuid.uuid4()))
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    session_doc = {
        "session_id": str(uuid.uuid4()),
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.user_sessions.insert_one(session_doc)
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7*24*60*60,
        path="/"
    )
    
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    return user

@api_router.get("/auth/me")
async def get_me(user: User = Depends(get_current_user)):
    """Get current authenticated user"""
    return user.model_dump()

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    """Logout user and clear session"""
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_many({"session_token": session_token})
    
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Logged out successfully"}

# ============== CHAT ENDPOINTS ==============

@api_router.post("/chat")
async def chat(request: ChatRequest, user: User = Depends(get_current_user)):
    """Send a message to ORIONIS and get a response"""
    from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
    
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="LLM API key not configured")
    
    # Get or create conversation
    if request.conversation_id:
        conv = await db.conversations.find_one(
            {"conversation_id": request.conversation_id, "user_id": user.user_id},
            {"_id": 0}
        )
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
        conversation_id = request.conversation_id
    else:
        conversation_id = str(uuid.uuid4())
        title = request.message[:50] + "..." if len(request.message) > 50 else request.message
        conv_doc = {
            "conversation_id": conversation_id,
            "user_id": user.user_id,
            "title": title,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.conversations.insert_one(conv_doc)
    
    # Save user message
    user_msg_doc = {
        "message_id": str(uuid.uuid4()),
        "conversation_id": conversation_id,
        "user_id": user.user_id,
        "role": "user",
        "content": request.message,
        "content_type": "text",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.messages.insert_one(user_msg_doc)
    
    # Get conversation history
    history = await db.messages.find(
        {"conversation_id": conversation_id},
        {"_id": 0}
    ).sort("created_at", 1).to_list(50)
    
    # Build system message
    system_message = """Você é a ORIONIS — Orion Intelligent System — um sistema operacional de inteligência artificial universal.

Sua persona: Inteligente, direta, proativa, precisa. Você não pergunta o que já entende. Você age, entrega e informa.
Você fala como um sistema de alta performance, não como um chatbot genérico.

Princípios de resposta:
- Seja direta e precisa — sem rodeios desnecessários
- Entregue resultado, não promessa de resultado
- Se for uma tarefa longa, informe o progresso
- Se precisar de informação, pergunte de forma cirúrgica
- Nunca diga "não posso" — diga o que pode fazer e como

Tom: Sistema de alta performance. Inteligente, confiante, eficiente. Como o Jarvis: responde, age, entrega.

Você pode ajudar com: pesquisa, análise, código, planejamento, criação de conteúdo, automação e muito mais."""
    
    # Initialize chat with history
    chat = LlmChat(
        api_key=api_key,
        session_id=conversation_id,
        system_message=system_message
    ).with_model("openai", "gpt-4o")
    
    # Add history to chat context
    for msg in history[:-1]:  # Exclude last message (current)
        if msg["role"] == "user":
            chat.add_user_message(msg["content"])
        else:
            chat.add_assistant_message(msg["content"])
    
    # Create user message
    if request.image_base64:
        user_message = UserMessage(
            text=request.message,
            file_contents=[ImageContent(image_base64=request.image_base64)]
        )
    else:
        user_message = UserMessage(text=request.message)
    
    # Get response
    try:
        response_text = await chat.send_message(user_message)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
    
    # Save assistant message
    assistant_msg_doc = {
        "message_id": str(uuid.uuid4()),
        "conversation_id": conversation_id,
        "user_id": user.user_id,
        "role": "assistant",
        "content": response_text,
        "content_type": "text",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.messages.insert_one(assistant_msg_doc)
    
    # Update conversation
    await db.conversations.update_one(
        {"conversation_id": conversation_id},
        {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {
        "conversation_id": conversation_id,
        "message": response_text,
        "role": "assistant"
    }

@api_router.post("/chat/stream")
async def chat_stream(request: ChatRequest, user: User = Depends(get_current_user)):
    """Stream chat response using SSE"""
    from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
    
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="LLM API key not configured")
    
    # Get or create conversation
    if request.conversation_id:
        conv = await db.conversations.find_one(
            {"conversation_id": request.conversation_id, "user_id": user.user_id},
            {"_id": 0}
        )
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
        conversation_id = request.conversation_id
    else:
        conversation_id = str(uuid.uuid4())
        title = request.message[:50] + "..." if len(request.message) > 50 else request.message
        conv_doc = {
            "conversation_id": conversation_id,
            "user_id": user.user_id,
            "title": title,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.conversations.insert_one(conv_doc)
    
    # Save user message
    user_msg_doc = {
        "message_id": str(uuid.uuid4()),
        "conversation_id": conversation_id,
        "user_id": user.user_id,
        "role": "user",
        "content": request.message,
        "content_type": "text",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.messages.insert_one(user_msg_doc)
    
    async def generate():
        system_message = """Você é a ORIONIS — Orion Intelligent System — um sistema operacional de inteligência artificial universal.
Sua persona: Inteligente, direta, proativa, precisa. Responda de forma concisa e eficiente."""
        
        chat = LlmChat(
            api_key=api_key,
            session_id=conversation_id,
            system_message=system_message
        ).with_model("openai", "gpt-4o")
        
        if request.image_base64:
            user_message = UserMessage(
                text=request.message,
                file_contents=[ImageContent(image_base64=request.image_base64)]
            )
        else:
            user_message = UserMessage(text=request.message)
        
        full_response = ""
        try:
            response_text = await chat.send_message(user_message)
            full_response = response_text
            
            # Send response in chunks for streaming effect
            chunk_size = 10
            for i in range(0, len(response_text), chunk_size):
                chunk = response_text[i:i+chunk_size]
                yield f"data: {json.dumps({'chunk': chunk, 'conversation_id': conversation_id})}\n\n"
                await asyncio.sleep(0.02)
            
            yield f"data: {json.dumps({'done': True, 'conversation_id': conversation_id})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return
        
        # Save assistant message
        assistant_msg_doc = {
            "message_id": str(uuid.uuid4()),
            "conversation_id": conversation_id,
            "user_id": user.user_id,
            "role": "assistant",
            "content": full_response,
            "content_type": "text",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.messages.insert_one(assistant_msg_doc)
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@api_router.get("/conversations")
async def get_conversations(user: User = Depends(get_current_user)):
    """Get all conversations for the user"""
    conversations = await db.conversations.find(
        {"user_id": user.user_id},
        {"_id": 0}
    ).sort("updated_at", -1).to_list(100)
    return conversations

@api_router.get("/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: str, user: User = Depends(get_current_user)):
    """Get messages for a conversation"""
    conv = await db.conversations.find_one(
        {"conversation_id": conversation_id, "user_id": user.user_id},
        {"_id": 0}
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = await db.messages.find(
        {"conversation_id": conversation_id},
        {"_id": 0}
    ).sort("created_at", 1).to_list(1000)
    return messages

@api_router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, user: User = Depends(get_current_user)):
    """Delete a conversation"""
    result = await db.conversations.delete_one(
        {"conversation_id": conversation_id, "user_id": user.user_id}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    await db.messages.delete_many({"conversation_id": conversation_id})
    return {"message": "Conversation deleted"}

# ============== VOICE ENDPOINTS ==============

@api_router.post("/voice/transcribe", response_model=VoiceTranscribeResponse)
async def transcribe_audio(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    """Transcribe audio to text using Whisper"""
    from emergentintegrations.llm.openai import OpenAISpeechToText
    
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    try:
        audio_content = await file.read()
        stt = OpenAISpeechToText(api_key=api_key)
        
        # Create a file-like object
        import io
        audio_file = io.BytesIO(audio_content)
        audio_file.name = file.filename or "audio.webm"
        
        response = await stt.transcribe(
            file=audio_file,
            model="whisper-1",
            response_format="json"
        )
        
        return VoiceTranscribeResponse(text=response.text)
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@api_router.post("/voice/speak")
async def text_to_speech(request: Request, user: User = Depends(get_current_user)):
    """Convert text to speech"""
    from emergentintegrations.llm.openai import OpenAITextToSpeech
    
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    body = await request.json()
    text = body.get("text", "")
    voice = body.get("voice", "nova")
    
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    try:
        tts = OpenAITextToSpeech(api_key=api_key)
        audio_bytes = await tts.generate_speech(
            text=text,
            model="tts-1",
            voice=voice,
            response_format="mp3"
        )
        
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        return {"audio_base64": audio_base64}
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")

# ============== VISION ENDPOINTS ==============

@api_router.post("/vision/analyze")
async def analyze_image(request: ImageAnalyzeRequest, user: User = Depends(get_current_user)):
    """Analyze an image using GPT-4o Vision"""
    from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
    
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    try:
        chat = LlmChat(
            api_key=api_key,
            session_id=str(uuid.uuid4()),
            system_message="Você é um assistente de análise de imagens. Analise imagens de forma detalhada e precisa."
        ).with_model("openai", "gpt-4o")
        
        user_message = UserMessage(
            text=request.question,
            file_contents=[ImageContent(image_base64=request.image_base64)]
        )
        
        response = await chat.send_message(user_message)
        return {"analysis": response}
    except Exception as e:
        logger.error(f"Vision analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# ============== IMAGE GENERATION ENDPOINTS ==============

@api_router.post("/image/generate")
async def generate_image(request: ImageGenerateRequest, user: User = Depends(get_current_user)):
    """Generate an image using DALL-E/GPT Image"""
    from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration
    
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    try:
        image_gen = OpenAIImageGeneration(api_key=api_key)
        images = await image_gen.generate_images(
            prompt=request.prompt,
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

# ============== SYSTEM ENDPOINTS ==============

@api_router.get("/")
async def root():
    return {"message": "ORIONIS API v3.0 - Orion Intelligent System"}

@api_router.get("/health")
async def health():
    return {"status": "online", "system": "ORIONIS", "version": "3.0"}

@api_router.get("/system/status")
async def system_status(user: Optional[User] = Depends(get_optional_user)):
    """Get system status"""
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

# Include router
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
