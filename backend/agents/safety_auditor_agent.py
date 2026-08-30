# Agent 5 — Safety Auditor Agent.
# Verifies Surviving Sepsis Campaign compliance, gives final approval before
# treatment is dispatched, writes the audit log entry, and generates a
# signed PDF audit report via the Nutrient Processor API.

import os
from datetime import datetime, timezone

from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from graph.state import SepsisGuardState
from models.schemas import TreatmentPlan
from prompts.auditor_prompt import SAFETY_AUDITOR_PROMPT
from tools.nutrient_tool import generate_pdf, sign_pdf

llm = ChatGroq(model="qwen/qwen3.8-27b", groq_api_key=os.getenv("GROQ_API_KEY"))


class ComplianceCheck(BaseModel):
    bundle_compliant: bool = Field(description="Whether the plan satisfies the Surviving Sepsis Campaign 1-hour bundle")
    violations: list[str] = Field(default_factory=list, description="Any compliance violations found")


structured_llm = llm.with_structured_output(ComplianceCheck)


def _render_audit_html(state: SepsisGuardState, approved: bool, violations: list[str], audit_log: str) -> str:
    """Renders the treatment plan + compliance result as HTML for Nutrient to convert into a PDF."""
    violations_html = "".join(f"<li>{v}</li>" for v in violations) or "<li>None</li>"
    return f"""
    <html>
      <body style="font-family: sans-serif;">
        <h1>MediGuard SepsisGuard — Audit Report</h1>
        <p><strong>Patient ID:</strong> {state.get('patient_id')}</p>
        <p><strong>Severity:</strong> {state.get('severity')}</p>
        <p><strong>Approved:</strong> {approved}</p>
        <h2>Antibiotics</h2>
        <p>{', '.join(state.get('antibiotics', [])) or 'None'}</p>
        <h2>Dosages</h2>
        <p>{', '.join(state.get('dosages', [])) or 'None'}</p>
        <h2>ICU Resources</h2>
        <p>Bed: {state.get('bed_id')} | Pump: {state.get('pump_id')}</p>
        <h2>Compliance Violations</h2>
        <ul>{violations_html}</ul>
        <h2>Audit Log</h2>
        <p>{audit_log}</p>
      </body>
    </html>
    """


def run(state: SepsisGuardState) -> SepsisGuardState:
    if not state.get("sepsis_alert"):
        return state

    check = structured_llm.invoke(
        [
            ("system", SAFETY_AUDITOR_PROMPT),
            (
                "human",
                f"Antibiotics: {state.get('antibiotics')}\n"
                f"Dosages: {state.get('dosages')}\n"
                f"Contraindication warnings: {state.get('contraindication_warnings')}\n"
                f"ICU bed reserved: {state.get('icu_bed_reserved')} ({state.get('bed_id')})\n"
                f"Infusion pump reserved: {state.get('infusion_pump_reserved')} ({state.get('pump_id')})",
            ),
        ]
    )

    approved = bool(
        check.bundle_compliant
        and not check.violations
        and state.get("icu_bed_reserved")
        and state.get("antibiotics")
    )

    audit_log = (
        f"[{datetime.now(timezone.utc).isoformat()}] Treatment plan for "
        f"{state.get('patient_id')} reviewed. Approved={approved}. "
        f"Violations={check.violations or 'none'}."
    )

    # Generate the audit PDF, then sign it. Either step can return None
    # (unconfigured key or a failed call) without raising — the pipeline
    # keeps running and the plan is still approved/rejected on its own
    # merits; only the PDF artifact is missing, flagged via a warning.
    signed_audit_pdf_base64 = None
    nutrient_warning = None
    audit_html = _render_audit_html(state, approved, check.violations, audit_log)
    unsigned_pdf_base64 = generate_pdf(audit_html)
    if unsigned_pdf_base64:
        signed_audit_pdf_base64 = sign_pdf(unsigned_pdf_base64)
        if not signed_audit_pdf_base64:
            nutrient_warning = "Nutrient generated the audit PDF but signing failed; using unsigned PDF."
            signed_audit_pdf_base64 = unsigned_pdf_base64
    else:
        nutrient_warning = "Nutrient PDF generation unavailable; audit report was not produced."

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
        "compliance_violations": check.violations,
        "audit_log": audit_log,
        "treatment_plan": treatment_plan.model_dump(),
        "signed_audit_pdf_base64": signed_audit_pdf_base64,
        "audit_pdf_signed": bool(signed_audit_pdf_base64) and nutrient_warning is None,
        "nutrient_warning": nutrient_warning,
    }
