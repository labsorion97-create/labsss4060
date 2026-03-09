"""
ORIONIS Voice Service
"""
from typing import Optional
import io
import base64

from app.core.config import settings


class VoiceService:
    """Voice service for STT and TTS"""
    
    async def transcribe(self, audio_content: bytes, filename: str = "audio.webm") -> dict:
        """Transcribe audio to text using Whisper"""
        from emergentintegrations.llm.openai import OpenAISpeechToText
        
        stt = OpenAISpeechToText(api_key=settings.EMERGENT_LLM_KEY)
        
        audio_file = io.BytesIO(audio_content)
        audio_file.name = filename
        
        response = await stt.transcribe(
            file=audio_file,
            model="whisper-1",
            response_format="json"
        )
        
        return {
            "text": response.text,
            "language": getattr(response, "language", None),
            "duration": getattr(response, "duration", None)
        }
    
    async def speak(self, text: str, voice: str = "nova", speed: float = 1.0) -> str:
        """Convert text to speech and return base64 audio"""
        from emergentintegrations.llm.openai import OpenAITextToSpeech
        
        # Limit text length
        text = text[:4096]
        
        tts = OpenAITextToSpeech(api_key=settings.EMERGENT_LLM_KEY)
        
        audio_bytes = await tts.generate_speech(
            text=text,
            model="tts-1",
            voice=voice,
            response_format="mp3"
        )
        
        return base64.b64encode(audio_bytes).decode('utf-8')
