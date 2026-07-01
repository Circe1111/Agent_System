"""LangGraph workflow for the multi-agent learning pipeline.

Nodes (in order):
    profile -> rag -> generator -> guardrail -> planner

`guardrail` is a conditional node: if the generated resource is approved it
proceeds to `planner`; otherwise it loops back to `generator` (up to
`MAX_RETRIES` times) before forcing progression to `planner`.
"""
from langgraph.graph import StateGraph, END

from backend.models_agent import AgentState
from backend.agents import (
    profile_agent,
    rag_agent,
    generator_agent,
    guardrail_agent,
    planner_agent,
)

MAX_RETRIES = 3


def _build_graph() -> StateGraph:
    workflow = StateGraph(AgentState)
    workflow.add_node("profile", profile_agent)
    workflow.add_node("rag", rag_agent)
    workflow.add_node("generator", generator_agent)
    workflow.add_node("guardrail", guardrail_agent)
    workflow.add_node("planner", planner_agent)

    workflow.set_entry_point("profile")
    workflow.add_edge("profile", "rag")
    workflow.add_edge("rag", "generator")
    workflow.add_edge("generator", "guardrail")

    def guardrail_router(state: dict):
        if state.get("is_approved"):
            return "planner"
        retry_count = state.get("retry_count", 0)
        if retry_count >= MAX_RETRIES:
            print(f">>> 已达到最大重试次数({MAX_RETRIES})，强制进入规划阶段")
            return "planner"
        return "generator"

    workflow.add_conditional_edges(
        "guardrail",
        guardrail_router,
        {"planner": "planner", "generator": "generator"},
    )
    workflow.add_edge("planner", END)
    return workflow


# Module-level compiled graph (kept for back-compat with anything that
# already imported `graph_app`).
graph_app = _build_graph().compile()


def create_workflow_graph():
    """Return a fresh compiled graph instance.

    Useful for tests or for spawning isolated runs per request.
    """
    return _build_graph().compile()
