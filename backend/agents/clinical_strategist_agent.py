# Agent 2 — Clinical Strategist Agent.
# Orchestrates the sepsis emergency response: delegates to the Pharmaco-Genomic,
# ICU Resource Broker, and Safety Auditor agents, then assembles the final treatment plan.

import os

from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from graph.state import SepsisGuardState
from prompts.strategist_prompt import CLINICAL_STRATEGIST_PROMPT

llm = ChatGroq(model="qwen/qwen3.8-27b", groq_api_key=os.getenv("GROQ_API_KEY"))


class TreatmentStrategy(BaseModel):
    summary: str = Field(description="One-paragraph summary of the response strategy")
    priority_actions: list[str] = Field(
        description="Ordered list of the highest-priority actions for the next hour, "
        "following the Surviving Sepsis Campaign 1-hour bundle"
    )


structured_llm = llm.with_structured_output(TreatmentStrategy)


def run(state: SepsisGuardState) -> SepsisGuardState:
    alert = state.get("sepsis_alert")
    if not alert:
        return state

    strategy = structured_llm.invoke(
        [
            ("system", CLINICAL_STRATEGIST_PROMPT),
            (
                "human",
                f"Sepsis alert: {alert}\n"
                f"Suspected infection source: {state.get('suspected_infection_source')}\n"
                f"Recommended actions from Vitals Sentinel: {state.get('recommended_actions')}",
            ),
        ]
    )

    return {
        **state,
        "strategy_summary": strategy.summary,
        "priority_actions": strategy.priority_actions,
    }
