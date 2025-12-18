"""High-level orchestration router for the hiring workflow."""

from typing import Dict, Any, Generator, Optional
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.orchestration.state import HiringState, create_initial_state, validate_state, get_state_summary
from src.orchestration.graph import get_hiring_graph


class HiringOrchestrator:
    """
    High-level orchestrator for the hiring workflow.

    Provides a clean interface for running the multi-agent hiring
    workflow with various execution modes.
    """

    def __init__(self):
        """Initialize the orchestrator."""
        self.graph = get_hiring_graph()
        self.last_result: Optional[Dict[str, Any]] = None

    def run(
        self,
        job_description: str,
        num_candidates: int = 10,
        num_to_interview: int = 3,
        special_requirements: Optional[str] = None,
        max_revisions: int = 2
    ) -> Dict[str, Any]:
        """
        Run the complete hiring workflow.

        Args:
            job_description: The job description to hire for
            num_candidates: Expected number of candidates
            num_to_interview: Number to recommend for interviews
            special_requirements: Any special requirements
            max_revisions: Maximum revision loops

        Returns:
            Formatted results dictionary
        """
        # Create initial state
        initial_state = create_initial_state(
            job_description=job_description,
            num_candidates=num_candidates,
            num_to_interview=num_to_interview,
            special_requirements=special_requirements,
            max_revisions=max_revisions
        )

        # Validate state
        errors = validate_state(initial_state)
        if errors:
            return {
                "success": False,
                "error": "; ".join(errors),
                "results": None
            }

        # Execute the graph
        try:
            final_state = self.graph.invoke(initial_state)
            self.last_result = self._format_results(final_state)
            return self.last_result
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": None
            }

    def run_streaming(
        self,
        job_description: str,
        num_candidates: int = 10,
        num_to_interview: int = 3,
        special_requirements: Optional[str] = None,
        max_revisions: int = 2
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Run workflow with streaming updates.

        Yields status updates as each node completes.

        Args:
            job_description: The job description
            num_candidates: Expected number of candidates
            num_to_interview: Number to recommend
            special_requirements: Any special requirements
            max_revisions: Maximum revision loops

        Yields:
            Status updates and intermediate results
        """
        initial_state = create_initial_state(
            job_description=job_description,
            num_candidates=num_candidates,
            num_to_interview=num_to_interview,
            special_requirements=special_requirements,
            max_revisions=max_revisions
        )

        errors = validate_state(initial_state)
        if errors:
            yield {
                "type": "error",
                "message": "; ".join(errors)
            }
            return

        yield {
            "type": "start",
            "message": "Starting hiring workflow...",
            "timestamp": datetime.now().isoformat()
        }

        try:
            for event in self.graph.stream(initial_state):
                # Extract the node name and state update
                for node_name, node_state in event.items():
                    yield {
                        "type": "node_complete",
                        "node": node_name,
                        "summary": get_state_summary(node_state),
                        "log": node_state.get("execution_log", [])[-1:],
                        "timestamp": datetime.now().isoformat()
                    }

                    # Check for completion or errors
                    if node_state.get("completed"):
                        self.last_result = self._format_results(node_state)
                        yield {
                            "type": "complete",
                            "results": self.last_result,
                            "timestamp": datetime.now().isoformat()
                        }

        except Exception as e:
            yield {
                "type": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def run_step_by_step(
        self,
        job_description: str,
        num_candidates: int = 10,
        num_to_interview: int = 3,
        special_requirements: Optional[str] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Run workflow step by step with full intermediate results.

        This mode is useful for debugging or detailed monitoring.

        Yields:
            Full state after each step
        """
        initial_state = create_initial_state(
            job_description=job_description,
            num_candidates=num_candidates,
            num_to_interview=num_to_interview,
            special_requirements=special_requirements
        )

        for event in self.graph.stream(initial_state):
            for node_name, state in event.items():
                yield {
                    "step": node_name,
                    "state": state,
                    "summary": get_state_summary(state)
                }

    def _format_results(self, state: HiringState) -> Dict[str, Any]:
        """
        Format final results for presentation.

        Args:
            state: Final workflow state

        Returns:
            Formatted results dictionary
        """
        success = state.get("completed", False) and not state.get("error")

        return {
            "success": success,
            "error": state.get("error"),

            # Phase results
            "plan": state.get("plan"),
            "screening_results": state.get("screening_results"),
            "matching_results": state.get("matching_results"),
            "ranking_results": state.get("ranking_results"),

            # Quality control
            "critique": state.get("critique"),
            "verdict": state.get("verdict"),

            # Final output
            "final_recommendations": state.get("final_recommendations"),
            "interview_schedule": state.get("interview_schedule"),

            # Metadata
            "revision_count": state.get("revision_count", 0),
            "execution_log": state.get("execution_log", []),
            "started_at": state.get("started_at"),
            "completed_at": state.get("completed_at")
        }

    def get_execution_report(self) -> Optional[Dict[str, Any]]:
        """
        Get a detailed execution report from the last run.

        Returns:
            Execution report or None if no run completed
        """
        if not self.last_result:
            return None

        return {
            "success": self.last_result.get("success"),
            "verdict": self.last_result.get("verdict"),
            "revisions": self.last_result.get("revision_count", 0),
            "execution_log": self.last_result.get("execution_log", []),
            "duration": self._calculate_duration(),
            "has_recommendations": bool(self.last_result.get("final_recommendations"))
        }

    def _calculate_duration(self) -> Optional[str]:
        """Calculate execution duration."""
        if not self.last_result:
            return None

        started = self.last_result.get("started_at")
        completed = self.last_result.get("completed_at")

        if not started or not completed:
            return None

        try:
            start = datetime.fromisoformat(started)
            end = datetime.fromisoformat(completed)
            duration = (end - start).total_seconds()
            return f"{duration:.1f} seconds"
        except:
            return None


# Convenience function
def run_hiring_workflow(
    job_description: str,
    num_candidates: int = 10,
    num_to_interview: int = 3,
    special_requirements: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to run the hiring workflow.

    Args:
        job_description: The job description
        num_candidates: Expected number of candidates
        num_to_interview: Number to recommend
        special_requirements: Any special requirements

    Returns:
        Workflow results
    """
    orchestrator = HiringOrchestrator()
    return orchestrator.run(
        job_description=job_description,
        num_candidates=num_candidates,
        num_to_interview=num_to_interview,
        special_requirements=special_requirements
    )
