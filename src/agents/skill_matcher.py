"""Skill Matcher Agent for detailed candidate evaluation."""

from typing import Any, Dict
from langchain_core.messages import HumanMessage
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.agents.base_agent import BaseAgent
from src.prompts.matcher_prompts import MATCHER_SYSTEM_PROMPT, MATCHER_TASK_PROMPT


class SkillMatcherAgent(BaseAgent):
    """
    Skill Matcher Agent that performs detailed skill and experience matching.

    This executor agent evaluates passed candidates across multiple dimensions:
    technical skills, experience, education, and soft skills.
    """

    def __init__(self):
        """Initialize the Skill Matcher Agent."""
        super().__init__(
            name="Skill Matcher",
            system_prompt=MATCHER_SYSTEM_PROMPT,
            temperature=0.2  # Low temperature for consistent evaluation
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform detailed skill matching for screened candidates.

        Args:
            state: Current workflow state containing:
                - job_description: The job requirements
                - screening_results: Results from Resume Screener

        Returns:
            Updated state with:
                - matching_results: Detailed skill analysis for each candidate
                - matching_completed: True
                - current_step: Incremented
        """
        job_description = state.get("job_description", "")
        screening_results = state.get("screening_results", "")

        if not screening_results:
            return {
                **state,
                "error": "No screening results provided for skill matching",
                "matching_results": None,
                "matching_completed": False
            }

        # Create matching prompt
        prompt = MATCHER_TASK_PROMPT.format(
            job_description=job_description,
            screening_results=screening_results
        )

        # Perform skill matching
        matching_results = self.invoke([HumanMessage(content=prompt)])

        return {
            **state,
            "matching_results": matching_results,
            "matching_completed": True,
            "current_step": state.get("current_step", 0) + 1
        }

    def match_single_candidate(
        self,
        candidate_info: str,
        job_description: str
    ) -> Dict[str, Any]:
        """
        Perform skill matching for a single candidate.

        Args:
            candidate_info: Candidate resume/profile information
            job_description: Job requirements

        Returns:
            Skill matching analysis dictionary
        """
        prompt = f"""
Perform detailed skill matching for this candidate:

JOB REQUIREMENTS:
{job_description}

CANDIDATE INFORMATION:
{candidate_info}

Evaluate across all dimensions (Technical Skills, Experience, Education, Soft Skills)
and provide the weighted overall score.
"""

        result = self.invoke([HumanMessage(content=prompt)])

        return {
            "matching_analysis": result,
            "candidate_preview": candidate_info[:200] + "..."
        }

    def compare_candidates(
        self,
        candidates: list,
        job_description: str
    ) -> str:
        """
        Compare multiple candidates side by side.

        Args:
            candidates: List of candidate information strings
            job_description: Job requirements

        Returns:
            Comparative analysis
        """
        candidates_text = "\n\n---\n\n".join(
            f"CANDIDATE {i+1}:\n{c}" for i, c in enumerate(candidates)
        )

        prompt = f"""
Compare these candidates for the following job:

JOB REQUIREMENTS:
{job_description}

CANDIDATES:
{candidates_text}

Provide a side-by-side comparison across all evaluation dimensions.
Highlight key differentiators and rank them.
"""

        return self.invoke([HumanMessage(content=prompt)])

    def identify_skill_gaps(
        self,
        matching_results: str,
        job_description: str
    ) -> str:
        """
        Identify common skill gaps across candidates.

        Args:
            matching_results: Results from skill matching
            job_description: Job requirements

        Returns:
            Analysis of common skill gaps
        """
        prompt = f"""
Analyze the skill matching results to identify common gaps:

JOB REQUIREMENTS:
{job_description}

MATCHING RESULTS:
{matching_results}

Identify:
1. Skills that most candidates lack
2. Experience gaps common to the pool
3. Recommendations for the hiring team
"""

        return self.invoke([HumanMessage(content=prompt)])
