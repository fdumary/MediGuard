# Tests for Pydantic request/response schema behavior.

import pytest
from pydantic import ValidationError

from models.schemas import PatientVitals, Prescription


def test_patient_vitals_current_medications_defaults_to_empty_list():
    vitals = PatientVitals(
        patient_id="P-001",
        heart_rate=78,
        blood_pressure_systolic=118,
        blood_pressure_diastolic=76,
        temperature=36.8,
        respiratory_rate=16,
        lactate=1.1,
        wbc_count=7.2,
        timestamp="2026-01-01T00:00:00Z",
    )
    assert vitals.current_medications == []


def test_patient_vitals_accepts_current_medications():
    vitals = PatientVitals(
        patient_id="P-003",
        heart_rate=130,
        blood_pressure_systolic=80,
        blood_pressure_diastolic=50,
        temperature=39.8,
        respiratory_rate=28,
        lactate=4.5,
        wbc_count=18.0,
        timestamp="2026-08-30T10:00:00Z",
        current_medications=["Warfarin", "Digoxin"],
    )
    assert vitals.current_medications == ["Warfarin", "Digoxin"]


def test_patient_vitals_missing_required_field_raises():
    with pytest.raises(ValidationError):
        PatientVitals(patient_id="P-001")


def test_prescription_requires_all_fields():
    prescription = Prescription(
        patient_id="P-003",
        doctor_name="Dr. Patel",
        medicines=["Warfarin"],
        dosages=["5mg daily"],
        conditions=["Atrial fibrillation"],
    )
    assert prescription.patient_id == "P-003"

    with pytest.raises(ValidationError):
        Prescription(patient_id="P-003", doctor_name="Dr. Patel")
