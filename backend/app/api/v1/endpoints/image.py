"""
ORIONIS API v1 - Image Generation Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_token
from app.services.image_service import ImageService
from app.schemas.schemas import ImageGenerateRequest, ImageGenerateResponse

router = APIRouter(prefix="/image", tags=["Image Generation"])


@router.post("/generate", response_model=ImageGenerateResponse)
async def generate_image(
    data: ImageGenerateRequest,
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Generate images from prompt"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = ImageService()
    images = await service.generate(data.prompt, data.n, data.size, data.quality)
    
    return ImageGenerateResponse(images=images)
