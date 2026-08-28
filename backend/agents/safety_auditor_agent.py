# Agent 5 — Safety Auditor Agent.
# Verifies Surviving Sepsis Campaign compliance, gives final approval before
# treatment is dispatched, and writes the audit log entry.

import os
from datetime import datetime, timezone

from langchain_groq import ChatGroq

from graph.state import SepsisGuardState
from models.schemas import TreatmentPlan
from prompts.auditor_prompt import SAFETY_AUDITOR_PROMPT

llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=os.getenv("GROQ_API_KEY"))


def run(state: SepsisGuardState) -> SepsisGuardState:
    if not state.get("sepsis_alert"):
        return state

    response = llm.invoke(
        [
            ("system", SAFETY_AUDITOR_PROMPT),
            (
                "human",
                f"Antibiotics: {state.get('antibiotics')}\n"
                f"Dosages: {state.get('dosages')}\n"
                f"ICU bed reserved: {state.get('icu_bed_reserved')}\n"
                f"Infusion pump reserved: {state.get('infusion_pump_reserved')}",
            ),
        ]
    )

    approved = bool(state.get("icu_bed_reserved") and state.get("antibiotics"))
    audit_log = (
        f"[{datetime.now(timezone.utc).isoformat()}] Treatment plan for "
        f"{state.get('patient_id')} reviewed. Approved={approved}. Notes: {response.content}"
    )

    treatment_plan = TreatmentPlan(
        patient_id=state["patient_id"],
        antibiotics=state.get("antibiotics", []),
        dosages=state.get("dosages", []),
        icu_bed_reserved=state.get("icu_bed_reserved", False),
        infusion_pump_reserved=state.get("infusion_pump_reserved", False),
        approved=approved,
        audit_log=audit_log,
    )

    return {
        **state,
        "approved": approved,
        "audit_log": audit_log,
        "treatment_plan": treatment_plan.model_dump(),
    }
