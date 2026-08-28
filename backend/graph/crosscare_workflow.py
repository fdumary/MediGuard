# LangGraph StateGraph wiring the 3 CrossCare agents together:
# Prescription Ingestion -> Pharmacology Interaction -> Physician Recommendation.

from langgraph.graph import END, StateGraph

from agents import (
    pharmacology_interaction_agent,
    physician_recommendation_agent,
    prescription_ingestion_agent,
)
from graph.state import CrossCareState


def build_crosscare_graph():
    graph = StateGraph(CrossCareState)

    graph.add_node("prescription_ingestion", prescription_ingestion_agent.run)
    graph.add_node("pharmacology_interaction", pharmacology_interaction_agent.run)
    graph.add_node("physician_recommendation", physician_recommendation_agent.run)

    graph.set_entry_point("prescription_ingestion")
    graph.add_edge("prescription_ingestion", "pharmacology_interaction")
    graph.add_edge("pharmacology_interaction", "physician_recommendation")
    graph.add_edge("physician_recommendation", END)

    return graph.compile()


crosscare_app = build_crosscare_graph()
