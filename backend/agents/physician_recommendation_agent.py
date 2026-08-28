# Agent 8 — Physician Recommendation Agent.
# Suggests safe alternative medicines, writes a clinical note for the doctor,
# and drafts the alert sent to all prescribing physicians.

import os

from langchain_groq import ChatGroq

from graph.state import CrossCareState
from prompts.recommendation_prompt import PHYSICIAN_RECOMMENDATION_PROMPT
from tools.rxnorm_api_tool import find_alternatives

llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=os.getenv("GROQ_API_KEY"))


def run(state: CrossCareState) -> CrossCareState:
    dangerous_combinations = state.get("dangerous_combinations", [])

    recommendations = []
    for combo in dangerous_combinations:
        drug_name = combo.split(" + ")[0]
        alternatives = find_alternatives(drug_name)
        if alternatives:
            recommendations.append(f"Consider replacing {drug_name} with {alternatives[0]}")

    response = llm.invoke(
        [
            ("system", PHYSICIAN_RECOMMENDATION_PROMPT),
            (
                "human",
                f"Dangerous combinations: {dangerous_combinations}\n"
                f"Risk level: {state.get('risk_level')}\n"
                f"Candidate alternatives: {recommendations}",
            ),
        ]
    )

    return {
        **state,
        "recommendations": recommendations,
        "clinical_note": response.content,
    }
