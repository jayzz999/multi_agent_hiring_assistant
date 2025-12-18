"""Pytest configuration and fixtures."""

import pytest
import tempfile
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_job_description():
    """Return a sample job description for testing."""
    return """
    Senior Python Developer

    We are looking for an experienced Python developer to join our team.

    Requirements:
    - 5+ years of Python development experience
    - Strong knowledge of Django or FastAPI
    - Experience with PostgreSQL and Redis
    - Familiarity with AWS services
    - Experience with Docker and Kubernetes

    Responsibilities:
    - Design and implement scalable APIs
    - Write clean, maintainable code
    - Participate in code reviews
    - Mentor junior developers
    """


@pytest.fixture
def sample_resume():
    """Return a sample resume for testing."""
    return """
    John Smith
    Senior Software Engineer
    john.smith@email.com | (555) 123-4567

    EXPERIENCE
    Senior Developer at TechCorp (2020-Present)
    - Built Python APIs with FastAPI
    - Managed PostgreSQL databases
    - Deployed to AWS using Docker

    Software Engineer at StartupXYZ (2017-2020)
    - Django web development
    - Redis caching implementation

    SKILLS
    Python, Django, FastAPI, PostgreSQL, Redis, AWS, Docker

    EDUCATION
    BS Computer Science, State University, 2017
    """


@pytest.fixture
def temp_directory():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_state():
    """Return a sample hiring state for testing."""
    from src.orchestration.state import create_initial_state

    return create_initial_state(
        job_description="Senior Python Developer with 5 years experience",
        num_candidates=10,
        num_to_interview=3,
        special_requirements="AWS experience required"
    )


@pytest.fixture
def completed_state():
    """Return a state that simulates completed workflow."""
    from src.orchestration.state import create_initial_state

    state = create_initial_state(
        job_description="Senior Python Developer",
        num_candidates=5,
        num_to_interview=2
    )

    state.update({
        "plan": "Detailed hiring plan...",
        "plan_created": True,
        "screening_results": "Screening results...",
        "screening_completed": True,
        "matching_results": "Matching results...",
        "matching_completed": True,
        "ranking_results": "Ranking results...",
        "ranking_completed": True,
        "critique": "Critique results...",
        "verdict": "APPROVE",
        "critique_completed": True,
        "completed": True,
        "final_recommendations": "Top candidates..."
    })

    return state


# Markers for different test categories
def pytest_configure(config):
    """Add custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "api: marks tests that require API calls"
    )
