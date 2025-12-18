"""Robustness testing for the hiring assistant."""

from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field
import time
import traceback
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


@dataclass
class TestResult:
    """Result of a single robustness test."""
    test_name: str
    passed: bool
    details: str
    duration: float
    severity: str = "medium"  # low, medium, high
    category: str = "general"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "test_name": self.test_name,
            "passed": self.passed,
            "details": self.details,
            "duration": f"{self.duration:.3f}s",
            "severity": self.severity,
            "category": self.category
        }


@dataclass
class TestSuite:
    """Collection of test results."""
    name: str
    results: List[TestResult] = field(default_factory=list)
    started_at: str = ""
    completed_at: str = ""

    def add_result(self, result: TestResult):
        """Add a test result."""
        self.results.append(result)

    def get_summary(self) -> Dict[str, Any]:
        """Get test suite summary."""
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)

        return {
            "suite_name": self.name,
            "total_tests": len(self.results),
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{(passed / len(self.results) * 100) if self.results else 0:.1f}%",
            "failed_tests": [r.test_name for r in self.results if not r.passed],
            "high_severity_failures": [
                r.test_name for r in self.results
                if not r.passed and r.severity == "high"
            ]
        }


class RobustnessTests:
    """Robustness testing suite for the hiring assistant."""

    def __init__(self, orchestrator=None):
        """
        Initialize robustness tests.

        Args:
            orchestrator: HiringOrchestrator instance to test
        """
        self.orchestrator = orchestrator
        self.results: List[TestResult] = []
        self.test_suites: List[TestSuite] = []

    def run_all_tests(self, skip_api_tests: bool = False) -> List[TestResult]:
        """
        Run all robustness tests.

        Args:
            skip_api_tests: Skip tests that require API calls

        Returns:
            List of test results
        """
        self.results = []

        # Input validation tests
        self.results.append(self.test_empty_job_description())
        self.results.append(self.test_very_short_input())
        self.results.append(self.test_very_long_input())
        self.results.append(self.test_special_characters())
        self.results.append(self.test_unicode_input())
        self.results.append(self.test_invalid_num_candidates())

        # State validation tests
        self.results.append(self.test_invalid_state())
        self.results.append(self.test_missing_required_fields())

        # Edge case tests
        self.results.append(self.test_zero_candidates())
        self.results.append(self.test_more_interviews_than_candidates())

        if not skip_api_tests and self.orchestrator:
            self.results.append(self.test_basic_workflow())

        return self.results

    def test_empty_job_description(self) -> TestResult:
        """Test handling of empty job description."""
        start = time.time()

        try:
            from src.orchestration.state import validate_state, create_initial_state

            state = create_initial_state(job_description="")
            errors = validate_state(state)

            passed = len(errors) > 0 and "description" in str(errors).lower()
            details = "Correctly identified empty job description" if passed else "Failed to catch empty input"

        except Exception as e:
            passed = True  # Exception is acceptable for invalid input
            details = f"Raised exception as expected: {str(e)[:100]}"

        return TestResult(
            test_name="Empty Job Description",
            passed=passed,
            details=details,
            duration=time.time() - start,
            severity="high",
            category="input_validation"
        )

    def test_very_short_input(self) -> TestResult:
        """Test handling of very short job description."""
        start = time.time()

        try:
            from src.orchestration.state import create_initial_state

            # Very short but technically valid
            state = create_initial_state(job_description="Dev")
            passed = state.get("job_description") == "Dev"
            details = "Accepted very short input (may need validation)" if passed else "Rejected short input"

        except Exception as e:
            passed = False
            details = f"Unexpected error: {str(e)[:100]}"

        return TestResult(
            test_name="Very Short Input",
            passed=passed,
            details=details,
            duration=time.time() - start,
            severity="low",
            category="input_validation"
        )

    def test_very_long_input(self) -> TestResult:
        """Test handling of very long job description."""
        start = time.time()

        try:
            from src.orchestration.state import create_initial_state

            # Create a very long job description (50KB)
            long_jd = "Looking for a Python developer. " * 2000
            state = create_initial_state(job_description=long_jd)

            passed = len(state.get("job_description", "")) == len(long_jd)
            details = f"Handled {len(long_jd)} character input successfully"

        except Exception as e:
            passed = False
            details = f"Failed with long input: {str(e)[:100]}"

        return TestResult(
            test_name="Very Long Input",
            passed=passed,
            details=details,
            duration=time.time() - start,
            severity="medium",
            category="input_validation"
        )

    def test_special_characters(self) -> TestResult:
        """Test handling of special characters in input."""
        start = time.time()

        try:
            from src.orchestration.state import create_initial_state

            special_jd = "Looking for developer with C++ & C# skills. Salary: $100k-$150k. Email: test@company.com"
            state = create_initial_state(job_description=special_jd)

            passed = state.get("job_description") == special_jd
            details = "Handled special characters correctly" if passed else "Issues with special characters"

        except Exception as e:
            passed = False
            details = f"Error with special characters: {str(e)[:100]}"

        return TestResult(
            test_name="Special Characters",
            passed=passed,
            details=details,
            duration=time.time() - start,
            severity="medium",
            category="input_validation"
        )

    def test_unicode_input(self) -> TestResult:
        """Test handling of unicode characters."""
        start = time.time()

        try:
            from src.orchestration.state import create_initial_state

            unicode_jd = "Développeur Python recherché. 日本語スキル歓迎. Зарплата: €80k"
            state = create_initial_state(job_description=unicode_jd)

            passed = state.get("job_description") == unicode_jd
            details = "Handled unicode correctly" if passed else "Issues with unicode"

        except Exception as e:
            passed = False
            details = f"Error with unicode: {str(e)[:100]}"

        return TestResult(
            test_name="Unicode Input",
            passed=passed,
            details=details,
            duration=time.time() - start,
            severity="medium",
            category="input_validation"
        )

    def test_invalid_num_candidates(self) -> TestResult:
        """Test handling of invalid number of candidates."""
        start = time.time()

        try:
            from src.orchestration.state import validate_state, create_initial_state

            state = create_initial_state(
                job_description="Valid job description here",
                num_candidates=-5
            )
            errors = validate_state(state)

            passed = len(errors) > 0
            details = "Correctly caught negative candidates" if passed else "Did not validate negative number"

        except Exception as e:
            passed = True
            details = f"Raised exception for invalid input: {str(e)[:100]}"

        return TestResult(
            test_name="Invalid Candidate Count",
            passed=passed,
            details=details,
            duration=time.time() - start,
            severity="high",
            category="input_validation"
        )

    def test_invalid_state(self) -> TestResult:
        """Test handling of invalid state structure."""
        start = time.time()

        try:
            from src.orchestration.state import validate_state

            # Create an invalid state dict
            invalid_state = {
                "job_description": None,
                "num_candidates": "not a number"
            }

            errors = validate_state(invalid_state)
            passed = len(errors) > 0
            details = f"Found {len(errors)} validation errors" if passed else "No validation errors found"

        except Exception as e:
            passed = True
            details = f"Properly handled invalid state: {str(e)[:100]}"

        return TestResult(
            test_name="Invalid State Structure",
            passed=passed,
            details=details,
            duration=time.time() - start,
            severity="high",
            category="state_validation"
        )

    def test_missing_required_fields(self) -> TestResult:
        """Test handling of missing required fields."""
        start = time.time()

        try:
            from src.orchestration.state import validate_state

            incomplete_state = {}
            errors = validate_state(incomplete_state)

            passed = len(errors) > 0
            details = f"Caught {len(errors)} missing fields" if passed else "Did not catch missing fields"

        except Exception as e:
            passed = True
            details = f"Handled missing fields: {str(e)[:100]}"

        return TestResult(
            test_name="Missing Required Fields",
            passed=passed,
            details=details,
            duration=time.time() - start,
            severity="high",
            category="state_validation"
        )

    def test_zero_candidates(self) -> TestResult:
        """Test handling of zero candidates."""
        start = time.time()

        try:
            from src.orchestration.state import validate_state, create_initial_state

            state = create_initial_state(
                job_description="Valid job",
                num_candidates=0
            )
            errors = validate_state(state)

            passed = len(errors) > 0
            details = "Correctly caught zero candidates" if passed else "Accepted zero candidates"

        except Exception as e:
            passed = True
            details = f"Handled zero candidates: {str(e)[:100]}"

        return TestResult(
            test_name="Zero Candidates",
            passed=passed,
            details=details,
            duration=time.time() - start,
            severity="medium",
            category="edge_case"
        )

    def test_more_interviews_than_candidates(self) -> TestResult:
        """Test when interview count exceeds candidate count."""
        start = time.time()

        try:
            from src.orchestration.state import validate_state, create_initial_state

            state = create_initial_state(
                job_description="Valid job",
                num_candidates=3,
                num_to_interview=10
            )
            errors = validate_state(state)

            passed = len(errors) > 0
            details = "Caught inconsistent counts" if passed else "Accepted invalid interview count"

        except Exception as e:
            passed = True
            details = f"Handled invalid counts: {str(e)[:100]}"

        return TestResult(
            test_name="Interview Count Exceeds Candidates",
            passed=passed,
            details=details,
            duration=time.time() - start,
            severity="medium",
            category="edge_case"
        )

    def test_basic_workflow(self) -> TestResult:
        """Test basic workflow execution (requires API)."""
        start = time.time()

        if not self.orchestrator:
            return TestResult(
                test_name="Basic Workflow",
                passed=False,
                details="No orchestrator provided",
                duration=time.time() - start,
                severity="high",
                category="integration"
            )

        try:
            result = self.orchestrator.run(
                job_description="Senior Python Developer with 5 years experience",
                num_candidates=5,
                num_to_interview=2
            )

            passed = result.get("success", False) or result.get("plan") is not None
            details = "Workflow executed successfully" if passed else f"Workflow failed: {result.get('error', 'Unknown')}"

        except Exception as e:
            passed = False
            details = f"Workflow exception: {str(e)[:200]}"

        return TestResult(
            test_name="Basic Workflow",
            passed=passed,
            details=details,
            duration=time.time() - start,
            severity="high",
            category="integration"
        )

    def get_summary(self) -> Dict[str, Any]:
        """Get test summary."""
        if not self.results:
            return {"message": "No tests run"}

        passed = [r for r in self.results if r.passed]
        failed = [r for r in self.results if not r.passed]

        return {
            "total_tests": len(self.results),
            "passed": len(passed),
            "failed": len(failed),
            "pass_rate": f"{(len(passed) / len(self.results)) * 100:.1f}%",
            "total_duration": f"{sum(r.duration for r in self.results):.2f}s",
            "failed_tests": [r.to_dict() for r in failed],
            "by_category": self._group_by_category(),
            "by_severity": self._group_by_severity()
        }

    def _group_by_category(self) -> Dict[str, Dict]:
        """Group results by category."""
        categories: Dict[str, Dict] = {}
        for result in self.results:
            cat = result.category
            if cat not in categories:
                categories[cat] = {"passed": 0, "failed": 0}
            if result.passed:
                categories[cat]["passed"] += 1
            else:
                categories[cat]["failed"] += 1
        return categories

    def _group_by_severity(self) -> Dict[str, int]:
        """Group failures by severity."""
        failures = [r for r in self.results if not r.passed]
        return {
            "high": sum(1 for r in failures if r.severity == "high"),
            "medium": sum(1 for r in failures if r.severity == "medium"),
            "low": sum(1 for r in failures if r.severity == "low")
        }
