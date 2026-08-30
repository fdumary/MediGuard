# Agent 7 — Pharmacology Interaction Agent.
# Cross-checks all drugs on a patient's aggregated prescription list via the
# RxNorm API, detects dangerous combinations, and flags kidney/heart risks.

import os

from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from graph.state import CrossCareState
from prompts.interaction_prompt import PHARMACOLOGY_INTERACTION_PROMPT
from tools.rxnorm_api_tool import check_interaction_pair, get_drug_details

llm = ChatGroq(model="qwen/qwen3.8-27b", groq_api_key=os.getenv("GROQ_API_KEY"))


class InteractionAssessment(BaseModel):
    additional_dangerous_combinations: list[str] = Field(
        default_factory=list,
        description="Any clinically dangerous combinations not already caught by the RxNorm pairwise check, "
        "formatted as 'DrugA + DrugB'",
    )
    kidney_risk: bool = Field(description="Whether the combined medication list poses a cumulative kidney risk")
    heart_risk: bool = Field(description="Whether the combined medication list poses a cumulative heart risk")
    risk_level: str = Field(description="Overall risk level: low, medium, high, or critical")


structured_llm = llm.with_structured_output(InteractionAssessment)


def run(state: CrossCareState) -> CrossCareState:
    medicines = state.get("medicines", [])

    drug_details = [get_drug_details(m) for m in medicines]

    # RxNorm pairwise interaction sweep across the medicine list.
    rxnorm_combinations = []
    rxcuis = [d.get("idGroup", {}).get("rxnormId", [None])[0] for d in drug_details if isinstance(d, dict)]
    for i in range(len(rxcuis)):
        for j in range(i + 1, len(rxcuis)):
            if rxcuis[i] and rxcuis[j]:
                result = check_interaction_pair(rxcuis[i], rxcuis[j])
                if result.get("fullInteractionTypeGroup"):
                    rxnorm_combinations.append(f"{medicines[i]} + {medicines[j]}")

    assessment = structured_llm.invoke(
        [
            ("system", PHARMACOLOGY_INTERACTION_PROMPT),
            (
                "human",
                f"Medicines: {medicines}\n"
                f"Combinations already flagged by RxNorm: {rxnorm_combinations}\n"
                "Assess cumulative kidney/heart risk and flag any additional dangerous combinations.",
            ),
        ]
    )

    dangerous_combinations = sorted(set(rxnorm_combinations) | set(assessment.additional_dangerous_combinations))

    return {
        **state,
        "dangerous_combinations": dangerous_combinations,
        "kidney_risk": assessment.kidney_risk,
        "heart_risk": assessment.heart_risk,
        "risk_level": assessment.risk_level,
    }
