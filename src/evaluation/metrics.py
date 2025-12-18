"""Performance metrics collection and analysis."""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import time
import json


@dataclass
class AgentMetrics:
    """Metrics for a single agent execution."""
    agent_name: str
    execution_time: float
    tokens_used: int
    success: bool
    error_message: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_name": self.agent_name,
            "execution_time": self.execution_time,
            "tokens_used": self.tokens_used,
            "success": self.success,
            "error_message": self.error_message,
            "timestamp": self.timestamp
        }


@dataclass
class WorkflowMetrics:
    """Metrics for a complete workflow execution."""
    total_time: float
    agent_metrics: List[AgentMetrics]
    revision_count: int
    final_verdict: str
    candidate_count: int
    recommended_count: int
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_time": self.total_time,
            "agent_metrics": [m.to_dict() for m in self.agent_metrics],
            "revision_count": self.revision_count,
            "final_verdict": self.final_verdict,
            "candidate_count": self.candidate_count,
            "recommended_count": self.recommended_count,
            "started_at": self.started_at,
            "completed_at": self.completed_at
        }

    def get_success_rate(self) -> float:
        """Calculate agent success rate."""
        if not self.agent_metrics:
            return 0.0
        successful = sum(1 for m in self.agent_metrics if m.success)
        return successful / len(self.agent_metrics)


class MetricsCollector:
    """Collect and analyze workflow metrics."""

    def __init__(self):
        """Initialize the metrics collector."""
        self.metrics: List[AgentMetrics] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.workflow_history: List[WorkflowMetrics] = []

    def start_workflow(self):
        """Mark workflow start."""
        self.start_time = time.time()
        self.metrics = []

    def end_workflow(self):
        """Mark workflow end."""
        self.end_time = time.time()

    def record_agent_execution(
        self,
        agent_name: str,
        execution_time: float,
        tokens_used: int,
        success: bool,
        error_message: Optional[str] = None
    ):
        """
        Record metrics for an agent execution.

        Args:
            agent_name: Name of the agent
            execution_time: Time taken in seconds
            tokens_used: Estimated token count
            success: Whether execution succeeded
            error_message: Error message if failed
        """
        self.metrics.append(AgentMetrics(
            agent_name=agent_name,
            execution_time=execution_time,
            tokens_used=tokens_used,
            success=success,
            error_message=error_message
        ))

    def get_workflow_metrics(
        self,
        revision_count: int = 0,
        final_verdict: str = "N/A",
        candidate_count: int = 0,
        recommended_count: int = 0
    ) -> WorkflowMetrics:
        """
        Get complete workflow metrics.

        Args:
            revision_count: Number of revisions
            final_verdict: Final critic verdict
            candidate_count: Number of candidates processed
            recommended_count: Number recommended for interview

        Returns:
            WorkflowMetrics object
        """
        total_time = 0.0
        if self.start_time and self.end_time:
            total_time = self.end_time - self.start_time

        workflow_metrics = WorkflowMetrics(
            total_time=total_time,
            agent_metrics=self.metrics.copy(),
            revision_count=revision_count,
            final_verdict=final_verdict,
            candidate_count=candidate_count,
            recommended_count=recommended_count,
            completed_at=datetime.now().isoformat()
        )

        self.workflow_history.append(workflow_metrics)
        return workflow_metrics

    def get_summary(self) -> Dict[str, Any]:
        """
        Get metrics summary.

        Returns:
            Summary dictionary
        """
        if not self.metrics:
            return {"message": "No metrics recorded"}

        successful = [m for m in self.metrics if m.success]
        failed = [m for m in self.metrics if not m.success]
        total_time = sum(m.execution_time for m in self.metrics)
        total_tokens = sum(m.tokens_used for m in self.metrics)

        return {
            "total_executions": len(self.metrics),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": f"{(len(successful) / len(self.metrics)) * 100:.1f}%",
            "total_time": f"{total_time:.2f}s",
            "avg_time_per_agent": f"{total_time / len(self.metrics):.2f}s",
            "total_tokens": total_tokens,
            "avg_tokens_per_agent": total_tokens // len(self.metrics),
            "agents_executed": [m.agent_name for m in self.metrics],
            "errors": [
                {"agent": m.agent_name, "error": m.error_message}
                for m in failed
            ]
        }

    def get_agent_performance(self) -> Dict[str, Dict[str, Any]]:
        """
        Get performance breakdown by agent.

        Returns:
            Dictionary mapping agent names to their performance stats
        """
        agent_stats: Dict[str, Dict[str, Any]] = {}

        for metric in self.metrics:
            name = metric.agent_name
            if name not in agent_stats:
                agent_stats[name] = {
                    "executions": 0,
                    "successful": 0,
                    "failed": 0,
                    "total_time": 0.0,
                    "total_tokens": 0,
                    "errors": []
                }

            stats = agent_stats[name]
            stats["executions"] += 1
            stats["total_time"] += metric.execution_time
            stats["total_tokens"] += metric.tokens_used

            if metric.success:
                stats["successful"] += 1
            else:
                stats["failed"] += 1
                if metric.error_message:
                    stats["errors"].append(metric.error_message)

        # Calculate averages
        for name, stats in agent_stats.items():
            if stats["executions"] > 0:
                stats["avg_time"] = stats["total_time"] / stats["executions"]
                stats["success_rate"] = stats["successful"] / stats["executions"]

        return agent_stats

    def export_to_json(self, filepath: str):
        """
        Export metrics to JSON file.

        Args:
            filepath: Path to output file
        """
        data = {
            "summary": self.get_summary(),
            "agent_performance": self.get_agent_performance(),
            "workflow_history": [w.to_dict() for w in self.workflow_history],
            "raw_metrics": [m.to_dict() for m in self.metrics]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def reset(self):
        """Reset all metrics."""
        self.metrics = []
        self.start_time = None
        self.end_time = None

    def get_cost_estimate(self, cost_per_1k_tokens: float = 0.002) -> Dict[str, float]:
        """
        Estimate API costs based on token usage.

        Args:
            cost_per_1k_tokens: Cost per 1000 tokens (default for GPT-4o-mini)

        Returns:
            Cost breakdown dictionary
        """
        total_tokens = sum(m.tokens_used for m in self.metrics)
        total_cost = (total_tokens / 1000) * cost_per_1k_tokens

        agent_costs = {}
        for metric in self.metrics:
            name = metric.agent_name
            agent_cost = (metric.tokens_used / 1000) * cost_per_1k_tokens
            agent_costs[name] = agent_costs.get(name, 0) + agent_cost

        return {
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 4),
            "cost_per_agent": {k: round(v, 4) for k, v in agent_costs.items()}
        }
