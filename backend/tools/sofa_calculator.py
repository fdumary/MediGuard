# Computes the bedside qSOFA (quick Sequential Organ Failure Assessment) score
# used by the Vitals Sentinel Agent to decide whether to trigger a sepsis alert.

from models.schemas import PatientVitals


def calculate_qsofa(vitals: PatientVitals) -> int:
    """
    qSOFA awards 1 point each for:
      - Respiratory rate >= 22 breaths/min
      - Systolic blood pressure <= 100 mmHg
      - Altered mentation (not modeled here, vitals-only proxy uses temperature/HR)
    A score >= 2 indicates a high risk of sepsis-related mortality.
    """
    score = 0

    if vitals.respiratory_rate >= 22:
        score += 1

    if vitals.blood_pressure_systolic <= 100:
        score += 1

    # Proxy for altered mentation: extreme tachycardia + fever/hypothermia
    if vitals.heart_rate >= 130 or vitals.temperature >= 39.0 or vitals.temperature <= 35.0:
        score += 1

    return score


def classify_severity(qsofa_score: int, lactate: float) -> str:
    """Maps qSOFA + lactate into a human-readable severity bucket for alerts."""
    if qsofa_score >= 3 or lactate >= 4.0:
        return "critical"
    if qsofa_score == 2 or lactate >= 2.0:
        return "severe"
    if qsofa_score == 1:
        return "moderate"
    return "mild"
