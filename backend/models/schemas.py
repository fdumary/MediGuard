# Pydantic schemas shared across the SepsisGuard and CrossCare agent pipelines,
# the FastAPI routes, and the WebSocket broadcast payloads.

from typing import List
from pydantic import BaseModel


class PatientVitals(BaseModel):
    patient_id: str
    heart_rate: float
    blood_pressure_systolic: float
    blood_pressure_diastolic: float
    temperature: float
    respiratory_rate: float
    lactate: float
    wbc_count: float
    timestamp: str


class SepsisAlert(BaseModel):
    patient_id: str
    qsofa_score: int
    severity: str  # mild | moderate | severe | critical
    triggered_at: str
    vitals: PatientVitals


class TreatmentPlan(BaseModel):
    patient_id: str
    antibiotics: List[str]
    dosages: List[str]
    icu_bed_reserved: bool
    infusion_pump_reserved: bool
    approved: bool
    audit_log: str


class Prescription(BaseModel):
    patient_id: str
    doctor_name: str
    medicines: List[str]
    dosages: List[str]
    conditions: List[str]


class DrugInteractionResult(BaseModel):
    patient_id: str
    dangerous_combinations: List[str]
    risk_level: str  # low | medium | high | critical
    recommendations: List[str]
    clinical_note: str
