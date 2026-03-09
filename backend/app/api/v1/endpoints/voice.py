"""
ORIONIS API v1 - Voice Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_token
from app.services.auth_service import AuthService
from app.services.voice_service import VoiceService
from app.schemas.schemas import VoiceTranscribeResponse, VoiceSpeakRequest, VoiceSpeakResponse

router = APIRouter(prefix="/voice", tags=["Voice"])


@router.post("/transcribe", response_model=VoiceTranscribeResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Transcribe audio to text"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    audio_content = await file.read()
    service = VoiceService()
    
    result = await service.transcribe(audio_content, file.filename or "audio.webm")
    return VoiceTranscribeResponse(**result)


@router.post("/speak", response_model=VoiceSpeakResponse)
async def text_to_speech(
    data: VoiceSpeakRequest,
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Convert text to speech"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = VoiceService()
    audio_base64 = await service.speak(data.text, data.voice, data.speed)
    
    return VoiceSpeakResponse(audio_base64=audio_base64)
