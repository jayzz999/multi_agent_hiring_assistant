"""Sourcing Agent for proactive candidate discovery."""

from typing import Dict, Any, List
from langchain_core.messages import HumanMessage
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.agents.base_agent import BaseAgent
from src.prompts.sourcing_prompts import SOURCING_SYSTEM_PROMPT


class SourcingAgent(BaseAgent):
    """Agent responsible for proactive candidate sourcing and talent pool management."""

    def __init__(self):
        super().__init__(
            name="SourcingAgent",
            system_prompt=SOURCING_SYSTEM_PROMPT,
            temperature=0.7
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute sourcing strategy based on job requirements.

        Args:
            state: Current workflow state with job description

        Returns:
            Updated state with sourcing strategy
        """
        state["execution_log"] = state.get("execution_log", [])
        state["execution_log"].append(f"[{self.name}] Starting sourcing strategy creation")

        job_description = state.get("job_description", "")
        plan = state.get("plan", "")

        # Create sourcing strategy
        prompt = f"""
        Based on this job description and hiring plan, create a comprehensive sourcing strategy:

        JOB DESCRIPTION:
        {job_description}

        HIRING PLAN:
        {plan}

        Create a sourcing strategy that includes:
        1. Target candidate profiles (titles, companies, backgrounds)
        2. Boolean search strings for LinkedIn/job boards
        3. Keywords and skills to search for
        4. Recommended sourcing channels (LinkedIn, GitHub, job boards, communities)
        5. Outreach message templates
        6. Talent pool segments to target
        7. Competitor companies to source from
        8. Communities and forums where candidates congregate

        Format your response as a structured sourcing plan.
        """

        response = self.invoke([HumanMessage(content=prompt)])

        state["sourcing_strategy"] = response
        state["sourcing_completed"] = True
        state["execution_log"].append(f"[{self.name}] Sourcing strategy created")

        return state

    def generate_boolean_search(self, skills: List[str], titles: List[str]) -> str:
        """Generate LinkedIn boolean search string."""
        prompt = f"""
        Generate a LinkedIn boolean search string for:
        Skills: {', '.join(skills)}
        Titles: {', '.join(titles)}

        Use proper boolean operators (AND, OR, NOT) and parentheses.
        """
        return self.chat(prompt)

    def create_outreach_message(self, candidate_profile: str, job_description: str) -> str:
        """Create personalized outreach message."""
        prompt = f"""
        Create a personalized outreach message for this candidate:

        CANDIDATE PROFILE:
        {candidate_profile}

        JOB DESCRIPTION:
        {job_description}

        The message should:
        - Be professional yet personable
        - Highlight why they're a good fit
        - Include clear next steps
        - Be concise (under 150 words)
        """
        return self.chat(prompt)
