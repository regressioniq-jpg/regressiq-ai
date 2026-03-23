from typing import TypedDict, Dict, List, Any
from langgraph.graph import StateGraph, END

from agents import (
    change_agent,
    impact_agent,
    risk_agent,
    test_agent,
    coverage_agent,
    strategy_agent
)


class RegressIQState(TypedDict, total=False):
    cr_text: str
    change_analysis: Dict[str, Any]
    impacted_modules: List[str]
    graph: Any
    risk_assessment: Dict[str, Any]
    test_plan: List[Dict[str, Any]]
    coverage: Dict[str, Any]
    strategy: str


def change_node(state: RegressIQState):
    result = change_agent(state["cr_text"])
    return {"change_analysis": result}


def impact_node(state: RegressIQState):
    changed_modules = state["change_analysis"]["changed_modules"]
    impacted_modules, graph = impact_agent(changed_modules)
    return {
        "impacted_modules": impacted_modules,
        "graph": graph
    }


def risk_node(state: RegressIQState):
    result = risk_agent(state["impacted_modules"])
    return {"risk_assessment": result}


def test_node(state: RegressIQState):
    summary = state["change_analysis"].get("summary", "")
    result = test_agent(state["impacted_modules"], summary)
    return {"test_plan": result}


def coverage_node(state: RegressIQState):
    result = coverage_agent(state["impacted_modules"], state["test_plan"])
    return {"coverage": result}


def strategy_node(state: RegressIQState):
    result = strategy_agent(
        state["impacted_modules"],
        state["risk_assessment"],
        state["coverage"],
        state["test_plan"]
    )
    return {"strategy": result}


builder = StateGraph(RegressIQState)

builder.add_node("change", change_node)
builder.add_node("impact", impact_node)
builder.add_node("risk", risk_node)
builder.add_node("tests", test_node)
builder.add_node("coverage", coverage_node)
builder.add_node("strategy", strategy_node)

builder.set_entry_point("change")
builder.add_edge("change", "impact")
builder.add_edge("impact", "risk")
builder.add_edge("risk", "tests")
builder.add_edge("tests", "coverage")
builder.add_edge("coverage", "strategy")
builder.add_edge("strategy", END)

graph = builder.compile()