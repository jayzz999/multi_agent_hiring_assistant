"""Tests for orchestration components."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.orchestration.state import (
    HiringState,
    create_initial_state,
    validate_state,
    get_state_summary,
    WorkflowProgress
)
from src.orchestration.router import HiringOrchestrator


class TestHiringState:
    """Tests for HiringState and related functions."""

    def test_create_initial_state(self):
        """Test creating initial state with required fields."""
        state = create_initial_state(
            job_description="Senior Python Developer",
            num_candidates=10,
            num_to_interview=3
        )

        assert state["job_description"] == "Senior Python Developer"
        assert state["num_candidates"] == 10
        assert state["num_to_interview"] == 3
        assert state["plan_created"] == False
        assert state["completed"] == False
        assert state["current_step"] == 0

    def test_create_state_with_special_requirements(self):
        """Test state creation with optional fields."""
        state = create_initial_state(
            job_description="Python Developer",
            special_requirements="Must have AWS experience"
        )

        assert state["special_requirements"] == "Must have AWS experience"

    def test_create_state_with_max_revisions(self):
        """Test state creation with custom max revisions."""
        state = create_initial_state(
            job_description="Developer",
            max_revisions=5
        )

        assert state["max_revisions"] == 5

    def test_state_has_timestamp(self):
        """Test that state includes start timestamp."""
        state = create_initial_state(job_description="Developer")
        assert state.get("started_at") is not None

    def test_state_has_execution_log(self):
        """Test that state includes execution log."""
        state = create_initial_state(job_description="Developer")
        assert isinstance(state.get("execution_log"), list)


class TestValidateState:
    """Tests for state validation."""

    def test_validate_valid_state(self):
        """Test validation of a valid state."""
        state = create_initial_state(
            job_description="Senior Python Developer with 5 years experience",
            num_candidates=10,
            num_to_interview=3
        )

        errors = validate_state(state)
        assert len(errors) == 0

    def test_validate_empty_job_description(self):
        """Test validation catches empty job description."""
        state = create_initial_state(
            job_description="",
            num_candidates=10
        )

        errors = validate_state(state)
        assert len(errors) > 0
        assert any("description" in e.lower() for e in errors)

    def test_validate_negative_candidates(self):
        """Test validation catches negative candidate count."""
        state = create_initial_state(
            job_description="Developer",
            num_candidates=-5
        )

        errors = validate_state(state)
        assert len(errors) > 0

    def test_validate_zero_candidates(self):
        """Test validation catches zero candidates."""
        state = create_initial_state(
            job_description="Developer",
            num_candidates=0
        )

        errors = validate_state(state)
        assert len(errors) > 0

    def test_validate_interviews_exceed_candidates(self):
        """Test validation catches when interviews exceed candidates."""
        state = create_initial_state(
            job_description="Developer",
            num_candidates=3,
            num_to_interview=10
        )

        errors = validate_state(state)
        assert len(errors) > 0

    def test_validate_missing_fields(self):
        """Test validation of incomplete state."""
        state = {}
        errors = validate_state(state)
        assert len(errors) > 0


class TestGetStateSummary:
    """Tests for state summary generation."""

    def test_summary_initial_state(self):
        """Test summary of initial state."""
        state = create_initial_state(
            job_description="Developer",
            num_candidates=10,
            num_to_interview=3
        )

        summary = get_state_summary(state)

        assert summary["num_candidates"] == 10
        assert summary["num_to_interview"] == 3
        assert summary["completed"] == False
        assert summary["phases"]["planning"] == False

    def test_summary_completed_phases(self):
        """Test summary shows completed phases."""
        state = create_initial_state(job_description="Developer")
        state["plan_created"] = True
        state["screening_completed"] = True

        summary = get_state_summary(state)

        assert summary["phases"]["planning"] == True
        assert summary["phases"]["screening"] == True
        assert summary["phases"]["matching"] == False

    def test_summary_verdict(self):
        """Test summary includes verdict."""
        state = create_initial_state(job_description="Developer")
        state["verdict"] = "APPROVE"

        summary = get_state_summary(state)
        assert summary["verdict"] == "APPROVE"


class TestWorkflowProgress:
    """Tests for WorkflowProgress tracking."""

    def test_progress_initialization(self):
        """Test progress tracker initialization."""
        progress = WorkflowProgress()

        assert progress.current_phase == "initialized"
        assert progress.progress_percentage == 0.0
        assert len(progress.phases_completed) == 0

    def test_update_phase(self):
        """Test updating current phase."""
        progress = WorkflowProgress()
        progress.update_phase("planning", "Planner Agent")

        assert progress.current_phase == "planning"
        assert progress.current_agent == "Planner Agent"
        assert progress.progress_percentage > 0

    def test_complete_phase(self):
        """Test completing a phase."""
        progress = WorkflowProgress()
        progress.complete_phase("planning")

        assert "planning" in progress.phases_completed

    def test_add_error(self):
        """Test adding error."""
        progress = WorkflowProgress()
        progress.add_error("Test error")

        assert len(progress.errors) == 1
        assert "Test error" in progress.errors[0]

    def test_get_summary(self):
        """Test getting progress summary."""
        progress = WorkflowProgress()
        progress.update_phase("screening")
        progress.complete_phase("planning")

        summary = progress.get_summary()

        assert summary["current_phase"] == "screening"
        assert "planning" in summary["phases_completed"]
        assert "progress" in summary


class TestHiringOrchestrator:
    """Tests for HiringOrchestrator."""

    def test_orchestrator_initialization(self):
        """Test orchestrator initializes correctly."""
        orchestrator = HiringOrchestrator()
        assert orchestrator.graph is not None
        assert orchestrator.last_result is None

    def test_orchestrator_validates_input(self):
        """Test orchestrator validates input before running."""
        orchestrator = HiringOrchestrator()

        result = orchestrator.run(
            job_description="",  # Empty - should fail validation
            num_candidates=10
        )

        assert result["success"] == False
        assert result.get("error") is not None

    def test_orchestrator_run_returns_formatted_result(self):
        """Test orchestrator returns properly formatted result."""
        orchestrator = HiringOrchestrator()

        # Even with invalid input, should return expected structure
        result = orchestrator.run(
            job_description="",
            num_candidates=-1
        )

        assert "success" in result
        assert "error" in result

    def test_execution_report_empty_initially(self):
        """Test execution report is None before running."""
        orchestrator = HiringOrchestrator()
        report = orchestrator.get_execution_report()
        assert report is None


class TestGraphBuilding:
    """Tests for graph construction."""

    def test_graph_has_all_nodes(self):
        """Test that graph has all required nodes."""
        from src.orchestration.graph import build_hiring_graph

        graph = build_hiring_graph()
        # Graph should compile without errors
        assert graph is not None

    def test_routing_function_approve(self):
        """Test routing function with APPROVE verdict."""
        from src.orchestration.graph import should_revise

        state = {
            "verdict": "APPROVE",
            "revision_count": 0,
            "max_revisions": 2
        }

        result = should_revise(state)
        assert result == "finalize"

    def test_routing_function_revise(self):
        """Test routing function with REVISE verdict."""
        from src.orchestration.graph import should_revise

        state = {
            "verdict": "REVISE",
            "revision_count": 0,
            "max_revisions": 2
        }

        result = should_revise(state)
        assert result == "revise"

    def test_routing_function_max_revisions(self):
        """Test routing function when max revisions reached."""
        from src.orchestration.graph import should_revise

        state = {
            "verdict": "REVISE",
            "revision_count": 2,
            "max_revisions": 2
        }

        result = should_revise(state)
        assert result == "finalize"  # Should finalize despite REVISE

    def test_routing_function_error(self):
        """Test routing function with error in state."""
        from src.orchestration.graph import should_revise

        state = {
            "error": "Some error occurred",
            "verdict": "APPROVE"
        }

        result = should_revise(state)
        assert result == "error"


# Run with: pytest tests/test_orchestration.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
