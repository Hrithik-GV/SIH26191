"""FastAPI router for comprehensive decision-support report generation and export."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.services.audit_service import AuditService
from backend.app.services.report_generation_service import ReportGenerationService
from backend.app.api.v1.endpoints.auth import (
    get_current_user,
    require_any_authority,
    require_admin,
)

router = APIRouter(prefix="/reports", tags=["Report Generation & Executive Exports"])


class ReportGenerateRequest(BaseModel):
    district: Optional[str] = Field("Wayanad", description="Jurisdiction district name")
    habitation_id: Optional[uuid.UUID] = Field(None, description="Target settlement ID for focal assessment")
    hazard_event_id: Optional[uuid.UUID] = Field(None, description="Focal hazard event / disaster trigger ID")
    relocation_site_id: Optional[uuid.UUID] = Field(None, description="Selected candidate resettlement parcel ID")
    officer_notes: Optional[str] = Field(None, description="Executive remarks or operational directives")


class ReportExportRequest(ReportGenerateRequest):
    format: str = Field("json", pattern="^(json|csv|pdf)$", description="Export format: json, csv, or pdf")


@router.get("/options", summary="Get Report Configuration Dropdown Options")
def get_report_options(
    db: Session = Depends(get_db),
    user: Dict[str, Any] = Depends(require_any_authority),
):
    """
    Returns available districts, monitored habitations, hazard events, and relocation sites
    to populate selection controls for authority users.
    """
    return ReportGenerationService.get_available_options(db)


@router.post("/generate", summary="Generate Comprehensive 13-Section Decision Support Report (JSON)")
def generate_report(
    payload: ReportGenerateRequest,
    db: Session = Depends(get_db),
    user: Dict[str, Any] = Depends(require_any_authority),
):
    """
    Compiles full 13-section decision support report with explicit epistemic demarcation:
    - Observed data
    - Model-derived scores
    - Prototype assumptions
    - Recommendations
    """
    report = ReportGenerationService.generate_report(
        db=db,
        district=payload.district,
        habitation_id=payload.habitation_id,
        hazard_event_id=payload.hazard_event_id,
        relocation_site_id=payload.relocation_site_id,
        officer=user,
        officer_notes=payload.officer_notes,
    )

    AuditService.record_action(
        action="REPORT_GENERATE",
        user_id=user["id"],
        user_name=user["name"],
        user_role=user["role"],
        resource_type="REPORT",
        resource_id=report["report_id"],
        details={
            "district": payload.district,
            "habitation_id": str(payload.habitation_id) if payload.habitation_id else None,
            "relocation_site_id": str(payload.relocation_site_id) if payload.relocation_site_id else None,
        },
    )

    return report


@router.post("/export", summary="Export Report as PDF, CSV, or JSON")
def export_report(
    payload: ReportExportRequest,
    db: Session = Depends(get_db),
    user: Dict[str, Any] = Depends(require_any_authority),
):
    """
    Compiles and exports the report formatted as PDF, CSV, or JSON attachment.
    Audited in the tamper-evident audit log.
    """
    report = ReportGenerationService.generate_report(
        db=db,
        district=payload.district,
        habitation_id=payload.habitation_id,
        hazard_event_id=payload.hazard_event_id,
        relocation_site_id=payload.relocation_site_id,
        officer=user,
        officer_notes=payload.officer_notes,
    )

    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    clean_hab = (report["jurisdiction"]["focal_habitation"]).replace(" ", "_").lower()
    filename_base = f"sih26_report_{clean_hab}_{timestamp_str}"

    AuditService.record_action(
        action="REPORT_EXPORT",
        user_id=user["id"],
        user_name=user["name"],
        user_role=user["role"],
        resource_type="REPORT",
        resource_id=report["report_id"],
        details={
            "format": payload.format,
            "district": payload.district,
            "habitation": report["jurisdiction"]["focal_habitation"],
        },
    )

    if payload.format.lower() == "csv":
        csv_content = ReportGenerationService.export_csv(report)
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename_base}.csv"},
        )

    if payload.format.lower() == "pdf":
        pdf_bytes = ReportGenerationService.export_pdf(report)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename_base}.pdf"},
        )

    # Default JSON
    return report
