# Agent 4 — ICU Resource Broker Agent.
# Checks ICU bed availability, reserves an infusion pump, and notifies nursing staff.

import os
import random

from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from graph.state import SepsisGuardState
from prompts.resource_prompt import ICU_RESOURCE_BROKER_PROMPT

llm = ChatGroq(model="qwen/qwen3.8-27b", groq_api_key=os.getenv("GROQ_API_KEY") or "gsk_placeholder")


class NursingNotification(BaseModel):
    message: str = Field(description="Concise message for the nursing staff describing what is needed and by when")


structured_llm = llm.with_structured_output(NursingNotification)

# Simulated ICU resource pool for this hackathon build — swap for a real
# bed-management system integration in production.
_AVAILABLE_BEDS = [f"ICU-{n}" for n in range(1, 13)]
_AVAILABLE_PUMPS = [f"PUMP-{n}" for n in range(1, 21)]


def run(state: SepsisGuardState) -> SepsisGuardState:
    if not state.get("sepsis_alert"):
        return state

    bed_id = random.choice(_AVAILABLE_BEDS)
    pump_id = random.choice(_AVAILABLE_PUMPS)

    notification = structured_llm.invoke(
        [
            ("system", ICU_RESOURCE_BROKER_PROMPT),
            (
                "human",
                f"Patient: {state.get('patient_id')}\n"
                f"Severity: {state.get('severity')}\n"
                f"Priority actions: {state.get('priority_actions')}\n"
                f"Reserved bed: {bed_id}, reserved pump: {pump_id}",
            ),
        ]
    )

    return {
        **state,
        "icu_bed_reserved": True,
        "infusion_pump_reserved": True,
        "bed_id": bed_id,
        "pump_id": pump_id,
        "nursing_message": notification.message,
    }
