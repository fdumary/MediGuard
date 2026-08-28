# LangGraph StateGraph wiring the 5 SepsisGuard agents together:
# Vitals Sentinel -> Clinical Strategist -> (Pharmaco-Genomic + ICU Resource Broker) -> Safety Auditor.

from langgraph.graph import END, StateGraph

from agents import (
    clinical_strategist_agent,
    icu_resource_broker_agent,
    pharmaco_genomic_agent,
    safety_auditor_agent,
    vitals_sentinel_agent,
)
from graph.state import SepsisGuardState


def route_after_vitals(state: SepsisGuardState) -> str:
    """Only continue the pipeline if a sepsis alert was actually triggered."""
    return "clinical_strategist" if state.get("sepsis_alert") else END


def build_sepsisguard_graph():
    graph = StateGraph(SepsisGuardState)

    graph.add_node("vitals_sentinel", vitals_sentinel_agent.run)
    graph.add_node("clinical_strategist", clinical_strategist_agent.run)
    graph.add_node("pharmaco_genomic", pharmaco_genomic_agent.run)
    graph.add_node("icu_resource_broker", icu_resource_broker_agent.run)
    graph.add_node("safety_auditor", safety_auditor_agent.run)

    graph.set_entry_point("vitals_sentinel")
    graph.add_conditional_edges(
        "vitals_sentinel",
        route_after_vitals,
        {"clinical_strategist": "clinical_strategist", END: END},
    )
    graph.add_edge("clinical_strategist", "pharmaco_genomic")
    graph.add_edge("pharmaco_genomic", "icu_resource_broker")
    graph.add_edge("icu_resource_broker", "safety_auditor")
    graph.add_edge("safety_auditor", END)

    return graph.compile()


sepsisguard_app = build_sepsisguard_graph()
