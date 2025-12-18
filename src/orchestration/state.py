"""Shared state definitions for the hiring workflow."""

from typing import TypedDict, Optional, Literal, List, Any
from dataclasses import dataclass, field
from datetime import datetime


class HiringState(TypedDict, total=False):
    """
    Shared state for the hiring workflow.

    This state is passed between all agents in the workflow,
    allowing them to read previous results and add their own.
    """

    # Input Configuration
    job_description: str
    num_candidates: int
    num_to_interview: int
    special_requirements: Optional[str]

    # Planning Phase
    plan: Optional[str]
    plan_created: bool

    # Screening Phase
    screening_results: Optional[str]
    screening_completed: bool

    # Skill Matching Phase
    matching_results: Optional[str]
    matching_completed: bool

    # Ranking Phase
    ranking_results: Optional[str]
    ranking_completed: bool

    # Critique Phase
    critique: Optional[str]
    verdict: Optional[Literal["APPROVE", "REVISE", "REJECT"]]
    critique_completed: bool

    # Workflow Control
    current_step: int
    revision_count: int
    max_revisions: int
    error: Optional[str]
    completed: bool

    # Final Output
    final_recommendations: Optional[str]
    interview_schedule: Optional[str]

    # Metadata
    started_at: Optional[str]
    completed_at: Optional[str]
    execution_log: List[str]


def create_initial_state(
    job_description: str,
    num_candidates: int = 10,
    num_to_interview: int = 3,
    special_requirements: Optional[str] = None,
    max_revisions: int = 2
) -> HiringState:
    """
    Create the initial state for a hiring workflow.

    Args:
        job_description: The job description to hire for
        num_candidates: Expected number of candidates to process
        num_to_interview: Number of candidates to recommend for interviews
        special_requirements: Any special requirements or notes
        max_revisions: Maximum revision loops before forcing completion

    Returns:
        Initialized HiringState
    """
    return HiringState(
        # Input
        job_description=job_description,
        num_candidates=num_candidates,
        num_to_interview=num_to_interview,
        special_requirements=special_requirements,

        # Planning
        plan=None,
        plan_created=False,

        # Screening
        screening_results=None,
        screening_completed=False,

        # Matching
        matching_results=None,
        matching_completed=False,

        # Ranking
        ranking_results=None,
        ranking_completed=False,

        # Critique
        critique=None,
        verdict=None,
        critique_completed=False,

        # Workflow control
        current_step=0,
        revision_count=0,
        max_revisions=max_revisions,
        error=None,
        completed=False,

        # Output
        final_recommendations=None,
        interview_schedule=None,

        # Metadata
        started_at=datetime.now().isoformat(),
        completed_at=None,
        execution_log=[]
    )


@dataclass
class WorkflowProgress:
    """Track workflow progress for UI updates."""

    current_phase: str = "initialized"
    phases_completed: List[str] = field(default_factory=list)
    current_agent: Optional[str] = None
    progress_percentage: float = 0.0
    status_message: str = "Workflow initialized"
    errors: List[str] = field(default_factory=list)

    PHASES = [
        "planning",
        "screening",
        "matching",
        "ranking",
        "critique",
        "finalization"
    ]

    def update_phase(self, phase: str, agent_name: str = None):
        """Update the current phase."""
        self.current_phase = phase
        self.current_agent = agent_name

        phase_index = self.PHASES.index(phase) if phase in self.PHASES else 0
        self.progress_percentage = (phase_index / len(self.PHASES)) * 100

        self.status_message = f"Running {phase} phase"
        if agent_name:
            self.status_message += f" ({agent_name})"

    def complete_phase(self, phase: str):
        """Mark a phase as complete."""
        if phase not in self.phases_completed:
            self.phases_completed.append(phase)

        phase_index = self.PHASES.index(phase) if phase in self.PHASES else 0
        self.progress_percentage = ((phase_index + 1) / len(self.PHASES)) * 100

    def add_error(self, error: str):
        """Add an error message."""
        self.errors.append(error)
        self.status_message = f"Error: {error}"

    def get_summary(self) -> dict:
        """Get progress summary."""
        return {
            "current_phase": self.current_phase,
            "phases_completed": self.phases_completed,
            "current_agent": self.current_agent,
            "progress": f"{self.progress_percentage:.1f}%",
            "status": self.status_message,
            "has_errors": len(self.errors) > 0
        }


def validate_state(state: HiringState) -> List[str]:
    """
    Validate the hiring state for common issues.

    Args:
        state: The state to validate

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    if not state.get("job_description"):
        errors.append("Job description is required")

    if state.get("num_candidates", 0) <= 0:
        errors.append("Number of candidates must be positive")

    if state.get("num_to_interview", 0) <= 0:
        errors.append("Number to interview must be positive")

    if state.get("num_to_interview", 0) > state.get("num_candidates", 0):
        errors.append("Number to interview cannot exceed number of candidates")

    return errors


def get_state_summary(state: HiringState) -> dict:
    """
    Get a summary of the current state.

    Args:
        state: The hiring state

    Returns:
        Summary dictionary
    """
    return {
        "job_description_length": len(state.get("job_description", "")),
        "num_candidates": state.get("num_candidates", 0),
        "num_to_interview": state.get("num_to_interview", 0),
        "phases": {
            "planning": state.get("plan_created", False),
            "screening": state.get("screening_completed", False),
            "matching": state.get("matching_completed", False),
            "ranking": state.get("ranking_completed", False),
            "critique": state.get("critique_completed", False)
        },
        "verdict": state.get("verdict"),
        "revision_count": state.get("revision_count", 0),
        "completed": state.get("completed", False),
        "has_error": state.get("error") is not None
    }
