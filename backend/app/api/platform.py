"""Unified APIs for scam detection, cases, analytics, graphs, maps and assistance."""
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_current_user, require_roles
from app.ml.scam import analyse_scam
from app.models.domain import FraudReport
from app.models.enums import ReportStatus, UserRole
from app.models.user import User
from app.schemas.platform import (
    AssistantRequest,
    GraphRequest,
    ReportCreate,
    ReportOut,
    ReportUpdate,
    ScamRequest,
    ScamResult,
)
from app.services.graph import analyse_graph

router = APIRouter(tags=["Public Safety Platform"])


@router.post("/scam/analyse", response_model=ScamResult)
async def scam_analysis(payload: ScamRequest, _: User = Depends(get_current_user)):
    return analyse_scam(payload)


@router.post("/reports", response_model=ReportOut, status_code=201)
async def create_report(
    payload: ReportCreate,
    user: User = Depends(get_current_user),
):
    report = FraudReport(
        reporter_id=user.id,
        category=payload.category,
        title=payload.title,
        description=payload.description,
        channel=payload.channel,
        risk_score=payload.risk_score,
        latitude=payload.latitude,
        longitude=payload.longitude,
        district=payload.district,
        metadata=payload.metadata,
    )
    await report.insert()
    return report


@router.get("/reports", response_model=list[ReportOut])
async def list_reports(
    user: User = Depends(get_current_user),
    limit: int = 100,
):
    if user.role == UserRole.CITIZEN:
        query = FraudReport.find(FraudReport.reporter_id == user.id)
    else:
        query = FraudReport.find()
    reports = await query.sort(-FraudReport.created_at).limit(
        min(max(limit, 1), 500)
    ).to_list()
    return reports


@router.patch("/reports/{report_id}", response_model=ReportOut)
async def update_report(
    report_id: str,
    payload: ReportUpdate,
    _: User = Depends(require_roles(UserRole.OFFICER, UserRole.ADMIN)),
):
    try:
        report_uuid = uuid.UUID(report_id)
    except ValueError as exc:
        raise HTTPException(404, "Report not found") from exc

    report = await FraudReport.get(report_uuid)
    if not report:
        raise HTTPException(404, "Report not found")

    report.status = payload.status
    report.updated_at = datetime.now(timezone.utc)
    await report.save()
    return report


@router.post("/graph/analyse")
async def graph_analysis(
    payload: GraphRequest,
    _: User = Depends(require_roles(UserRole.ANALYST, UserRole.OFFICER, UserRole.ADMIN)),
):
    try:
        return analyse_graph(payload.nodes, payload.edges)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/geo/hotspots")
async def hotspots(_: User = Depends(get_current_user)):
    pipeline = [
        {"$match": {"latitude": {"$ne": None}}},
        {
            "$group": {
                "_id": "$district",
                "latitude": {"$avg": "$latitude"},
                "longitude": {"$avg": "$longitude"},
                "incidents": {"$sum": 1},
                "risk_score": {"$avg": "$risk_score"},
            }
        },
    ]
    rows = await FraudReport.aggregate(pipeline).to_list()
    return [
        {
            "district": row["_id"] or "Unknown",
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "incidents": row["incidents"],
            "risk_score": round(row["risk_score"] or 0, 1),
        }
        for row in rows
    ]


@router.get("/analytics/summary")
async def analytics(_: User = Depends(get_current_user)):
    since = datetime.now(timezone.utc) - timedelta(days=30)
    total = await FraudReport.count()
    recent = await FraudReport.find(FraudReport.created_at >= since).count()
    risk_pipeline = [{"$group": {"_id": None, "avg": {"$avg": "$risk_score"}}}]
    risk_rows = await FraudReport.aggregate(risk_pipeline).to_list()
    risk = risk_rows[0]["avg"] if risk_rows else 0

    status_pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
    ]
    status_rows = await FraudReport.aggregate(status_pipeline).to_list()
    category_pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
    ]
    category_rows = await FraudReport.aggregate(category_pipeline).to_list()

    return {
        "total_reports": total,
        "reports_30d": recent,
        "average_risk": round(risk or 0, 1),
        "by_status": {str(row["_id"]): row["count"] for row in status_rows},
        "by_category": {row["_id"]: row["count"] for row in category_rows},
    }


@router.post("/assistant/chat")
async def assistant(
    payload: AssistantRequest,
    _: User = Depends(get_current_user),
):
    analysis = analyse_scam(
        ScamRequest(content=payload.message, channel="chat", language=payload.language)
    )
    return {
        "reply": analysis.explanation + " " + " ".join(analysis.suggested_actions),
        "risk": analysis.model_dump(),
        "emergency": {
            "cyber_fraud": "1930",
            "emergency": "112",
            "portal": "https://cybercrime.gov.in",
        },
        "disclaimer": (
            "For immediate danger call 112. "
            "This assistant does not replace law enforcement."
        ),
    }
