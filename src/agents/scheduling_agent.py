"""Scheduling Agent for interview coordination and calendar management."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from langchain_core.messages import HumanMessage
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.agents.base_agent import BaseAgent
from src.prompts.scheduling_prompts import SCHEDULING_SYSTEM_PROMPT


class SchedulingAgent(BaseAgent):
    """Agent responsible for interview scheduling and calendar coordination."""

    def __init__(self):
        super().__init__(
            name="SchedulingAgent",
            system_prompt=SCHEDULING_SYSTEM_PROMPT,
            temperature=0.3
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute scheduling tasks.

        Args:
            state: Current workflow state

        Returns:
            Updated state with scheduling information
        """
        state["execution_log"] = state.get("execution_log", [])
        state["execution_log"].append(f"[{self.name}] Processing interview scheduling")

        # Get candidates to interview
        ranking_results = state.get("ranking_results", "")

        prompt = f"""
        Based on these candidate rankings, create an interview scheduling plan:

        RANKINGS:
        {ranking_results}

        Create a plan that includes:
        1. Recommended interview sequence (phone screen, technical, panel, etc.)
        2. Suggested duration for each interview type
        3. Recommended interviewers based on role requirements
        4. Time buffer recommendations
        5. Interview guide suggestions

        Output a structured scheduling plan.
        """

        response = self.invoke([HumanMessage(content=prompt)])

        state["interview_schedule"] = response
        state["scheduling_completed"] = True
        state["execution_log"].append(f"[{self.name}] Interview schedule created")

        return state

    def find_available_slots(
        self,
        interviewer_calendars: List[Dict[str, Any]],
        candidate_availability: List[Dict[str, Any]],
        duration_minutes: int = 60,
        buffer_minutes: int = 15
    ) -> List[datetime]:
        """
        Find available time slots for all participants.

        Args:
            interviewer_calendars: List of interviewer availability
            candidate_availability: Candidate's available times
            duration_minutes: Interview duration
            buffer_minutes: Buffer between meetings

        Returns:
            List of available datetime slots
        """
        # This would integrate with calendar APIs (Google Calendar, Outlook)
        # For now, return mock implementation
        available_slots = []

        # Logic would:
        # 1. Get busy times for all interviewers
        # 2. Find common free time
        # 3. Check candidate availability
        # 4. Return slots with buffer

        return available_slots

    def create_interview_panel(
        self,
        job_requirements: Dict[str, Any],
        available_interviewers: List[Dict[str, Any]],
        interview_type: str = "technical"
    ) -> List[str]:
        """
        Create an optimal interview panel.

        Args:
            job_requirements: Job requirements and skills needed
            available_interviewers: Pool of available interviewers
            interview_type: Type of interview

        Returns:
            List of recommended interviewer IDs
        """
        prompt = f"""
        Create an optimal interview panel for:

        JOB REQUIREMENTS:
        {job_requirements}

        AVAILABLE INTERVIEWERS:
        {available_interviewers}

        INTERVIEW TYPE: {interview_type}

        Consider:
        - Skills match with job requirements
        - Diversity in panel composition
        - Seniority mix
        - Department representation
        - Workload distribution

        Return interviewer IDs and rationale.
        """

        response = self.chat(prompt)
        # Parse response and extract IDs
        return []

    def optimize_interview_order(
        self,
        candidates: List[Dict[str, Any]],
        constraints: Dict[str, Any]
    ) -> List[str]:
        """
        Optimize the order of candidate interviews.

        Args:
            candidates: List of candidates to interview
            constraints: Scheduling constraints

        Returns:
            Ordered list of candidate IDs
        """
        prompt = f"""
        Optimize interview order for these candidates:

        CANDIDATES:
        {candidates}

        CONSTRAINTS:
        {constraints}

        Consider:
        - Candidate availability
        - Urgency/priority
        - Interviewer fatigue (don't schedule all back-to-back)
        - Mix of strong and medium candidates
        - Time zones

        Return optimized order with reasoning.
        """

        response = self.chat(prompt)
        return []

    def detect_scheduling_conflicts(
        self,
        proposed_schedule: List[Dict[str, Any]]
    ) -> List[str]:
        """Detect conflicts in proposed schedule."""
        conflicts = []

        # Check for:
        # - Overlapping interviews for same interviewer
        # - Insufficient buffer time
        # - Outside working hours
        # - Interviewer workload too high

        return conflicts

    def suggest_reschedule_options(
        self,
        original_time: datetime,
        reason: str,
        participant_availability: List[Dict[str, Any]]
    ) -> List[datetime]:
        """Suggest alternative times for rescheduling."""
        # Find alternative slots based on availability
        return []
