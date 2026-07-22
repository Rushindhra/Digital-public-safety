"""Counterfeit currency screening endpoints."""
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.config import settings
from app.core.deps import get_current_user
from app.ml.counterfeit import InvalidNoteImage, analyse_note
from app.models.user import User
from app.schemas.counterfeit import CounterfeitAnalysis, Denomination

router = APIRouter(prefix="/counterfeit", tags=["Counterfeit Detection"])
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("/analyse", response_model=CounterfeitAnalysis)
async def analyse_currency_note(
    denomination: Denomination,
    image: UploadFile = File(...),
    _: User = Depends(get_current_user),
) -> CounterfeitAnalysis:
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Only JPEG, PNG, and WebP images are supported")
    limit = settings.MAX_UPLOAD_MB * 1024 * 1024
    content = await image.read(limit + 1)
    await image.close()
    if len(content) > limit:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, f"Image must not exceed {settings.MAX_UPLOAD_MB} MB")
    try:
        return analyse_note(content, denomination)
    except InvalidNoteImage as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc

