"""Integration with skills assessment platforms."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import uuid


class AssessmentPlatform(str, Enum):
    """Supported assessment platforms."""
    HACKERRANK = "hackerrank"
    CODILITY = "codility"
    LEETCODE = "leetcode"
    TESTGORILLA = "testgorilla"
    CRITERIA = "criteria"
    INTERNAL = "internal"


class AssessmentIntegration:
    """Integration with external assessment platforms."""

    def __init__(self):
        # Platform API credentials
        self.api_keys = {}

    def create_assessment(
        self,
        platform: AssessmentPlatform,
        assessment_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create an assessment on external platform.

        Args:
            platform: Assessment platform
            assessment_config: Assessment configuration

        Returns:
            Created assessment details
        """
        if platform == AssessmentPlatform.HACKERRANK:
            return self._create_hackerrank_test(assessment_config)
        elif platform == AssessmentPlatform.CODILITY:
            return self._create_codility_test(assessment_config)
        else:
            return self._create_internal_assessment(assessment_config)

    def _create_hackerrank_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create HackerRank test."""
        # In production, use HackerRank API
        # POST /tests

        test_id = f"hr_{uuid.uuid4().hex[:12]}"

        return {
            "test_id": test_id,
            "platform": "hackerrank",
            "test_url": f"https://www.hackerrank.com/test/{test_id}",
            "duration_minutes": config.get("duration", 90),
            "questions": config.get("questions", []),
            "created_at": datetime.now().isoformat()
        }

    def _create_codility_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create Codility test."""
        # In production, use Codility API
        test_id = f"codility_{uuid.uuid4().hex[:12]}"

        return {
            "test_id": test_id,
            "platform": "codility",
            "test_url": f"https://app.codility.com/test/{test_id}",
            "duration_minutes": config.get("duration", 120),
            "created_at": datetime.now().isoformat()
        }

    def _create_internal_assessment(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create internal assessment."""
        test_id = f"internal_{uuid.uuid4().hex[:12]}"

        return {
            "test_id": test_id,
            "platform": "internal",
            "test_url": f"https://company.com/assessments/{test_id}",
            "duration_minutes": config.get("duration", 60),
            "created_at": datetime.now().isoformat()
        }

    def send_assessment_invite(
        self,
        assessment_id: str,
        candidate_email: str,
        candidate_name: str,
        deadline: datetime,
        platform: AssessmentPlatform
    ) -> Dict[str, Any]:
        """Send assessment invitation to candidate."""
        # Platform-specific invitation
        if platform == AssessmentPlatform.HACKERRANK:
            return self._send_hackerrank_invite(assessment_id, candidate_email, deadline)
        elif platform == AssessmentPlatform.CODILITY:
            return self._send_codility_invite(assessment_id, candidate_email, deadline)
        else:
            return self._send_internal_invite(assessment_id, candidate_email, deadline)

    def _send_hackerrank_invite(
        self,
        assessment_id: str,
        candidate_email: str,
        deadline: datetime
    ) -> Dict[str, Any]:
        """Send HackerRank invite."""
        # POST /tests/{test_id}/candidates
        invite_id = f"invite_{uuid.uuid4().hex[:10]}"

        return {
            "invite_id": invite_id,
            "assessment_id": assessment_id,
            "candidate_email": candidate_email,
            "deadline": deadline.isoformat(),
            "invite_url": f"https://www.hackerrank.com/x/{invite_id}",
            "sent_at": datetime.now().isoformat(),
            "status": "sent"
        }

    def _send_codility_invite(
        self,
        assessment_id: str,
        candidate_email: str,
        deadline: datetime
    ) -> Dict[str, Any]:
        """Send Codility invite."""
        invite_id = f"invite_{uuid.uuid4().hex[:10]}"

        return {
            "invite_id": invite_id,
            "assessment_id": assessment_id,
            "candidate_email": candidate_email,
            "deadline": deadline.isoformat(),
            "sent_at": datetime.now().isoformat(),
            "status": "sent"
        }

    def _send_internal_invite(
        self,
        assessment_id: str,
        candidate_email: str,
        deadline: datetime
    ) -> Dict[str, Any]:
        """Send internal assessment invite."""
        invite_id = f"invite_{uuid.uuid4().hex[:10]}"

        return {
            "invite_id": invite_id,
            "assessment_id": assessment_id,
            "candidate_email": candidate_email,
            "test_url": f"https://company.com/assessments/{assessment_id}?token={invite_id}",
            "deadline": deadline.isoformat(),
            "sent_at": datetime.now().isoformat(),
            "status": "sent"
        }

    def get_assessment_results(
        self,
        assessment_id: str,
        platform: AssessmentPlatform
    ) -> Dict[str, Any]:
        """Get assessment results."""
        if platform == AssessmentPlatform.HACKERRANK:
            return self._get_hackerrank_results(assessment_id)
        elif platform == AssessmentPlatform.CODILITY:
            return self._get_codility_results(assessment_id)
        else:
            return self._get_internal_results(assessment_id)

    def _get_hackerrank_results(self, assessment_id: str) -> Dict[str, Any]:
        """Get HackerRank results."""
        # GET /tests/{test_id}/candidates/{candidate_id}/report

        # Mock results
        return {
            "assessment_id": assessment_id,
            "platform": "hackerrank",
            "status": "completed",
            "score": 85.5,
            "max_score": 100,
            "percentile": 78,
            "time_taken_minutes": 75,
            "questions": [
                {
                    "question_id": "q1",
                    "title": "Array Manipulation",
                    "score": 40,
                    "max_score": 40,
                    "time_taken": 25
                },
                {
                    "question_id": "q2",
                    "title": "String Algorithms",
                    "score": 45.5,
                    "max_score": 60,
                    "time_taken": 50
                }
            ],
            "plagiarism_detected": False,
            "completed_at": datetime.now().isoformat()
        }

    def _get_codility_results(self, assessment_id: str) -> Dict[str, Any]:
        """Get Codility results."""
        return {
            "assessment_id": assessment_id,
            "platform": "codility",
            "status": "completed",
            "score": 92,
            "correctness": 95,
            "performance": 89,
            "time_complexity_score": 90,
            "plagiarism_score": 5,  # lower is better
            "completed_at": datetime.now().isoformat()
        }

    def _get_internal_results(self, assessment_id: str) -> Dict[str, Any]:
        """Get internal assessment results."""
        return {
            "assessment_id": assessment_id,
            "platform": "internal",
            "status": "completed",
            "score": 88,
            "completed_at": datetime.now().isoformat()
        }

    def check_assessment_status(
        self,
        assessment_id: str,
        candidate_email: str,
        platform: AssessmentPlatform
    ) -> Dict[str, Any]:
        """Check if candidate has completed assessment."""
        # Mock statuses: invited, started, in_progress, completed, expired
        return {
            "assessment_id": assessment_id,
            "candidate_email": candidate_email,
            "status": "completed",
            "started_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            "completed_at": datetime.now().isoformat(),
            "time_remaining_minutes": 0
        }

    def get_assessment_analytics(
        self,
        assessment_id: str,
        platform: AssessmentPlatform
    ) -> Dict[str, Any]:
        """Get analytics for an assessment."""
        return {
            "assessment_id": assessment_id,
            "total_invited": 50,
            "started": 42,
            "completed": 38,
            "completion_rate": 76.0,
            "average_score": 75.5,
            "median_score": 78.0,
            "score_distribution": {
                "0-20": 2,
                "21-40": 5,
                "41-60": 12,
                "61-80": 15,
                "81-100": 4
            },
            "average_time_minutes": 82
        }
