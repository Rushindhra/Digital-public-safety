"""Evidence ingestion with bounded streaming, hashing and access control."""
import hashlib
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.config import settings
from app.core.deps import require_roles
from app.models.domain import Evidence, FraudReport
from app.models.enums import UserRole
from app.models.user import User

router = APIRouter(prefix="/evidence", tags=["Evidence"])
ALLOWED = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/pdf",
    "audio/mpeg",
    "audio/wav",
    "video/mp4",
    "text/plain",
}


@router.post("/{report_id}", status_code=201)
async def upload_evidence(
    report_id: str,
    kind: str,
    file: UploadFile = File(...),
    _: User = Depends(require_roles(UserRole.OFFICER, UserRole.ADMIN)),
):
    try:
        report_uuid = uuid.UUID(report_id)
    except ValueError as exc:
        raise HTTPException(404, "Report not found") from exc

    report = await FraudReport.get(report_uuid)
    if not report:
        raise HTTPException(404, "Report not found")
    if file.content_type not in ALLOWED:
        raise HTTPException(415, "Unsupported evidence type")

    content = await file.read(settings.MAX_UPLOAD_MB * 1024 * 1024 + 1)
    await file.close()
    if len(content) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, "Evidence exceeds upload limit")

    digest = hashlib.sha256(content).hexdigest()
    existing = await Evidence.find_one(Evidence.sha256 == digest)
    if existing:
        raise HTTPException(409, "This evidence file has already been stored")

    root = Path(settings.UPLOAD_DIR).resolve()
    root.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "evidence").suffix.lower()[:10]
    target = root / f"{uuid.uuid4().hex}{suffix}"
    target.write_bytes(content)

    evidence = Evidence(
        report_id=report.id,
        kind=kind[:30],
        filename=Path(file.filename or "evidence").name,
        storage_path=str(target),
        sha256=digest,
        content_type=file.content_type,
        size_bytes=len(content),
    )
    await evidence.insert()
    return {
        "id": str(evidence.id),
        "filename": evidence.filename,
        "sha256": digest,
        "size_bytes": len(content),
    }
