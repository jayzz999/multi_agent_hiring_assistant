"""Planner Agent for creating hiring workflow plans."""

from typing import Any, Dict
from langchain_core.messages import HumanMessage
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.agents.base_agent import BaseAgent
from src.prompts.planner_prompts import PLANNER_SYSTEM_PROMPT, PLANNER_TASK_PROMPT


class PlannerAgent(BaseAgent):
    """
    Planning agent that analyzes job descriptions and creates hiring workflow plans.

    The Planner is the first agent in the PEC (Planner-Executor-Critic) architecture.
    It sets the criteria and guidelines that executor agents will follow.
    """

    def __init__(self):
        """Initialize the Planner Agent."""
        super().__init__(
            name="Hiring Planner",
            system_prompt=PLANNER_SYSTEM_PROMPT,
            temperature=0.3  # Lower temperature for consistent, structured planning
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a hiring workflow plan based on the job description.

        Args:
            state: Current workflow state containing:
                - job_description: The job description to analyze
                - num_candidates: Number of candidates to process
                - special_requirements: Any special requirements

        Returns:
            Updated state with:
                - plan: The generated hiring plan
                - plan_created: True
                - current_step: Incremented
        """
        job_description = state.get("job_description", "")
        num_candidates = state.get("num_candidates", 10)
        special_requirements = state.get("special_requirements", "")

        if not job_description:
            return {
                **state,
                "error": "No job description provided",
                "plan": None,
                "plan_created": False
            }

        # Create the planning prompt
        prompt = PLANNER_TASK_PROMPT.format(
            job_description=job_description,
            num_candidates=num_candidates,
            special_requirements=special_requirements or "None specified"
        )

        # Generate the plan
        plan = self.invoke([HumanMessage(content=prompt)])

        return {
            **state,
            "plan": plan,
            "plan_created": True,
            "current_step": state.get("current_step", 0) + 1
        }

    def analyze_job_description(self, job_description: str) -> Dict[str, Any]:
        """
        Standalone method to analyze a job description without full workflow.

        Args:
            job_description: The job description text

        Returns:
            Dictionary with analysis results
        """
        analysis_prompt = f"""Analyze this job description and extract:
1. Key technical requirements
2. Experience level needed
3. Must-have vs nice-to-have skills
4. Potential challenges in finding candidates

JOB DESCRIPTION:
{job_description}

Provide a structured analysis."""

        analysis = self.invoke([HumanMessage(content=analysis_prompt)])

        return {
            "job_description": job_description[:500] + "..." if len(job_description) > 500 else job_description,
            "analysis": analysis
        }
