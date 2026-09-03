# Agent 3 — Pharmaco-Genomic Agent.
# Checks the NLM API for drug interactions, recommends the correct empiric
# antibiotics for suspected sepsis, and calculates a safe dosage.

import os

from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from graph.state import SepsisGuardState
from prompts.pharmaco_prompt import PHARMACO_GENOMIC_PROMPT
from tools.nlm_api_tool import check_drug_interactions, find_rxcui_by_name

llm = ChatGroq(model="qwen/qwen3.8-27b", groq_api_key=os.getenv("GROQ_API_KEY") or "gsk_placeholder")


class AntibioticPlan(BaseModel):
    antibiotics: list[str] = Field(description="Recommended empiric antibiotic(s) by generic name")
    dosages: list[str] = Field(description="Dosage + route + frequency for each antibiotic, same order as antibiotics")
    contraindication_warnings: list[str] = Field(
        default_factory=list,
        description="Any warnings about interactions with the patient's current medications",
    )


structured_llm = llm.with_structured_output(AntibioticPlan)


def run(state: SepsisGuardState) -> SepsisGuardState:
    alert = state.get("sepsis_alert")
    if not alert:
        return state

    current_meds = state.get("current_medications", [])
    rxcuis = [rxcui for rxcui in (find_rxcui_by_name(m) for m in current_meds) if rxcui]
    interactions = check_drug_interactions(rxcuis) if rxcuis else {}

    plan = structured_llm.invoke(
        [
            ("system", PHARMACO_GENOMIC_PROMPT),
            (
                "human",
                f"Sepsis alert: {alert}\n"
                f"Suspected infection source: {state.get('suspected_infection_source')}\n"
                f"Current medications: {current_meds}\n"
                f"Known NLM interactions: {interactions}\n"
                "Recommend empiric antibiotics and safe dosages.",
            ),
        ]
    )

    return {
        **state,
        "antibiotics": plan.antibiotics,
        "dosages": plan.dosages,
        "contraindication_warnings": plan.contraindication_warnings,
    }
