# Agent 2 — Clinical Strategist Agent.
# Orchestrates the sepsis emergency response: delegates to the Pharmaco-Genomic,
# ICU Resource Broker, and Safety Auditor agents, then assembles the final treatment plan.

import os

from langchain_groq import ChatGroq

from graph.state import SepsisGuardState
from prompts.strategist_prompt import CLINICAL_STRATEGIST_PROMPT

llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=os.getenv("GROQ_API_KEY"))


def run(state: SepsisGuardState) -> SepsisGuardState:
    alert = state.get("sepsis_alert")
    if not alert:
        return state

    # The strategist reasons over the alert to set the plan of action; the
    # actual delegation to downstream agents happens as graph edges in
    # graph/sepsisguard_workflow.py.
    response = llm.invoke(
        [
            ("system", CLINICAL_STRATEGIST_PROMPT),
            ("human", f"Sepsis alert: {alert}"),
        ]
    )

    return {
        **state,
        "strategy_notes": response.content,
    }
