# Converts simulated patient JSON / OCR prescription output into simplified
# FHIR-style resources (Patient, MedicationStatement) for downstream agents.

from typing import Any


def vitals_to_fhir_observation(patient_id: str, vitals: dict) -> dict:
    """Wraps raw vitals into a minimal FHIR Observation resource."""
    return {
        "resourceType": "Observation",
        "status": "final",
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectiveDateTime": vitals.get("timestamp"),
        "component": [
            {"code": {"text": "heart_rate"}, "valueQuantity": {"value": vitals.get("heart_rate")}},
            {"code": {"text": "blood_pressure_systolic"}, "valueQuantity": {"value": vitals.get("blood_pressure_systolic")}},
            {"code": {"text": "blood_pressure_diastolic"}, "valueQuantity": {"value": vitals.get("blood_pressure_diastolic")}},
            {"code": {"text": "temperature"}, "valueQuantity": {"value": vitals.get("temperature")}},
            {"code": {"text": "respiratory_rate"}, "valueQuantity": {"value": vitals.get("respiratory_rate")}},
            {"code": {"text": "lactate"}, "valueQuantity": {"value": vitals.get("lactate")}},
            {"code": {"text": "wbc_count"}, "valueQuantity": {"value": vitals.get("wbc_count")}},
        ],
    }


def prescription_to_fhir_medication_statements(patient_id: str, medicines: list[str], dosages: list[str]) -> list[dict]:
    """Wraps a list of medicine/dosage pairs into FHIR MedicationStatement resources."""
    statements = []
    for medicine, dosage in zip(medicines, dosages):
        statements.append(
            {
                "resourceType": "MedicationStatement",
                "status": "active",
                "subject": {"reference": f"Patient/{patient_id}"},
                "medicationCodeableConcept": {"text": medicine},
                "dosage": [{"text": dosage}],
            }
        )
    return statements


def extract_medicine_dosage_pairs(ocr_text: str) -> list[dict[str, Any]]:
    """
    Very lightweight parser that splits OCR'd prescription text into
    medicine/dosage line items. Expects lines like "Amoxicillin 500mg".
    """
    pairs = []
    for line in ocr_text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(" ", 1)
        medicine = parts[0]
        dosage = parts[1] if len(parts) > 1 else ""
        pairs.append({"medicine": medicine, "dosage": dosage})
    return pairs
