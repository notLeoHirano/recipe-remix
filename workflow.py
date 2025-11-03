from langgraph.graph import StateGraph, END
from data_models import WorkflowState
from typing import Any

from agents.scraper_agent import ScraperAgent
from agents.filter_agent import DietaryFilterAgent 
from agents.substitution_agent import SubstitutionAgent
from agents.step_adjustment_agent import StepAdjustmentAgent

def check_for_flags(state: WorkflowState) -> str:
    """Checks if any dietary issues were flagged."""
    if state.dietary_flags and len(state.dietary_flags) > 0:
        return "substitute"
    return "adjust_steps"

def compile_workflow(llm_client: Any):
    """Initializes agents and compiles the LangGraph workflow."""

    scraper = ScraperAgent(llm_client)
    filter_agent = DietaryFilterAgent(llm_client)
    suggestion_agent = SubstitutionAgent(llm_client)
    step_adjust_agent = StepAdjustmentAgent(llm_client)

    graph = StateGraph(WorkflowState)
    graph.add_node("scrape", scraper.run)
    graph.add_node("filter", filter_agent.run)
    graph.add_node("substitute", suggestion_agent.run)
    graph.add_node("adjust_steps", step_adjust_agent.run)

    graph.add_edge("scrape", "filter")
    graph.add_conditional_edges(
        "filter",
        check_for_flags,
        {"substitute": "substitute", "adjust_steps": "adjust_steps"}
    )
    graph.add_edge("substitute", "adjust_steps")
    graph.add_edge("adjust_steps", END)

    graph.set_entry_point("scrape")
    return graph.compile()