# REST API routes for MediGuard: patient vitals ingestion (SepsisGuard) and
# prescription submission (CrossCare), each triggering their LangGraph workflow.

import json
from pathlib import Path

from fastapi import APIRouter

from api.websocket import manager
from graph.crosscare_workflow import crosscare_app
from graph.sepsisguard_workflow import sepsisguard_app
from models.schemas import PatientVitals, Prescription

router = APIRouter()

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@router.get("/patients")
async def list_patients():
    with open(DATA_DIR / "simulated_patients.json") as f:
        return json.load(f)


@router.post("/sepsisguard/vitals")
async def submit_vitals(vitals: PatientVitals):
    """Feeds a vitals reading into the SepsisGuard LangGraph pipeline."""
    result = sepsisguard_app.invoke({"patient_id": vitals.patient_id, "vitals": vitals.model_dump()})
    if result.get("sepsis_alert"):
        await manager.broadcast({"type": "sepsis_alert", "data": result})
    return result


@router.post("/crosscare/prescriptions")
async def submit_prescription(prescription: Prescription):
    """Feeds a new prescription into the CrossCare LangGraph pipeline."""
    result = crosscare_app.invoke(
        {
            "patient_id": prescription.patient_id,
            "ocr_text": [],
            "medicines": prescription.medicines,
            "dosages": prescription.dosages,
        }
    )
    await manager.broadcast({"type": "drug_interaction_result", "data": result})
    return result


@router.get("/health")
async def health_check():
    return {"status": "ok"}
