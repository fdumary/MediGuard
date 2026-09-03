# Agent 1 — Vitals Sentinel Agent.
# Reads patient vitals every 30 seconds, calculates the qSOFA score, and
# triggers a Sepsis Alert into the SepsisGuard LangGraph workflow when thresholds are crossed.

import os
from datetime import datetime, timezone

from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from graph.state import SepsisGuardState
from models.schemas import PatientVitals
from prompts.vitals_prompt import VITALS_SENTINEL_PROMPT
from tools.sofa_calculator import calculate_qsofa, classify_severity

llm = ChatGroq(model="qwen/qwen3.8-27b", groq_api_key=os.getenv("GROQ_API_KEY") or "gsk_placeholder")


class VitalsAssessment(BaseModel):
    rationale: str = Field(description="One or two sentence clinical rationale a nurse can read in seconds")
    suspected_infection_source: str = Field(
        description="Best-guess infection source (e.g. urinary, respiratory, abdominal, skin/soft-tissue, unknown) inferred from the vitals pattern"
    )
    recommended_actions: list[str] = Field(
        description="Immediate next actions, e.g. 'draw blood cultures', 'start IV fluids'"
    )


structured_llm = llm.with_structured_output(VitalsAssessment)


def run(state: SepsisGuardState) -> SepsisGuardState:
    vitals = PatientVitals(**state["vitals"])

    qsofa_score = calculate_qsofa(vitals)
    severity = classify_severity(qsofa_score, vitals.lactate)

    sepsis_alert = None
    suspected_infection_source = ""
    recommended_actions: list[str] = []

    if qsofa_score >= 2:
        assessment = structured_llm.invoke(
            [
                ("system", VITALS_SENTINEL_PROMPT),
                (
                    "human",
                    f"Vitals: {vitals.model_dump()}\nqSOFA score: {qsofa_score}\nSeverity: {severity}",
                ),
            ]
        )
        suspected_infection_source = assessment.suspected_infection_source
        recommended_actions = assessment.recommended_actions

        sepsis_alert = {
            "patient_id": vitals.patient_id,
            "qsofa_score": qsofa_score,
            "severity": severity,
            "triggered_at": datetime.now(timezone.utc).isoformat(),
            "vitals": vitals.model_dump(),
            "rationale": assessment.rationale,
        }

    return {
        **state,
        "qsofa_score": qsofa_score,
        "severity": severity,
        "sepsis_alert": sepsis_alert,
        "suspected_infection_source": suspected_infection_source,
        "recommended_actions": recommended_actions,
    }
