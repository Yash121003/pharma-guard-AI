"""
LangGraph workflow definition. A single graph handles all AI features --
a router reads state["task"] and dispatches to the matching node, which
runs and terminates. Keeping every feature as a node on one graph (rather
than separate ad-hoc functions) is what the assignment calls for, and it
gives us one place to later add cross-node behavior (e.g. always logging
node execution, or chaining root_cause -> capa automatically).
"""
import logging

from langgraph.graph import END, StateGraph

from app.ai.nodes.capa import capa_node
from app.ai.nodes.completeness import completeness_node
from app.ai.nodes.duplicate import duplicate_node
from app.ai.nodes.extract import extract_node
from app.ai.nodes.qa import qa_node
from app.ai.nodes.risk import risk_node
from app.ai.nodes.root_cause import root_cause_node
from app.ai.nodes.summarize import summarize_node
from app.ai.state import ComplaintGraphState

logger = logging.getLogger(__name__)

NODE_MAP = {
    "extract": "extract_task",
    "qa": "qa_task",
    "summarize": "summarize_task",
    "root_cause": "root_cause_task",
    "capa": "capa_task",
    "risk": "risk_task",
    "duplicate": "duplicate_task",
    "completeness": "completeness_task",
}


def _route(state: ComplaintGraphState) -> str:
    task = state.get("task")
    if task not in NODE_MAP:
        raise ValueError(f"Unknown AI task: {task!r}")
    return NODE_MAP[task]


def build_graph():
    graph = StateGraph(ComplaintGraphState)

    graph.add_node("extract_task", extract_node)
    graph.add_node("qa_task", qa_node)
    graph.add_node("summarize_task", summarize_node)
    graph.add_node("root_cause_task", root_cause_node)
    graph.add_node("capa_task", capa_node)
    graph.add_node("risk_task", risk_node)
    graph.add_node("duplicate_task", duplicate_node)
    graph.add_node("completeness_task", completeness_node)

    graph.set_conditional_entry_point(_route, {node_name: node_name for node_name in NODE_MAP.values()})

    for node_name in NODE_MAP.values():
        graph.add_edge(node_name, END)

    return graph.compile()


# Compiled once at import time and reused across requests.
complaint_graph = build_graph()


def run_ai_task(task: str, **inputs) -> ComplaintGraphState:
    """
    Convenience entry point: run_ai_task("summarize", complaint_data={...})
    """
    initial_state: ComplaintGraphState = {"task": task, **inputs}
    logger.info("Running AI task: %s", task)
    result = complaint_graph.invoke(initial_state)
    return result
