"""LangGraph workflow definition for the hiring assistant."""

from typing import Literal
from langgraph.graph import StateGraph, END
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.orchestration.state import HiringState
from src.agents.planner_agent import PlannerAgent
from src.agents.resume_screener import ResumeScreenerAgent
from src.agents.skill_matcher import SkillMatcherAgent
from src.agents.candidate_ranker import CandidateRankerAgent
from src.agents.critic_agent import CriticAgent

# Initialize agents (lazy initialization to avoid API calls at import time)
_agents = {}


def get_agents():
    """Lazily initialize agents."""
    global _agents
    if not _agents:
        _agents = {
            "planner": PlannerAgent(),
            "screener": ResumeScreenerAgent(),
            "matcher": SkillMatcherAgent(),
            "ranker": CandidateRankerAgent(),
            "critic": CriticAgent()
        }
    return _agents


def log_step(state: HiringState, message: str) -> HiringState:
    """Add a log entry to the state."""
    log = state.get("execution_log", [])
    timestamp = datetime.now().strftime("%H:%M:%S")
    log.append(f"[{timestamp}] {message}")
    return {**state, "execution_log": log}


# Node functions
def plan_node(state: HiringState) -> HiringState:
    """Execute planning step."""
    state = log_step(state, "Starting planning phase...")

    try:
        agents = get_agents()
        result = agents["planner"].execute(state)
        result = log_step(result, "Planning completed successfully")
        return result
    except Exception as e:
        state = log_step(state, f"Planning failed: {str(e)}")
        return {**state, "error": f"Planning failed: {str(e)}"}


def screen_node(state: HiringState) -> HiringState:
    """Execute screening step."""
    state = log_step(state, "Starting resume screening...")

    if state.get("error"):
        return state

    try:
        agents = get_agents()
        result = agents["screener"].execute(state)
        result = log_step(result, "Screening completed successfully")
        return result
    except Exception as e:
        state = log_step(state, f"Screening failed: {str(e)}")
        return {**state, "error": f"Screening failed: {str(e)}"}


def match_node(state: HiringState) -> HiringState:
    """Execute skill matching step."""
    state = log_step(state, "Starting skill matching...")

    if state.get("error"):
        return state

    try:
        agents = get_agents()
        result = agents["matcher"].execute(state)
        result = log_step(result, "Skill matching completed successfully")
        return result
    except Exception as e:
        state = log_step(state, f"Matching failed: {str(e)}")
        return {**state, "error": f"Matching failed: {str(e)}"}


def rank_node(state: HiringState) -> HiringState:
    """Execute ranking step."""
    state = log_step(state, "Starting candidate ranking...")

    if state.get("error"):
        return state

    try:
        agents = get_agents()
        result = agents["ranker"].execute(state)
        result = log_step(result, "Ranking completed successfully")
        return result
    except Exception as e:
        state = log_step(state, f"Ranking failed: {str(e)}")
        return {**state, "error": f"Ranking failed: {str(e)}"}


def critique_node(state: HiringState) -> HiringState:
    """Execute critique step."""
    state = log_step(state, "Starting quality critique...")

    if state.get("error"):
        return state

    try:
        agents = get_agents()
        result = agents["critic"].execute(state)
        result = log_step(result, f"Critique completed - Verdict: {result.get('verdict', 'N/A')}")
        return result
    except Exception as e:
        state = log_step(state, f"Critique failed: {str(e)}")
        return {**state, "error": f"Critique failed: {str(e)}"}


def finalize_node(state: HiringState) -> HiringState:
    """Finalize the hiring process."""
    state = log_step(state, "Finalizing hiring workflow...")

    return {
        **state,
        "completed": True,
        "completed_at": datetime.now().isoformat(),
        "final_recommendations": state.get("ranking_results", "No recommendations available")
    }


def revision_node(state: HiringState) -> HiringState:
    """Prepare for revision."""
    revision_count = state.get("revision_count", 0) + 1
    state = log_step(state, f"Revision requested (attempt {revision_count})")

    return {
        **state,
        "revision_count": revision_count,
        # Reset completion flags for re-execution
        "screening_completed": False,
        "matching_completed": False,
        "ranking_completed": False,
        "critique_completed": False
    }


def error_node(state: HiringState) -> HiringState:
    """Handle errors."""
    state = log_step(state, f"Workflow ended with error: {state.get('error', 'Unknown error')}")

    return {
        **state,
        "completed": True,
        "completed_at": datetime.now().isoformat()
    }


# Routing function
def should_revise(state: HiringState) -> Literal["revise", "finalize", "error"]:
    """Determine next step based on critic verdict."""
    # Check for errors first
    if state.get("error"):
        return "error"

    verdict = state.get("verdict", "APPROVE")
    revision_count = state.get("revision_count", 0)
    max_revisions = state.get("max_revisions", 2)

    if verdict == "APPROVE":
        return "finalize"
    elif verdict in ["REVISE", "REJECT"] and revision_count < max_revisions:
        return "revise"
    else:
        # Max revisions reached, proceed anyway with a log note
        return "finalize"


def build_hiring_graph() -> StateGraph:
    """
    Build the hiring workflow graph.

    Returns:
        Compiled StateGraph for the hiring workflow
    """
    workflow = StateGraph(HiringState)

    # Add all nodes
    workflow.add_node("plan", plan_node)
    workflow.add_node("screen", screen_node)
    workflow.add_node("match", match_node)
    workflow.add_node("rank", rank_node)
    workflow.add_node("critique", critique_node)
    workflow.add_node("finalize", finalize_node)
    workflow.add_node("revision", revision_node)
    workflow.add_node("error", error_node)

    # Set entry point
    workflow.set_entry_point("plan")

    # Add sequential edges
    workflow.add_edge("plan", "screen")
    workflow.add_edge("screen", "match")
    workflow.add_edge("match", "rank")
    workflow.add_edge("rank", "critique")

    # Add conditional edge from critique
    workflow.add_conditional_edges(
        "critique",
        should_revise,
        {
            "revise": "revision",
            "finalize": "finalize",
            "error": "error"
        }
    )

    # Revision loops back to screening
    workflow.add_edge("revision", "screen")

    # Terminal nodes
    workflow.add_edge("finalize", END)
    workflow.add_edge("error", END)

    return workflow.compile()


# Pre-built graph instance for convenience
hiring_graph = None


def get_hiring_graph():
    """Get or create the hiring graph."""
    global hiring_graph
    if hiring_graph is None:
        hiring_graph = build_hiring_graph()
    return hiring_graph
