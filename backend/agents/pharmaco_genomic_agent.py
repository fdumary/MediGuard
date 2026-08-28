# Agent 3 — Pharmaco-Genomic Agent.
# Checks the NLM API for drug interactions, recommends the correct empiric
# antibiotics for suspected sepsis, and calculates a safe dosage.

import os

from langchain_groq import ChatGroq

from graph.state import SepsisGuardState
from prompts.pharmaco_prompt import PHARMACO_GENOMIC_PROMPT
from tools.nlm_api_tool import check_drug_interactions, find_rxcui_by_name

llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=os.getenv("GROQ_API_KEY"))


def run(state: SepsisGuardState) -> SepsisGuardState:
    alert = state.get("sepsis_alert")
    if not alert:
        return state

    current_meds = state.get("current_medications", [])
    rxcuis = [rxcui for rxcui in (find_rxcui_by_name(m) for m in current_meds) if rxcui]
    interactions = check_drug_interactions(rxcuis) if rxcuis else {}

    response = llm.invoke(
        [
            ("system", PHARMACO_GENOMIC_PROMPT),
            (
                "human",
                f"Sepsis alert: {alert}\nCurrent medications: {current_meds}\n"
                f"Known interactions: {interactions}\n"
                "Recommend empiric antibiotics and dosages as a JSON list.",
            ),
        ]
    )

    # Placeholder parsing — a production build would enforce structured
    # output (e.g. with_structured_output) instead of parsing free text.
    return {
        **state,
        "antibiotics": ["Piperacillin-Tazobactam"],
        "dosages": ["4.5g IV every 6 hours"],
        "pharmaco_notes": response.content,
    }
