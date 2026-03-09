"""
ORIONIS API v1 - Vision Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_token
from app.services.vision_service import VisionService
from app.schemas.schemas import VisionAnalyzeRequest, VisionAnalyzeResponse

router = APIRouter(prefix="/vision", tags=["Vision"])


@router.post("/analyze", response_model=VisionAnalyzeResponse)
async def analyze_image(
    data: VisionAnalyzeRequest,
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Analyze an image"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = VisionService()
    result = await service.analyze(data.image_base64, data.question, data.analysis_type)
    
    return VisionAnalyzeResponse(**result)


@router.post("/ocr")
async def ocr_image(
    data: VisionAnalyzeRequest,
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Extract text from image using OCR"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    service = VisionService()
    text = await service.ocr(data.image_base64)
    
    return {"text": text}


@router.post("/document")
async def analyze_document(
    data: VisionAnalyzeRequest,
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Analyze a document image"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    data.analysis_type = "document"
    service = VisionService()
    result = await service.analyze(data.image_base64, data.question, data.analysis_type)
    
    return VisionAnalyzeResponse(**result)


@router.post("/interface")
async def analyze_interface(
    data: VisionAnalyzeRequest,
    token: str = Depends(get_current_token),
    db: AsyncSession = Depends(get_db)
):
    """Analyze a UI/interface screenshot"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    data.analysis_type = "interface"
    service = VisionService()
    result = await service.analyze(data.image_base64, data.question, data.analysis_type)
    
    return VisionAnalyzeResponse(**result)
