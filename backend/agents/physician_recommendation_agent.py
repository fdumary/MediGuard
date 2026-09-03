# Agent 8 — Physician Recommendation Agent.
# Suggests a concrete, actionable plan for every flagged risk (never just
# "monitor"), writes everything in plain language, builds the final
# medication timeline for the patient, renders a polished PDF report
# addressed to the prescribing doctor via the Nutrient Processor API, and
# generates a structured signed document of the same report via Doctavian.
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

llm = ChatGroq(model="qwen/qwen3.8-27b", groq_api_key=os.getenv("GROQ_API_KEY") or "gsk_placeholder")


class MedicationPlanItem(BaseModel):
    drug: str = Field(description="Medication name (kept, dose-adjusted, or substituted)")
    dosage: str = Field(description="Dosage and route, e.g. '2.5mg, oral'")
    timing: str = Field(description="Concrete schedule the patient can follow, e.g. 'Mornings with food, starting today'")
    notes: str = Field(default="", description="One short plain-language note, e.g. why this changed or what to watch for")


class PhysicianRecommendation(BaseModel):
    recommendations: list[str] = Field(
        description="Plain-language, actionable recommendations, one per flagged risk. Each must include a "
        "concrete substitute, dose change, or monitoring schedule — never just 'monitor closely'"
    )
    medication_plan: list[MedicationPlanItem] = Field(
        description="The final medication plan for this patient going forward: every drug, dose, and schedule"
    )
    clinical_note: str = Field(description="Plain-language note explaining the risk and the plan, understandable to a patient's family")
    alert_message: str = Field(description="Short alert message to send to the prescribing doctors")


structured_llm = llm.with_structured_output(PhysicianRecommendation)

RISK_COLORS = {
    "critical": ("#ef4444", "#fef2f2"),
    "high": ("#f97316", "#fff7ed"),
    "medium": ("#eab308", "#fefce8"),
    "low": ("#22c55e", "#f0fdf4"),
}


def _render_report_html(state: CrossCareState, recommendation: "PhysicianRecommendation") -> str:
    """Renders a polished, letterhead-style drug interaction report as HTML for Nutrient to convert into a PDF."""
    patient_name = state.get("patient_name") or state.get("patient_id", "Unknown Patient")
    doctor_name = state.get("doctor_name") or "Prescribing Physician"
    risk_level = (state.get("risk_level") or "unknown").lower()
    accent, tint = RISK_COLORS.get(risk_level, ("#64748b", "#f8fafc"))

    combos_html = "".join(
        f'<li>{c}</li>' for c in state.get("dangerous_combinations", [])
    ) or "<li>None detected</li>"

    recs_html = "".join(f'<li>{r}</li>' for r in recommendation.recommendations) or "<li>None</li>"

    plan_rows = "".join(
        f"""<tr>
              <td class="drug">{item.drug}</td>
              <td>{item.dosage}</td>
              <td>{item.timing}</td>
              <td class="notes">{item.notes}</td>
            </tr>"""
        for item in recommendation.medication_plan
    ) or '<tr><td colspan="4" class="empty">No medication plan generated.</td></tr>'

    return f"""
    <html>
      <head>
        <style>
          * {{ box-sizing: border-box; }}
          body {{ font-family: 'Helvetica Neue', Arial, sans-serif; color: #1e293b; margin: 0; padding: 0; }}
          .header {{ background: linear-gradient(135deg, #0f172a, #1e3a5f); color: white; padding: 32px 40px; }}
          .header .brand {{ font-size: 13px; letter-spacing: 2px; text-transform: uppercase; color: #5eead4; font-weight: 600; }}
          .header h1 {{ margin: 6px 0 0; font-size: 24px; }}
          .header .sub {{ margin-top: 4px; color: #cbd5e1; font-size: 13px; }}
          .body {{ padding: 32px 40px; }}
          .info-grid {{ display: flex; gap: 24px; margin-bottom: 24px; }}
          .info-box {{ flex: 1; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px 16px; }}
          .info-box .label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #64748b; font-weight: 600; }}
          .info-box .value {{ font-size: 15px; font-weight: 700; margin-top: 2px; }}
          .salutation {{ font-size: 14px; margin: 20px 0 8px; }}
          .risk-banner {{ background: {tint}; border: 1px solid {accent}; border-left: 6px solid {accent}; border-radius: 8px; padding: 14px 18px; margin: 18px 0; }}
          .risk-banner .risk-label {{ color: {accent}; font-weight: 800; text-transform: uppercase; font-size: 13px; letter-spacing: 1px; }}
          h2 {{ font-size: 15px; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; margin-top: 28px; }}
          ul {{ margin: 10px 0; padding-left: 20px; font-size: 13px; line-height: 1.6; }}
          table {{ width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; }}
          th {{ background: #0f172a; color: white; text-align: left; padding: 10px 12px; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; }}
          td {{ padding: 10px 12px; border-bottom: 1px solid #e2e8f0; vertical-align: top; }}
          tr:nth-child(even) td {{ background: #f8fafc; }}
          td.drug {{ font-weight: 700; }}
          td.notes {{ color: #64748b; font-size: 12px; }}
          td.empty {{ text-align: center; color: #94a3b8; padding: 20px; }}
          .note-box {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; font-size: 13px; line-height: 1.6; margin-top: 10px; }}
          .footer {{ margin-top: 40px; padding-top: 16px; border-top: 1px solid #e2e8f0; font-size: 11px; color: #94a3b8; }}
        </style>
      </head>
      <body>
        <div class="header">
          <div class="brand">MediGuard &middot; CrossCare</div>
          <h1>Drug Interaction &amp; Recommendation Report</h1>
          <div class="sub">Generated by the CrossCare autonomous agent pipeline</div>
        </div>
        <div class="body">
          <div class="info-grid">
            <div class="info-box">
              <div class="label">Patient</div>
              <div class="value">{patient_name}</div>
            </div>
            <div class="info-box">
              <div class="label">Patient ID</div>
              <div class="value">{state.get('patient_id', '—')}</div>
            </div>
            <div class="info-box">
              <div class="label">Risk Level</div>
              <div class="value" style="color: {accent};">{risk_level.upper()}</div>
            </div>
          </div>

          <p class="salutation">Dear Dr. {doctor_name},</p>
          <p style="font-size: 13px; line-height: 1.6;">
            CrossCare reviewed {patient_name}'s current medications and found the findings below.
            Please review the recommended plan and confirm before it is applied.
          </p>

          <div class="risk-banner">
            <div class="risk-label">{risk_level} risk</div>
            <ul style="margin-bottom: 0;">{combos_html}</ul>
          </div>

          <h2>Recommendations</h2>
          <ul>{recs_html}</ul>

          <h2>Recommended Medication Plan &amp; Timeline</h2>
          <table>
            <thead>
              <tr><th>Medication</th><th>Dosage</th><th>Timing</th><th>Notes</th></tr>
            </thead>
            <tbody>{plan_rows}</tbody>
          </table>

          <h2>Clinical Note</h2>
          <div class="note-box">{recommendation.clinical_note}</div>

          <div class="footer">
            This report was generated by MediGuard's autonomous CrossCare pipeline and is intended to support,
            not replace, clinical judgment. Please review and co-sign before acting on this plan.
          </div>
        </div>
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
                f"Patient: {state.get('patient_name') or state.get('patient_id')}\n"
                f"Current medicines: {state.get('medicines')}\n"
                f"Dosages: {state.get('dosages')}\n"
                f"Dangerous combinations: {dangerous_combinations}\n"
                f"Risk level: {state.get('risk_level')}\n"
                f"Kidney risk: {state.get('kidney_risk')}, Heart risk: {state.get('heart_risk')}\n"
                f"Candidate RxNorm alternatives: {candidate_alternatives}\n\n"
                "Give a concrete, actionable recommendation for every flagged risk (never just 'monitor'), "
                "in plain language, and build the full medication plan/timeline for this patient.",
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
        "medication_plan": [item.model_dump() for item in recommendation.medication_plan],
        "clinical_note": recommendation.clinical_note,
        "alert_message": recommendation.alert_message,
        "drug_report_pdf_base64": drug_report_pdf_base64,
        "doctavian_document": doctavian_document,
    }
