"""Report generation for the hiring assistant."""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import os


class ReportGenerator:
    """Generate comprehensive reports for hiring workflows."""

    def __init__(self):
        """Initialize the report generator."""
        self.reports: List[Dict[str, Any]] = []

    def generate_workflow_report(
        self,
        workflow_result: Dict[str, Any],
        metrics: Optional[Dict[str, Any]] = None,
        include_details: bool = True
    ) -> str:
        """
        Generate a comprehensive workflow report.

        Args:
            workflow_result: Results from the hiring workflow
            metrics: Optional metrics data
            include_details: Include full phase details

        Returns:
            Formatted markdown report
        """
        report_parts = []

        # Header
        report_parts.append("# Hiring Workflow Report")
        report_parts.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Executive Summary
        report_parts.append("## Executive Summary")
        success = workflow_result.get("success", False)
        verdict = workflow_result.get("verdict", "N/A")

        report_parts.append(f"- **Status**: {'✅ Completed Successfully' if success else '❌ Failed'}")
        report_parts.append(f"- **Final Verdict**: {verdict}")
        report_parts.append(f"- **Revisions Required**: {workflow_result.get('revision_count', 0)}")

        if workflow_result.get("error"):
            report_parts.append(f"- **Error**: {workflow_result['error']}")

        report_parts.append("")

        # Metrics Summary
        if metrics:
            report_parts.append("## Performance Metrics")
            report_parts.append(f"- Total Execution Time: {metrics.get('total_time', 'N/A')}")
            report_parts.append(f"- Agents Executed: {metrics.get('total_executions', 'N/A')}")
            report_parts.append(f"- Success Rate: {metrics.get('success_rate', 'N/A')}")
            report_parts.append(f"- Total Tokens Used: {metrics.get('total_tokens', 'N/A')}")
            report_parts.append("")

        # Phase Details
        if include_details:
            report_parts.append("## Phase Details\n")

            # Planning
            if workflow_result.get("plan"):
                report_parts.append("### 📋 Planning Phase")
                report_parts.append("```")
                report_parts.append(self._truncate(workflow_result["plan"], 2000))
                report_parts.append("```\n")

            # Screening
            if workflow_result.get("screening_results"):
                report_parts.append("### 🔍 Screening Results")
                report_parts.append("```")
                report_parts.append(self._truncate(workflow_result["screening_results"], 2000))
                report_parts.append("```\n")

            # Matching
            if workflow_result.get("matching_results"):
                report_parts.append("### 🎯 Skill Matching Results")
                report_parts.append("```")
                report_parts.append(self._truncate(workflow_result["matching_results"], 2000))
                report_parts.append("```\n")

            # Ranking
            if workflow_result.get("ranking_results"):
                report_parts.append("### 🏆 Final Rankings")
                report_parts.append("```")
                report_parts.append(self._truncate(workflow_result["ranking_results"], 2000))
                report_parts.append("```\n")

            # Critique
            if workflow_result.get("critique"):
                report_parts.append("### ⚖️ Quality Critique")
                report_parts.append("```")
                report_parts.append(self._truncate(workflow_result["critique"], 2000))
                report_parts.append("```\n")

        # Final Recommendations
        if workflow_result.get("final_recommendations"):
            report_parts.append("## Final Recommendations")
            report_parts.append(workflow_result["final_recommendations"])
            report_parts.append("")

        # Interview Schedule
        if workflow_result.get("interview_schedule"):
            report_parts.append("## Interview Schedule")
            report_parts.append(workflow_result["interview_schedule"])
            report_parts.append("")

        # Execution Log
        if workflow_result.get("execution_log"):
            report_parts.append("## Execution Log")
            for log_entry in workflow_result["execution_log"]:
                report_parts.append(f"- {log_entry}")
            report_parts.append("")

        report = "\n".join(report_parts)
        self.reports.append({
            "type": "workflow",
            "content": report,
            "generated_at": datetime.now().isoformat()
        })

        return report

    def generate_metrics_report(
        self,
        metrics: Dict[str, Any],
        cost_info: Optional[Dict[str, float]] = None
    ) -> str:
        """
        Generate a detailed metrics report.

        Args:
            metrics: Metrics data from MetricsCollector
            cost_info: Optional cost estimation

        Returns:
            Formatted markdown report
        """
        report_parts = []

        report_parts.append("# Performance Metrics Report")
        report_parts.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Overview
        report_parts.append("## Overview")
        report_parts.append(f"- Total Executions: {metrics.get('total_executions', 0)}")
        report_parts.append(f"- Successful: {metrics.get('successful', 0)}")
        report_parts.append(f"- Failed: {metrics.get('failed', 0)}")
        report_parts.append(f"- Success Rate: {metrics.get('success_rate', 'N/A')}")
        report_parts.append("")

        # Timing
        report_parts.append("## Timing")
        report_parts.append(f"- Total Time: {metrics.get('total_time', 'N/A')}")
        report_parts.append(f"- Average per Agent: {metrics.get('avg_time_per_agent', 'N/A')}")
        report_parts.append("")

        # Token Usage
        report_parts.append("## Token Usage")
        report_parts.append(f"- Total Tokens: {metrics.get('total_tokens', 0):,}")
        report_parts.append(f"- Average per Agent: {metrics.get('avg_tokens_per_agent', 0):,}")
        report_parts.append("")

        # Cost Estimation
        if cost_info:
            report_parts.append("## Estimated Costs")
            report_parts.append(f"- Total Cost: ${cost_info.get('total_cost_usd', 0):.4f}")
            if cost_info.get("cost_per_agent"):
                report_parts.append("- By Agent:")
                for agent, cost in cost_info["cost_per_agent"].items():
                    report_parts.append(f"  - {agent}: ${cost:.4f}")
            report_parts.append("")

        # Errors
        errors = metrics.get("errors", [])
        if errors:
            report_parts.append("## Errors")
            for error in errors:
                report_parts.append(f"- **{error['agent']}**: {error['error']}")
            report_parts.append("")

        return "\n".join(report_parts)

    def generate_test_report(
        self,
        test_summary: Dict[str, Any]
    ) -> str:
        """
        Generate a robustness test report.

        Args:
            test_summary: Summary from RobustnessTests

        Returns:
            Formatted markdown report
        """
        report_parts = []

        report_parts.append("# Robustness Test Report")
        report_parts.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Summary
        report_parts.append("## Summary")
        report_parts.append(f"- Total Tests: {test_summary.get('total_tests', 0)}")
        report_parts.append(f"- Passed: {test_summary.get('passed', 0)}")
        report_parts.append(f"- Failed: {test_summary.get('failed', 0)}")
        report_parts.append(f"- Pass Rate: {test_summary.get('pass_rate', 'N/A')}")
        report_parts.append(f"- Total Duration: {test_summary.get('total_duration', 'N/A')}")
        report_parts.append("")

        # By Category
        by_category = test_summary.get("by_category", {})
        if by_category:
            report_parts.append("## Results by Category")
            for cat, results in by_category.items():
                status = "✅" if results["failed"] == 0 else "⚠️"
                report_parts.append(f"- {status} **{cat}**: {results['passed']}/{results['passed'] + results['failed']} passed")
            report_parts.append("")

        # By Severity
        by_severity = test_summary.get("by_severity", {})
        if by_severity and any(v > 0 for v in by_severity.values()):
            report_parts.append("## Failures by Severity")
            for severity, count in by_severity.items():
                if count > 0:
                    icon = "🔴" if severity == "high" else "🟡" if severity == "medium" else "🟢"
                    report_parts.append(f"- {icon} {severity.title()}: {count}")
            report_parts.append("")

        # Failed Tests Details
        failed_tests = test_summary.get("failed_tests", [])
        if failed_tests:
            report_parts.append("## Failed Tests")
            for test in failed_tests:
                report_parts.append(f"\n### {test['test_name']}")
                report_parts.append(f"- **Category**: {test.get('category', 'N/A')}")
                report_parts.append(f"- **Severity**: {test.get('severity', 'N/A')}")
                report_parts.append(f"- **Details**: {test.get('details', 'N/A')}")
                report_parts.append(f"- **Duration**: {test.get('duration', 'N/A')}")

        return "\n".join(report_parts)

    def generate_candidate_summary(
        self,
        ranking_results: str,
        num_recommended: int
    ) -> str:
        """
        Generate a simplified candidate summary for stakeholders.

        Args:
            ranking_results: Full ranking results
            num_recommended: Number of candidates recommended

        Returns:
            Simplified summary
        """
        report_parts = []

        report_parts.append("# Candidate Summary for Hiring Manager")
        report_parts.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        report_parts.append(f"**Candidates Recommended for Interview**: {num_recommended}\n")

        report_parts.append("## Ranking Overview")
        report_parts.append(ranking_results)

        report_parts.append("\n## Next Steps")
        report_parts.append("1. Review candidate profiles")
        report_parts.append("2. Confirm interview schedule")
        report_parts.append("3. Prepare interview questions (provided in full report)")
        report_parts.append("4. Schedule hiring committee review")

        return "\n".join(report_parts)

    def save_report(
        self,
        report: str,
        filename: str,
        output_dir: str = "./reports"
    ) -> str:
        """
        Save a report to file.

        Args:
            report: Report content
            filename: Output filename
            output_dir: Output directory

        Returns:
            Full path to saved file
        """
        os.makedirs(output_dir, exist_ok=True)

        # Add timestamp to filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_filename = f"{timestamp}_{filename}"

        filepath = os.path.join(output_dir, full_filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)

        return filepath

    def export_all_reports(self, output_dir: str = "./reports") -> List[str]:
        """
        Export all generated reports.

        Args:
            output_dir: Output directory

        Returns:
            List of saved file paths
        """
        saved_files = []

        for i, report in enumerate(self.reports):
            report_type = report.get("type", "general")
            filename = f"{report_type}_report_{i+1}.md"
            filepath = self.save_report(
                report["content"],
                filename,
                output_dir
            )
            saved_files.append(filepath)

        return saved_files

    def _truncate(self, text: str, max_length: int) -> str:
        """Truncate text to maximum length."""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "\n... [truncated]"
