# Tests for the FHIR conversion helpers used by the Prescription Ingestion
# Agent and the Vitals Sentinel Agent.

from tools.fhir_parser import (
    extract_medicine_dosage_pairs,
    prescription_to_fhir_medication_statements,
    vitals_to_fhir_observation,
)


def test_extract_medicine_dosage_pairs_basic():
    pairs = extract_medicine_dosage_pairs("Warfarin 5mg once daily\nAspirin 100mg once daily")
    assert pairs == [
        {"medicine": "Warfarin", "dosage": "5mg once daily"},
        {"medicine": "Aspirin", "dosage": "100mg once daily"},
    ]


def test_extract_medicine_dosage_pairs_ignores_blank_lines():
    pairs = extract_medicine_dosage_pairs("Metformin 500mg\n\n\nInsulin 10 units")
    assert len(pairs) == 2
    assert pairs[0]["medicine"] == "Metformin"
    assert pairs[1]["medicine"] == "Insulin"


def test_extract_medicine_dosage_pairs_handles_medicine_only_line():
    pairs = extract_medicine_dosage_pairs("Ibuprofen")
    assert pairs == [{"medicine": "Ibuprofen", "dosage": ""}]


def test_extract_medicine_dosage_pairs_empty_input():
    assert extract_medicine_dosage_pairs("") == []


def test_prescription_to_fhir_medication_statements():
    statements = prescription_to_fhir_medication_statements(
        "P-003", ["Warfarin", "Amiodarone"], ["5mg daily", "200mg daily"]
    )
    assert len(statements) == 2
    assert statements[0]["resourceType"] == "MedicationStatement"
    assert statements[0]["subject"]["reference"] == "Patient/P-003"
    assert statements[0]["medicationCodeableConcept"]["text"] == "Warfarin"
    assert statements[0]["dosage"][0]["text"] == "5mg daily"


def test_prescription_to_fhir_medication_statements_mismatched_lengths_truncates():
    # zip() truncates to the shorter list rather than raising — verify
    # that's still the actual (safe) behavior.
    statements = prescription_to_fhir_medication_statements(
        "P-003", ["Warfarin", "Amiodarone"], ["5mg daily"]
    )
    assert len(statements) == 1


def test_vitals_to_fhir_observation():
    vitals = {
        "heart_rate": 130,
        "blood_pressure_systolic": 80,
        "blood_pressure_diastolic": 50,
        "temperature": 39.8,
        "respiratory_rate": 28,
        "lactate": 4.5,
        "wbc_count": 18.0,
        "timestamp": "2026-08-30T10:00:00Z",
    }
    observation = vitals_to_fhir_observation("P-003", vitals)
    assert observation["resourceType"] == "Observation"
    assert observation["subject"]["reference"] == "Patient/P-003"
    assert observation["effectiveDateTime"] == "2026-08-30T10:00:00Z"
    component_codes = {c["code"]["text"] for c in observation["component"]}
    assert component_codes == {
        "heart_rate", "blood_pressure_systolic", "blood_pressure_diastolic",
        "temperature", "respiratory_rate", "lactate", "wbc_count",
    }
