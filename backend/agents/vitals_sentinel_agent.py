# Agent 1 — Vitals Sentinel Agent.
# Reads patient vitals every 30 seconds, calculates the qSOFA score, and
# triggers a Sepsis Alert into the SepsisGuard LangGraph workflow when thresholds are crossed.

import os
from datetime import datetime, timezone

from langchain_groq import ChatGroq

from graph.state import SepsisGuardState
from models.schemas import PatientVitals
from prompts.vitals_prompt import VITALS_SENTINEL_PROMPT
from tools.sofa_calculator import calculate_qsofa, classify_severity

llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=os.getenv("GROQ_API_KEY"))


def run(state: SepsisGuardState) -> SepsisGuardState:
    vitals = PatientVitals(**state["vitals"])

    qsofa_score = calculate_qsofa(vitals)
    severity = classify_severity(qsofa_score, vitals.lactate)

    sepsis_alert = None
    if qsofa_score >= 2:
        # Ask the LLM for a short clinical rationale to attach to the alert.
        response = llm.invoke(
            [
                ("system", VITALS_SENTINEL_PROMPT),
                ("human", f"Vitals: {vitals.model_dump()}\nqSOFA score: {qsofa_score}\nSeverity: {severity}"),
            ]
        )
        sepsis_alert = {
            "patient_id": vitals.patient_id,
            "qsofa_score": qsofa_score,
            "severity": severity,
            "triggered_at": datetime.now(timezone.utc).isoformat(),
            "vitals": vitals.model_dump(),
            "rationale": response.content,
        }

    return {
        **state,
        "qsofa_score": qsofa_score,
        "severity": severity,
        "sepsis_alert": sepsis_alert,
    }
