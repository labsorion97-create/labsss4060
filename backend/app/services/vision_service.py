"""
ORIONIS Vision Service
"""
import base64
from typing import Optional, Dict, Any

from app.core.config import settings


class VisionService:
    """Vision service for image analysis"""
    
    async def analyze(
        self,
        image_base64: str,
        question: str = "Descreva detalhadamente esta imagem.",
        analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """Analyze an image using GPT-4o Vision"""
        from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
        import uuid
        
        # Build prompt based on analysis type
        prompts = {
            "general": question,
            "ocr": "Extraia todo o texto visível nesta imagem. Retorne apenas o texto extraído.",
            "document": "Analise este documento. Extraia informações estruturadas como título, data, conteúdo principal e quaisquer dados importantes.",
            "interface": "Analise esta interface/UI. Descreva os elementos, layout, cores e sugira melhorias de UX.",
            "chart": "Analise este gráfico/dashboard. Extraia os dados, tendências e insights principais."
        }
        
        prompt = prompts.get(analysis_type, question)
        
        chat = LlmChat(
            api_key=settings.EMERGENT_LLM_KEY,
            session_id=str(uuid.uuid4()),
            system_message="Você é um assistente especialista em análise de imagens. Seja preciso e detalhado."
        ).with_model("openai", "gpt-4o")
        
        user_message = UserMessage(
            text=prompt,
            file_contents=[ImageContent(image_base64=image_base64)]
        )
        
        response = await chat.send_message(user_message)
        
        return {
            "analysis": response,
            "analysis_type": analysis_type,
            "metadata": {}
        }
    
    async def ocr(self, image_base64: str) -> str:
        """Extract text from image"""
        result = await self.analyze(image_base64, analysis_type="ocr")
        return result["analysis"]
