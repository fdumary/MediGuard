# Shared LangGraph state objects passed between agent nodes in both the
# SepsisGuard and CrossCare workflows.

from typing import Optional, TypedDict


class SepsisGuardState(TypedDict, total=False):
    patient_id: str
    patient_name: str
    vitals: dict
    current_medications: list[str]
    qsofa_score: int
    severity: str
    sepsis_alert: Optional[dict]
    suspected_infection_source: str
    recommended_actions: list[str]
    strategy_summary: str
    priority_actions: list[str]
    antibiotics: list[str]
    dosages: list[str]
    contraindication_warnings: list[str]
    icu_bed_reserved: bool
    infusion_pump_reserved: bool
    bed_id: str
    pump_id: str
    nursing_message: str
    approved: bool
    compliance_violations: list[str]
    audit_log: str
    treatment_plan: Optional[dict]
    signed_audit_pdf_base64: Optional[str]
    audit_pdf_signed: bool
    nutrient_warning: Optional[str]


class CrossCareState(TypedDict, total=False):
    patient_id: str
    patient_name: str
    doctor_name: str
    raw_prescriptions: list[dict]
    ocr_text: list[str]
    prescription_pdf_base64: Optional[str]
    extracted_prescription_data: Optional[dict]
    medicines: list[str]
    dosages: list[str]
    ingestion_notes: str
    fhir_medications: list[dict]
    dangerous_combinations: list[str]
    kidney_risk: bool
    heart_risk: bool
    risk_level: str
    recommendations: list[str]
    medication_plan: list[dict]
    clinical_note: str
    alert_message: str
    drug_report_pdf_base64: Optional[str]
    doctavian_document: Optional[dict]
