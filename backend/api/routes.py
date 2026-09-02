# REST API routes for MediGuard: patient vitals ingestion (SepsisGuard),
# prescription submission (CrossCare, JSON or PDF upload), SQLite persistence
# of every result, and download endpoints for the Nutrient-generated signed
# audit / drug report PDFs.

import base64
import json
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.websocket import manager
from database import InteractionResultRecord, PrescriptionRecord, SepsisAlertRecord, VitalsRecord, get_session
from graph.crosscare_workflow import crosscare_app
from graph.sepsisguard_workflow import sepsisguard_app
from models.schemas import PatientVitals, Prescription

router = APIRouter()

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# In-memory result caches keyed by patient_id, so the download endpoints
# below can serve the most recent PDF without an extra DB round-trip. SQLite
# (see backend/database.py) is the durable store; this is just a hot cache.
_sepsisguard_results: dict[str, dict] = {}
_crosscare_results: dict[str, dict] = {}


@router.get("/patients")
async def list_patients():
    with open(DATA_DIR / "simulated_patients.json") as f:
        return json.load(f)


@router.post("/sepsisguard/vitals")
async def submit_vitals(vitals: PatientVitals, db: AsyncSession = Depends(get_session)):
    """Feeds a vitals reading into the SepsisGuard LangGraph pipeline."""
    result = sepsisguard_app.invoke({
        "patient_id": vitals.patient_id,
        "patient_name": vitals.patient_name,
        "vitals": vitals.model_dump(),
        "current_medications": vitals.current_medications,
    })
    _sepsisguard_results[vitals.patient_id] = result

    db.add(VitalsRecord(patient_id=vitals.patient_id, vitals=vitals.model_dump()))
    if result.get("sepsis_alert"):
        db.add(SepsisAlertRecord(
            patient_id=vitals.patient_id,
            qsofa_score=result.get("qsofa_score"),
            result=result,
        ))
        await manager.broadcast({"type": "sepsis_alert", "data": result})
    await db.commit()

    return result


@router.post("/crosscare/prescriptions")
async def submit_prescription(prescription: Prescription, db: AsyncSession = Depends(get_session)):
    """Feeds a new prescription into the CrossCare LangGraph pipeline."""
    result = crosscare_app.invoke(
        {
            "patient_id": prescription.patient_id,
            "patient_name": prescription.patient_name,
            "doctor_name": prescription.doctor_name,
            "ocr_text": [],
            "medicines": prescription.medicines,
            "dosages": prescription.dosages,
        }
    )
    _crosscare_results[prescription.patient_id] = result

    db.add(PrescriptionRecord(
        patient_id=prescription.patient_id,
        doctor_name=prescription.doctor_name,
        prescription=prescription.model_dump(),
    ))
    db.add(InteractionResultRecord(
        patient_id=prescription.patient_id,
        risk_level=result.get("risk_level"),
        result=result,
    ))
    await manager.broadcast({"type": "drug_interaction_result", "data": result})
    await db.commit()

    return result


@router.post("/upload-prescription")
async def upload_prescription(
    patient_id: str,
    patient_name: str = "",
    doctor_name: str = "",
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session),
):
    """
    Accepts an uploaded prescription PDF, runs it through the CrossCare
    pipeline (Nutrient Data Extraction -> Pharmacology Interaction ->
    Physician Recommendation), persists the result, and returns the drug
    interaction findings plus a pointer to the downloadable report PDF.
    """
    pdf_bytes = await file.read()
    result = crosscare_app.invoke(
        {
            "patient_id": patient_id,
            "patient_name": patient_name,
            "doctor_name": doctor_name,
            "ocr_text": [],
            "prescription_pdf_base64": base64.b64encode(pdf_bytes).decode(),
        }
    )
    _crosscare_results[patient_id] = result

    db.add(PrescriptionRecord(
        patient_id=patient_id,
        doctor_name=doctor_name or None,
        prescription={"source": "pdf_upload", "filename": file.filename},
    ))
    db.add(InteractionResultRecord(
        patient_id=patient_id,
        risk_level=result.get("risk_level"),
        result=result,
    ))
    await manager.broadcast({"type": "drug_interaction_result", "data": result})
    await db.commit()

    # Returns the full graph state (same shape as /crosscare/prescriptions)
    # so both submission paths are interchangeable for callers/UI code.
    return result


@router.get("/download-audit/{patient_id}")
async def download_audit(patient_id: str, db: AsyncSession = Depends(get_session)):
    """
    Returns the signed SepsisGuard audit PDF for download. Checks the
    in-memory hot cache first, then falls back to the most recent SQLite
    record so downloads survive a server restart.
    """
    result = _sepsisguard_results.get(patient_id)
    if not result or not result.get("signed_audit_pdf_base64"):
        query = (
            select(SepsisAlertRecord)
            .where(SepsisAlertRecord.patient_id == patient_id)
            .order_by(SepsisAlertRecord.created_at.desc())
            .limit(1)
        )
        record = (await db.execute(query)).scalar_one_or_none()
        result = record.result if record else None

    if not result or not result.get("signed_audit_pdf_base64"):
        raise HTTPException(status_code=404, detail="No audit PDF available for this patient")

    pdf_bytes = base64.b64decode(result["signed_audit_pdf_base64"])
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="audit_{patient_id}.pdf"'},
    )


@router.get("/download-report/{patient_id}")
async def download_report(patient_id: str, db: AsyncSession = Depends(get_session)):
    """
    Returns the CrossCare drug interaction report PDF for download. Checks
    the in-memory hot cache first, then falls back to the most recent
    SQLite record so downloads survive a server restart.
    """
    result = _crosscare_results.get(patient_id)
    if not result or not result.get("drug_report_pdf_base64"):
        query = (
            select(InteractionResultRecord)
            .where(InteractionResultRecord.patient_id == patient_id)
            .order_by(InteractionResultRecord.created_at.desc())
            .limit(1)
        )
        record = (await db.execute(query)).scalar_one_or_none()
        result = record.result if record else None

    if not result or not result.get("drug_report_pdf_base64"):
        raise HTTPException(status_code=404, detail="No drug interaction report available for this patient")

    pdf_bytes = base64.b64decode(result["drug_report_pdf_base64"])
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="drug_report_{patient_id}.pdf"'},
    )


@router.get("/health")
async def health_check():
    return {"status": "ok"}
