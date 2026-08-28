# Agent 7 — Pharmacology Interaction Agent.
# Cross-checks all drugs on a patient's aggregated prescription list via the
# RxNorm API, detects dangerous combinations, and flags kidney/heart risks.

import os

from langchain_groq import ChatGroq

from graph.state import CrossCareState
from prompts.interaction_prompt import PHARMACOLOGY_INTERACTION_PROMPT
from tools.rxnorm_api_tool import check_interaction_pair, get_drug_details

llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=os.getenv("GROQ_API_KEY"))


def run(state: CrossCareState) -> CrossCareState:
    medicines = state.get("medicines", [])

    drug_details = [get_drug_details(m) for m in medicines]

    # Naive pairwise interaction sweep across the medicine list.
    dangerous_combinations = []
    rxcuis = [d.get("idGroup", {}).get("rxnormId", [None])[0] for d in drug_details if isinstance(d, dict)]
    for i in range(len(rxcuis)):
        for j in range(i + 1, len(rxcuis)):
            if rxcuis[i] and rxcuis[j]:
                result = check_interaction_pair(rxcuis[i], rxcuis[j])
                if result.get("fullInteractionTypeGroup"):
                    dangerous_combinations.append(f"{medicines[i]} + {medicines[j]}")

    response = llm.invoke(
        [
            ("system", PHARMACOLOGY_INTERACTION_PROMPT),
            (
                "human",
                f"Medicines: {medicines}\nDetected dangerous combinations: {dangerous_combinations}",
            ),
        ]
    )

    risk_level = "critical" if len(dangerous_combinations) >= 2 else "high" if dangerous_combinations else "low"

    return {
        **state,
        "dangerous_combinations": dangerous_combinations,
        "risk_level": risk_level,
        "interaction_notes": response.content,
    }
