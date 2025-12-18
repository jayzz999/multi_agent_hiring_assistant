"""Candidate Ranker Agent for final ranking and recommendations."""

from typing import Any, Dict, List
from langchain_core.messages import HumanMessage
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.agents.base_agent import BaseAgent
from src.prompts.ranker_prompts import RANKER_SYSTEM_PROMPT, RANKER_TASK_PROMPT


class CandidateRankerAgent(BaseAgent):
    """
    Candidate Ranker Agent that creates final rankings and recommendations.

    This executor agent synthesizes all prior evaluations into actionable
    hiring decisions and interview recommendations.
    """

    def __init__(self):
        """Initialize the Candidate Ranker Agent."""
        super().__init__(
            name="Candidate Ranker",
            system_prompt=RANKER_SYSTEM_PROMPT,
            temperature=0.1  # Very low temperature for consistent ranking
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rank candidates and provide final recommendations.

        Args:
            state: Current workflow state containing:
                - job_description: The job requirements
                - matching_results: Results from Skill Matcher
                - num_to_interview: Number of candidates to recommend

        Returns:
            Updated state with:
                - ranking_results: Final rankings and recommendations
                - ranking_completed: True
                - current_step: Incremented
        """
        job_description = state.get("job_description", "")
        matching_results = state.get("matching_results", "")
        num_to_interview = state.get("num_to_interview", 3)

        if not matching_results:
            return {
                **state,
                "error": "No matching results provided for ranking",
                "ranking_results": None,
                "ranking_completed": False
            }

        # Create ranking prompt
        prompt = RANKER_TASK_PROMPT.format(
            job_description=job_description,
            matching_results=matching_results,
            num_to_interview=num_to_interview
        )

        # Perform ranking
        ranking_results = self.invoke([HumanMessage(content=prompt)])

        return {
            **state,
            "ranking_results": ranking_results,
            "ranking_completed": True,
            "current_step": state.get("current_step", 0) + 1
        }

    def rank_candidates(
        self,
        candidates_data: List[Dict[str, Any]],
        job_description: str,
        num_to_recommend: int = 3
    ) -> str:
        """
        Rank a list of candidates with structured data.

        Args:
            candidates_data: List of candidate dictionaries with scores
            job_description: Job requirements
            num_to_recommend: Number of candidates to recommend

        Returns:
            Ranking analysis and recommendations
        """
        candidates_text = "\n\n".join(
            f"Candidate: {c.get('name', f'Candidate {i+1}')}\n"
            f"Overall Score: {c.get('score', 'N/A')}\n"
            f"Technical: {c.get('technical_score', 'N/A')}\n"
            f"Experience: {c.get('experience_score', 'N/A')}\n"
            f"Notes: {c.get('notes', 'No notes')}"
            for i, c in enumerate(candidates_data)
        )

        prompt = f"""
Rank these candidates and provide recommendations:

JOB REQUIREMENTS:
{job_description}

CANDIDATES:
{candidates_text}

Recommend the top {num_to_recommend} candidates for interviews.
"""

        return self.invoke([HumanMessage(content=prompt)])

    def generate_interview_questions(
        self,
        candidate_info: str,
        job_description: str,
        focus_areas: List[str] = None
    ) -> str:
        """
        Generate targeted interview questions for a candidate.

        Args:
            candidate_info: Candidate's profile/resume
            job_description: Job requirements
            focus_areas: Specific areas to probe

        Returns:
            List of interview questions
        """
        focus_text = ", ".join(focus_areas) if focus_areas else "general fit"

        prompt = f"""
Generate targeted interview questions for this candidate:

JOB REQUIREMENTS:
{job_description}

CANDIDATE:
{candidate_info}

FOCUS AREAS: {focus_text}

Provide:
1. 3-5 technical questions
2. 2-3 behavioral questions
3. 2-3 questions to address potential concerns
"""

        return self.invoke([HumanMessage(content=prompt)])

    def create_hiring_summary(
        self,
        ranking_results: str,
        job_description: str
    ) -> str:
        """
        Create an executive summary of the hiring process.

        Args:
            ranking_results: Full ranking results
            job_description: Job requirements

        Returns:
            Executive summary for stakeholders
        """
        prompt = f"""
Create an executive summary of this hiring round:

JOB DESCRIPTION:
{job_description}

RANKING RESULTS:
{ranking_results}

Provide a concise summary suitable for hiring managers including:
1. Key findings (2-3 sentences)
2. Top recommendations (names and brief justification)
3. Next steps
4. Any concerns or notes
"""

        return self.invoke([HumanMessage(content=prompt)])
