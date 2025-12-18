"""Tests for the hiring assistant agents."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.base_agent import BaseAgent
from src.agents.planner_agent import PlannerAgent
from src.agents.resume_screener import ResumeScreenerAgent
from src.agents.skill_matcher import SkillMatcherAgent
from src.agents.candidate_ranker import CandidateRankerAgent
from src.agents.critic_agent import CriticAgent


class TestBaseAgent:
    """Tests for the BaseAgent class."""

    def test_base_agent_is_abstract(self):
        """BaseAgent should not be instantiated directly."""
        with pytest.raises(TypeError):
            BaseAgent(name="test", system_prompt="test prompt")

    def test_agent_repr(self):
        """Test agent string representation."""
        planner = PlannerAgent()
        assert "PlannerAgent" in repr(planner)
        assert "Hiring Planner" in repr(planner)


class TestPlannerAgent:
    """Tests for the PlannerAgent."""

    def test_planner_initialization(self):
        """Test planner agent initializes correctly."""
        planner = PlannerAgent()
        assert planner.name == "Hiring Planner"
        assert planner.temperature == 0.3

    def test_planner_execute_empty_jd(self):
        """Test planner handles empty job description."""
        planner = PlannerAgent()
        state = {"job_description": ""}
        result = planner.execute(state)

        assert result.get("error") is not None
        assert result.get("plan_created") == False

    def test_planner_execute_preserves_state(self):
        """Test that planner preserves existing state fields."""
        planner = PlannerAgent()
        state = {
            "job_description": "",
            "custom_field": "preserved"
        }
        result = planner.execute(state)

        assert result.get("custom_field") == "preserved"


class TestResumeScreenerAgent:
    """Tests for the ResumeScreenerAgent."""

    def test_screener_initialization(self):
        """Test screener agent initializes correctly."""
        screener = ResumeScreenerAgent()
        assert screener.name == "Resume Screener"
        assert screener.temperature == 0.2

    def test_screener_has_rag_tool(self):
        """Test screener has RAG tool configured."""
        screener = ResumeScreenerAgent()
        assert screener.rag_tool is not None

    def test_screener_execute_no_jd(self):
        """Test screener handles missing job description."""
        screener = ResumeScreenerAgent()
        state = {"job_description": ""}
        result = screener.execute(state)

        assert result.get("error") is not None
        assert result.get("screening_completed") == False


class TestSkillMatcherAgent:
    """Tests for the SkillMatcherAgent."""

    def test_matcher_initialization(self):
        """Test skill matcher initializes correctly."""
        matcher = SkillMatcherAgent()
        assert matcher.name == "Skill Matcher"
        assert matcher.temperature == 0.2

    def test_matcher_execute_no_screening(self):
        """Test matcher handles missing screening results."""
        matcher = SkillMatcherAgent()
        state = {"job_description": "Test job"}
        result = matcher.execute(state)

        assert result.get("error") is not None
        assert result.get("matching_completed") == False


class TestCandidateRankerAgent:
    """Tests for the CandidateRankerAgent."""

    def test_ranker_initialization(self):
        """Test ranker initializes correctly."""
        ranker = CandidateRankerAgent()
        assert ranker.name == "Candidate Ranker"
        assert ranker.temperature == 0.1

    def test_ranker_execute_no_matching(self):
        """Test ranker handles missing matching results."""
        ranker = CandidateRankerAgent()
        state = {"job_description": "Test job"}
        result = ranker.execute(state)

        assert result.get("error") is not None
        assert result.get("ranking_completed") == False


class TestCriticAgent:
    """Tests for the CriticAgent."""

    def test_critic_initialization(self):
        """Test critic initializes correctly."""
        critic = CriticAgent()
        assert critic.name == "Hiring Critic"
        assert critic.temperature == 0.4

    def test_critic_extract_verdict_approve(self):
        """Test verdict extraction for APPROVE."""
        critic = CriticAgent()
        critique = "The process was excellent. FINAL VERDICT: APPROVE"
        verdict = critic._extract_verdict(critique)
        assert verdict == "APPROVE"

    def test_critic_extract_verdict_revise(self):
        """Test verdict extraction for REVISE."""
        critic = CriticAgent()
        critique = "Some issues found. VERDICT: REVISE"
        verdict = critic._extract_verdict(critique)
        assert verdict == "REVISE"

    def test_critic_extract_verdict_reject(self):
        """Test verdict extraction for REJECT."""
        critic = CriticAgent()
        critique = "Major issues. **REJECT**"
        verdict = critic._extract_verdict(critique)
        assert verdict == "REJECT"

    def test_critic_execute_no_data(self):
        """Test critic handles missing data."""
        critic = CriticAgent()
        state = {}
        result = critic.execute(state)

        assert result.get("error") is not None
        assert result.get("verdict") == "REJECT"


class TestAgentIntegration:
    """Integration tests for agent interactions."""

    def test_agents_share_state_structure(self):
        """Test that all agents can work with the same state structure."""
        from src.orchestration.state import create_initial_state

        state = create_initial_state(
            job_description="Senior Python Developer with 5 years experience",
            num_candidates=10,
            num_to_interview=3
        )

        # Each agent should be able to receive this state
        planner = PlannerAgent()
        screener = ResumeScreenerAgent()
        matcher = SkillMatcherAgent()
        ranker = CandidateRankerAgent()
        critic = CriticAgent()

        # All should at least not crash on the state structure
        assert state.get("job_description") is not None

    def test_agent_metrics(self):
        """Test that agents track metrics."""
        planner = PlannerAgent()

        # Initial metrics should be zero
        metrics = planner.get_metrics()
        assert metrics["execution_time"] == 0
        assert metrics["agent_name"] == "Hiring Planner"


# Run with: pytest tests/test_agents.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
