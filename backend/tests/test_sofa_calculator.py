# Regression tests for qSOFA scoring and severity classification against
# the 3 simulated patients shipped in data/simulated_patients.json.

from models.schemas import PatientVitals
from tools.sofa_calculator import calculate_qsofa, classify_severity


def _vitals(**overrides) -> PatientVitals:
    base = dict(
        patient_id="TEST",
        heart_rate=78,
        blood_pressure_systolic=118,
        blood_pressure_diastolic=76,
        temperature=36.8,
        respiratory_rate=16,
        lactate=1.1,
        wbc_count=7.2,
        timestamp="2026-01-01T00:00:00Z",
    )
    base.update(overrides)
    return PatientVitals(**base)


def test_healthy_patient_scores_zero():
    vitals = _vitals()
    assert calculate_qsofa(vitals) == 0
    assert classify_severity(0, vitals.lactate) == "mild"


def test_borderline_patient_p002():
    # Matches backend/data/simulated_patients.json patient P-002.
    vitals = _vitals(
        heart_rate=104, blood_pressure_systolic=98, blood_pressure_diastolic=64,
        temperature=38.1, respiratory_rate=20, lactate=2.3, wbc_count=13.5,
    )
    assert calculate_qsofa(vitals) == 1
    # Elevated lactate (>=2.0) pushes severity to "severe" even though
    # qSOFA alone is only 1 — this is qSOFA-plus-lactate combined logic,
    # not a qSOFA-only reading.
    assert classify_severity(1, vitals.lactate) == "severe"


def test_critical_patient_p003():
    # Matches backend/data/simulated_patients.json patient P-003.
    vitals = _vitals(
        heart_rate=132, blood_pressure_systolic=82, blood_pressure_diastolic=54,
        temperature=39.6, respiratory_rate=27, lactate=4.8, wbc_count=18.9,
    )
    assert calculate_qsofa(vitals) == 3
    assert classify_severity(3, vitals.lactate) == "critical"


def test_respiratory_rate_alone_scores_one_point():
    vitals = _vitals(respiratory_rate=22)
    assert calculate_qsofa(vitals) == 1


def test_hypotension_alone_scores_one_point():
    vitals = _vitals(blood_pressure_systolic=100)
    assert calculate_qsofa(vitals) == 1


def test_tachycardia_alone_scores_one_point():
    vitals = _vitals(heart_rate=130)
    assert calculate_qsofa(vitals) == 1


def test_hypothermia_scores_one_point():
    vitals = _vitals(temperature=35.0)
    assert calculate_qsofa(vitals) == 1


def test_critical_lactate_forces_critical_severity_even_at_low_qsofa():
    assert classify_severity(0, 4.5) == "critical"
