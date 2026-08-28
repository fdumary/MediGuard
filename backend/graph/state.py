# Shared LangGraph state objects passed between agent nodes in both the
# SepsisGuard and CrossCare workflows.

from typing import Optional, TypedDict


class SepsisGuardState(TypedDict, total=False):
    patient_id: str
    vitals: dict
    qsofa_score: int
    severity: str
    sepsis_alert: Optional[dict]
    antibiotics: list[str]
    dosages: list[str]
    icu_bed_reserved: bool
    infusion_pump_reserved: bool
    approved: bool
    audit_log: str
    treatment_plan: Optional[dict]


class CrossCareState(TypedDict, total=False):
    patient_id: str
    raw_prescriptions: list[dict]
    ocr_text: list[str]
    medicines: list[str]
    dosages: list[str]
    fhir_medications: list[dict]
    dangerous_combinations: list[str]
    risk_level: str
    recommendations: list[str]
    clinical_note: str
