"""Analytics service for recruitment metrics and insights."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class AnalyticsService:
    """Service for recruitment analytics and metrics."""

    def __init__(self):
        pass

    def get_hiring_funnel(
        self,
        job_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get hiring funnel metrics.

        Args:
            job_id: Optional job ID filter
            start_date: Start date
            end_date: End date

        Returns:
            Funnel metrics
        """
        # Mock data - in production, query from database
        return {
            "job_id": job_id,
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "funnel": {
                "applications": 500,
                "screened": 250,
                "assessed": 100,
                "interviewed": 50,
                "offers_made": 10,
                "offers_accepted": 8
            },
            "conversion_rates": {
                "application_to_screen": 50.0,
                "screen_to_assessment": 40.0,
                "assessment_to_interview": 50.0,
                "interview_to_offer": 20.0,
                "offer_acceptance_rate": 80.0
            }
        }

    def get_time_to_hire_metrics(
        self,
        job_id: Optional[str] = None,
        department: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get time-to-hire metrics."""
        return {
            "job_id": job_id,
            "department": department,
            "average_time_to_hire_days": 35,
            "median_time_to_hire_days": 32,
            "by_stage": {
                "application_to_screen": 3,
                "screen_to_assessment": 5,
                "assessment_to_interview": 7,
                "interview_to_offer": 14,
                "offer_to_acceptance": 6
            },
            "fastest_hire_days": 18,
            "slowest_hire_days": 67
        }

    def get_source_effectiveness(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Analyze effectiveness of different sourcing channels."""
        return {
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "sources": [
                {
                    "source": "LinkedIn",
                    "applications": 200,
                    "hires": 5,
                    "conversion_rate": 2.5,
                    "average_quality_score": 78,
                    "cost_per_hire": 3500
                },
                {
                    "source": "Indeed",
                    "applications": 150,
                    "hires": 2,
                    "conversion_rate": 1.3,
                    "average_quality_score": 65,
                    "cost_per_hire": 2000
                },
                {
                    "source": "Referrals",
                    "applications": 50,
                    "hires": 4,
                    "conversion_rate": 8.0,
                    "average_quality_score": 85,
                    "cost_per_hire": 1500
                },
                {
                    "source": "Company Website",
                    "applications": 100,
                    "hires": 1,
                    "conversion_rate": 1.0,
                    "average_quality_score": 70,
                    "cost_per_hire": 500
                }
            ],
            "best_source_by_quality": "Referrals",
            "best_source_by_cost": "Company Website",
            "best_source_by_volume": "LinkedIn"
        }

    def get_cost_per_hire(
        self,
        job_id: Optional[str] = None,
        department: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate cost per hire."""
        return {
            "job_id": job_id,
            "department": department,
            "total_cost": 25000,
            "cost_breakdown": {
                "job_board_postings": 8000,
                "assessment_tools": 2000,
                "background_checks": 1500,
                "interview_time": 10000,
                "recruiter_time": 3000,
                "other": 500
            },
            "hires_made": 3,
            "cost_per_hire": 8333,
            "industry_benchmark": 7500
        }

    def get_diversity_metrics(
        self,
        job_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get diversity hiring metrics."""
        # Note: Only aggregate anonymized data, respect privacy
        return {
            "job_id": job_id,
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "gender_distribution": {
                "applications": {"male": 60, "female": 35, "other": 5},
                "hires": {"male": 50, "female": 45, "other": 5}
            },
            "diversity_index": 75,  # 0-100 score
            "improvement_from_last_period": 5
        }

    def get_interviewer_effectiveness(
        self,
        interviewer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze interviewer effectiveness."""
        return {
            "interviewer_id": interviewer_id,
            "interviews_conducted": 45,
            "average_interview_duration": 52,
            "feedback_completion_rate": 95,
            "average_feedback_time_hours": 18,
            "candidates_recommended": 25,
            "candidates_hired": 8,
            "hire_rate_of_recommendations": 32,
            "average_candidate_rating": 3.8,
            "rating_variance": 0.8,  # Lower is more consistent
            "efficiency_score": 85
        }

    def get_candidate_experience_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Analyze candidate experience metrics."""
        return {
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "response_times": {
                "application_acknowledgment_hours": 2,
                "screening_decision_days": 5,
                "interview_scheduling_days": 3,
                "post_interview_feedback_days": 7,
                "offer_delivery_days": 2
            },
            "candidate_satisfaction": {
                "average_rating": 4.2,
                "response_rate": 65,
                "would_recommend": 78
            },
            "drop_off_rates": {
                "during_application": 15,
                "after_assessment": 10,
                "after_interview": 5,
                "offer_stage": 20
            }
        }

    def get_quality_of_hire(
        self,
        cohort_start: datetime,
        cohort_end: datetime
    ) -> Dict[str, Any]:
        """
        Measure quality of hire for a cohort.

        Note: This requires post-hire data from HRIS.
        """
        return {
            "cohort": {
                "start": cohort_start.isoformat(),
                "end": cohort_end.isoformat()
            },
            "total_hires": 25,
            "still_employed_after_90_days": 23,
            "retention_rate": 92,
            "average_performance_rating": 4.1,
            "promotion_rate": 12,
            "quality_score": 88,  # Composite score
            "hiring_manager_satisfaction": 4.3
        }

    def get_recruiter_performance(
        self,
        recruiter_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get recruiter performance metrics."""
        return {
            "recruiter_id": recruiter_id,
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "active_jobs": 8,
            "jobs_filled": 12,
            "fill_rate": 80,
            "average_time_to_fill": 32,
            "applications_sourced": 150,
            "interviews_scheduled": 45,
            "offers_extended": 15,
            "hires_made": 12,
            "offer_acceptance_rate": 80,
            "quality_of_hire_score": 85,
            "hiring_manager_satisfaction": 4.5
        }

    def get_pipeline_health(
        self,
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Assess health of hiring pipeline."""
        return {
            "job_id": job_id,
            "pipeline_status": "healthy",  # healthy, warning, critical
            "current_candidates": {
                "new_applications": 25,
                "in_screening": 15,
                "in_assessment": 8,
                "interview_scheduled": 5,
                "awaiting_decision": 3
            },
            "velocity": {
                "applications_per_day": 5,
                "screenings_per_day": 3,
                "interviews_per_week": 8
            },
            "bottlenecks": [
                {
                    "stage": "interview_scheduling",
                    "average_delay_days": 8,
                    "severity": "medium"
                }
            ],
            "estimated_time_to_fill": 28,
            "confidence_score": 75
        }

    def get_predictive_insights(
        self,
        job_id: str
    ) -> Dict[str, Any]:
        """Get AI-powered predictive insights."""
        return {
            "job_id": job_id,
            "predictions": {
                "estimated_time_to_fill": 35,
                "confidence": 78,
                "required_applications": 150,
                "estimated_cost": 22000
            },
            "recommendations": [
                "Increase budget for LinkedIn postings - historically best ROI for this role",
                "Consider lowering experience requirement from 7 to 5 years to expand pool",
                "Schedule interviews more frequently - current pace may lose candidates"
            ],
            "risk_factors": [
                {
                    "factor": "competitive_market",
                    "impact": "high",
                    "description": "Similar roles at 15% higher salary in market"
                }
            ]
        }

    def generate_executive_dashboard(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate executive summary dashboard."""
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {
                "open_positions": 25,
                "applications_received": 750,
                "interviews_conducted": 120,
                "offers_made": 18,
                "hires": 15,
                "total_recruiting_cost": 187500,
                "average_cost_per_hire": 12500,
                "average_time_to_hire": 35
            },
            "trends": {
                "applications_vs_last_period": 15,  # % change
                "time_to_hire_vs_last_period": -8,
                "cost_per_hire_vs_last_period": -5,
                "offer_acceptance_vs_last_period": 10
            },
            "top_challenges": [
                "High candidate drop-off at offer stage (20%)",
                "Extended time-to-hire for senior positions",
                "Limited diverse candidate pool for technical roles"
            ],
            "recommendations": [
                "Benchmark and adjust compensation packages",
                "Streamline interview process to reduce time-to-offer",
                "Expand sourcing to underrepresented talent communities"
            ]
        }
