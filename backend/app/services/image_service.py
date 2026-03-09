"""
ORIONIS Image Generation Service
"""
import base64
from typing import List

from app.core.config import settings


class ImageService:
    """Image generation service"""
    
    async def generate(
        self,
        prompt: str,
        n: int = 1,
        size: str = "1024x1024",
        quality: str = "standard"
    ) -> List[str]:
        """Generate images from prompt"""
        from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration
        
        image_gen = OpenAIImageGeneration(api_key=settings.EMERGENT_LLM_KEY)
        
        images = await image_gen.generate_images(
            prompt=prompt,
            model="gpt-image-1",
            number_of_images=n
        )
        
        # Convert to base64
        result = []
        for img_bytes in images:
            result.append(base64.b64encode(img_bytes).decode('utf-8'))
        
        return result
