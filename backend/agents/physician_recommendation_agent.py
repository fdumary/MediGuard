# Agent 8 — Physician Recommendation Agent.
# Suggests safe alternative medicines, writes a clinical note for the doctor,
# drafts the alert sent to all prescribing physicians, renders the drug
# interaction report as a PDF via the Nutrient Processor API, and generates
# a structured signed document of the same report via Doctavian.
#
# NOTE: Doctavian was briefly removed (2026-08-30) when no credentials had
# been issued; a demo key arrived shortly after and it's back. Its request
# shape is still unverified pending real docs — see tools/doctavian_tool.py.

import os

from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from graph.state import CrossCareState
from prompts.recommendation_prompt import PHYSICIAN_RECOMMENDATION_PROMPT
from tools.doctavian_tool import generate_drug_interaction_document
from tools.nutrient_tool import generate_pdf
from tools.rxnorm_api_tool import find_alternatives

llm = ChatGroq(model="qwen/qwen3.8-27b", groq_api_key=os.getenv("GROQ_API_KEY"))


class PhysicianRecommendation(BaseModel):
    recommendations: list[str] = Field(description="Actionable recommendations, one per flagged risk")
    clinical_note: str = Field(description="Concise clinical note explaining the risk and suggested change")
    alert_message: str = Field(description="Short alert message to send to the prescribing doctors")


structured_llm = llm.with_structured_output(PhysicianRecommendation)


def _render_report_html(state: CrossCareState, recommendation: "PhysicianRecommendation") -> str:
    """Renders the drug interaction findings as HTML for Nutrient to convert into a PDF."""
    combos_html = "".join(f"<li>{c}</li>" for c in state.get("dangerous_combinations", [])) or "<li>None</li>"
    recs_html = "".join(f"<li>{r}</li>" for r in recommendation.recommendations) or "<li>None</li>"
    return f"""
    <html>
      <body style="font-family: sans-serif;">
        <h1>MediGuard CrossCare — Drug Interaction Report</h1>
        <p><strong>Patient ID:</strong> {state.get('patient_id')}</p>
        <p><strong>Risk Level:</strong> {state.get('risk_level')}</p>
        <p><strong>Kidney Risk:</strong> {state.get('kidney_risk')} | <strong>Heart Risk:</strong> {state.get('heart_risk')}</p>
        <h2>Dangerous Combinations</h2>
        <ul>{combos_html}</ul>
        <h2>Recommendations</h2>
        <ul>{recs_html}</ul>
        <h2>Clinical Note</h2>
        <p>{recommendation.clinical_note}</p>
      </body>
    </html>
    """


def run(state: CrossCareState) -> CrossCareState:
    dangerous_combinations = state.get("dangerous_combinations", [])

    candidate_alternatives = []
    for combo in dangerous_combinations:
        drug_name = combo.split(" + ")[0]
        alternatives = find_alternatives(drug_name)
        if alternatives:
            candidate_alternatives.append(f"{drug_name} -> {alternatives[0]}")

    recommendation = structured_llm.invoke(
        [
            ("system", PHYSICIAN_RECOMMENDATION_PROMPT),
            (
                "human",
                f"Dangerous combinations: {dangerous_combinations}\n"
                f"Risk level: {state.get('risk_level')}\n"
                f"Kidney risk: {state.get('kidney_risk')}, Heart risk: {state.get('heart_risk')}\n"
                f"Candidate RxNorm alternatives: {candidate_alternatives}",
            ),
        ]
    )

    # PDF generation failures never break the pipeline — the recommendation
    # text/alert is already built above regardless of whether the report
    # PDF renders successfully.
    drug_report_pdf_base64 = generate_pdf(_render_report_html(state, recommendation))

    doctavian_document = generate_drug_interaction_document(
        patient_id=state["patient_id"],
        dangerous_combinations=dangerous_combinations,
        recommendations=recommendation.recommendations,
        clinical_note=recommendation.clinical_note,
    )

    return {
        **state,
        "recommendations": recommendation.recommendations,
        "clinical_note": recommendation.clinical_note,
        "alert_message": recommendation.alert_message,
        "drug_report_pdf_base64": drug_report_pdf_base64,
        "doctavian_document": doctavian_document,
    }
