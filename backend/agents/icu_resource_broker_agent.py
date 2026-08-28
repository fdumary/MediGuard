# Agent 4 — ICU Resource Broker Agent.
# Checks ICU bed availability, reserves an infusion pump, and notifies nursing staff.

import os

from langchain_groq import ChatGroq

from graph.state import SepsisGuardState
from prompts.resource_prompt import ICU_RESOURCE_BROKER_PROMPT

llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=os.getenv("GROQ_API_KEY"))


def run(state: SepsisGuardState) -> SepsisGuardState:
    if not state.get("sepsis_alert"):
        return state

    # In this hackathon build, bed/pump availability is simulated as always
    # available; swap in a real bed-management system for production use.
    response = llm.invoke(
        [
            ("system", ICU_RESOURCE_BROKER_PROMPT),
            ("human", f"Treatment context: {state.get('sepsis_alert')}"),
        ]
    )

    return {
        **state,
        "icu_bed_reserved": True,
        "infusion_pump_reserved": True,
        "nursing_notification": response.content,
    }
