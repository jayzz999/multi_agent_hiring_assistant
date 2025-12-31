"""Streamlit UI for the Multi-Agent Hiring Assistant."""

# Load environment variables FIRST
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import requests
import time
import json
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Page configuration
st.set_page_config(
    page_title="Multi-Agent Hiring Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .agent-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ddd;
        margin: 0.5rem 0;
    }
    .status-running {
        color: #f0ad4e;
    }
    .status-completed {
        color: #5cb85c;
    }
    .status-failed {
        color: #d9534f;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        color: #000000;
    }
    .metric-card h3, .metric-card h4, .metric-card p {
        color: #000000;
    }
</style>
""", unsafe_allow_html=True)


def check_api_health():
    """Check if the API is healthy."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except requests.exceptions.Timeout:
        # API is running but busy - still consider it healthy
        return True
    except:
        return False


def main():
    """Main Streamlit application."""

    # Initialize session state for navigation
    if "nav_page" not in st.session_state:
        st.session_state.nav_page = "🏠 Home"

    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50?text=Hiring+AI", width=150)
        st.markdown("---")

        # Navigation options
        nav_options = ["🏠 Home", "📋 New Workflow", "📊 Results", "📁 Documents", "⚙️ Settings"]

        # Get current index based on session state
        current_index = nav_options.index(st.session_state.nav_page) if st.session_state.nav_page in nav_options else 0

        # Navigation
        page = st.radio(
            "Navigation",
            nav_options,
            index=current_index,
            label_visibility="collapsed",
            key="nav_radio"
        )

        # Update session state when radio changes
        if page != st.session_state.nav_page:
            st.session_state.nav_page = page

        st.markdown("---")

        # API Status
        api_healthy = check_api_health()
        if api_healthy:
            st.success("✅ API Connected")
        else:
            st.error("❌ API Disconnected")
            st.info("Start the API with:\n`uvicorn api.main:app --reload`")

        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        Multi-Agent Hiring Assistant uses AI agents to automate:
        - Resume screening
        - Skill matching
        - Candidate ranking
        - Interview scheduling
        """)

    # Main content based on navigation
    if st.session_state.nav_page == "🏠 Home":
        show_home_page()
    elif st.session_state.nav_page == "📋 New Workflow":
        show_workflow_page()
    elif st.session_state.nav_page == "📊 Results":
        show_results_page()
    elif st.session_state.nav_page == "📁 Documents":
        show_documents_page()
    elif st.session_state.nav_page == "⚙️ Settings":
        show_settings_page()


def show_home_page():
    """Display the home page."""
    st.markdown("# 🤖 Multi-Agent Hiring Assistant")
    st.markdown("### Automate your hiring workflow with AI-powered agents")

    st.markdown("---")

    # Feature cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📋</h3>
            <h4>Planning</h4>
            <p>AI analyzes job requirements</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>🔍</h3>
            <h4>Screening</h4>
            <p>Automated resume review</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯</h3>
            <h4>Matching</h4>
            <p>Skill-based evaluation</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>🏆</h3>
            <h4>Ranking</h4>
            <p>Final recommendations</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Quick actions
    st.markdown("### Quick Actions")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🚀 Start New Workflow", use_container_width=True):
            st.session_state.nav_page = "📋 New Workflow"
            st.rerun()

    with col2:
        if st.button("📁 Upload Resumes", use_container_width=True):
            st.session_state.nav_page = "📁 Documents"
            st.rerun()

    with col3:
        if st.button("📊 View Results", use_container_width=True):
            st.session_state.nav_page = "📊 Results"
            st.rerun()

    # Recent activity
    st.markdown("---")
    st.markdown("### Recent Activity")

    try:
        response = requests.get(f"{API_URL}/api/v1/jobs", timeout=5)
        if response.status_code == 200:
            jobs = response.json().get("jobs", [])
            if jobs:
                for job in jobs[-5:]:  # Show last 5
                    status_icon = "🟡" if job["status"] == "running" else "🟢" if job["status"] == "completed" else "🔴"
                    st.markdown(f"{status_icon} **Job {job['job_id']}** - {job['status']} ({job.get('started_at', 'N/A')})")
            else:
                st.info("No recent workflows. Start a new one!")
        else:
            st.warning("Could not fetch recent activity")
    except:
        st.info("Connect to API to see recent activity")


def show_workflow_page():
    """Display the workflow creation page."""
    st.markdown("# 📋 New Hiring Workflow")

    # Job Description Input
    st.markdown("### Job Description")
    job_description = st.text_area(
        "Enter the job description",
        height=200,
        placeholder="Paste the full job description here...",
        help="Include required skills, experience, responsibilities, and qualifications"
    )

    # Configuration
    st.markdown("### Configuration")
    col1, col2 = st.columns(2)

    with col1:
        num_candidates = st.number_input(
            "Number of Candidates to Process",
            min_value=1,
            max_value=100,
            value=10,
            help="Expected number of candidates in the pool"
        )

    with col2:
        num_to_interview = st.number_input(
            "Candidates to Recommend for Interview",
            min_value=1,
            max_value=20,
            value=3,
            help="How many top candidates to recommend"
        )

    special_requirements = st.text_input(
        "Special Requirements (optional)",
        placeholder="Any special considerations for this role..."
    )

    st.markdown("---")

    # Submit button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Hiring Workflow", use_container_width=True, type="primary"):
            if len(job_description) < 50:
                st.error("Please enter a more detailed job description (at least 50 characters)")
            else:
                with st.spinner("Starting workflow..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/api/v1/workflow/start",
                            json={
                                "job_description": job_description,
                                "num_candidates": num_candidates,
                                "num_to_interview": num_to_interview,
                                "special_requirements": special_requirements or None
                            },
                            timeout=10
                        )

                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ Workflow started! Job ID: {result['job_id']}")
                            st.session_state.current_job_id = result['job_id']

                            # Show progress
                            show_workflow_progress(result['job_id'])
                        else:
                            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

                    except requests.exceptions.Timeout:
                        st.warning("⏳ Workflow is processing in the background. This may take 2-3 minutes.")
                        st.info("Check the **Results** page to see when it completes.")
                        # Try to fetch the latest job ID
                        try:
                            jobs_response = requests.get(f"{API_URL}/api/v1/jobs", timeout=5)
                            if jobs_response.status_code == 200:
                                jobs = jobs_response.json().get("jobs", [])
                                if jobs:
                                    latest_job = jobs[-1]
                                    st.session_state.current_job_id = latest_job['job_id']
                                    st.info(f"Job ID: {latest_job['job_id']} - Status: {latest_job['status']}")
                                    show_workflow_progress(latest_job['job_id'])
                        except:
                            pass
                    except requests.exceptions.ConnectionError:
                        st.error("Could not connect to API. Please ensure the server is running.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    # Example job description
    with st.expander("📝 Example Job Description"):
        st.markdown("""
        **Senior Python Developer**

        We are looking for an experienced Python developer to join our team.

        **Requirements:**
        - 5+ years of Python development experience
        - Strong knowledge of Django or FastAPI
        - Experience with PostgreSQL and Redis
        - Familiarity with AWS services
        - Experience with Docker and Kubernetes
        - Strong problem-solving skills

        **Responsibilities:**
        - Design and implement scalable APIs
        - Write clean, maintainable code
        - Participate in code reviews
        - Mentor junior developers

        **Nice to have:**
        - Machine learning experience
        - Open source contributions
        """)


def show_workflow_progress(job_id: str):
    """Show real-time workflow progress."""
    st.markdown("---")
    st.markdown("### Workflow Progress")

    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    details_placeholder = st.empty()

    phases = ["Planning", "Screening", "Matching", "Ranking", "Critique", "Finalization"]

    # Poll for updates
    max_polls = 180  # 6 minutes max (workflows can take 2-3 minutes with revisions)
    poll_count = 0
    consecutive_failures = 0

    while poll_count < max_polls:
        try:
            response = requests.get(f"{API_URL}/api/v1/workflow/status/{job_id}", timeout=3)
            if response.status_code == 200:
                consecutive_failures = 0  # Reset on success
                result = response.json()
                status = result.get("status", "unknown")

                if status == "running":
                    # Update progress bar with time-based estimate
                    progress = min(poll_count / 60, 0.9)  # Cap at 90% while running
                    progress_placeholder.progress(progress, text=f"Processing... ({int(progress * 100)}%)")

                    # Show more detailed status
                    elapsed_time = poll_count * 2  # seconds
                    details_placeholder.info(f"🔄 Agents are working on your request... (Elapsed: {elapsed_time}s)")

                elif status == "completed":
                    progress_placeholder.progress(1.0, text="Complete!")
                    status_placeholder.success("✅ Workflow completed successfully!")
                    details_placeholder.empty()

                    # Show results summary
                    if result.get("result"):
                        show_results_summary(result["result"])
                    break

                elif status in ["failed", "error"]:
                    progress_placeholder.progress(0.0)
                    error_msg = result.get("result", {}).get("error", "Unknown error")
                    status_placeholder.error(f"❌ Workflow failed: {error_msg}")
                    details_placeholder.empty()
                    break

        except requests.exceptions.Timeout:
            consecutive_failures += 1
            if consecutive_failures < 5:
                # API is busy, this is expected during heavy processing
                progress = min(poll_count / 60, 0.9)
                progress_placeholder.progress(progress, text=f"Processing... ({int(progress * 100)}%)")
                details_placeholder.warning("⏳ API is busy processing (this is normal)...")
            else:
                status_placeholder.error("❌ API connection lost. Please check the Results page manually.")
                break
        except Exception as e:
            consecutive_failures += 1
            if consecutive_failures < 5:
                details_placeholder.warning(f"Retrying... ({str(e)[:50]})")
            else:
                status_placeholder.error(f"❌ Connection error: {str(e)[:100]}")
                break

        time.sleep(2)
        poll_count += 1

    if poll_count >= max_polls:
        status_placeholder.warning("⏱️ Workflow is taking longer than expected. Check the Results page later.")
        details_placeholder.info(f"Job ID: {job_id}")


def show_results_summary(result: dict):
    """Show a beautifully formatted summary of workflow results."""
    st.markdown("---")
    st.markdown("## 📊 Workflow Results")

    # Top-level metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        verdict = result.get("verdict", "N/A")
        verdict_icon = "✅" if verdict == "APPROVE" else "⚠️" if verdict == "REVISE" else "❌"
        st.metric("Final Verdict", verdict, delta_color="off")
        st.markdown(f"<h2 style='text-align: center;'>{verdict_icon}</h2>", unsafe_allow_html=True)

    with col2:
        revisions = result.get("revision_count", 0)
        st.metric("Quality Revisions", f"{revisions} cycles")

    with col3:
        success = result.get("success", False)
        status_icon = "✅" if success else "❌"
        st.metric("Status", f"{status_icon} {'Complete' if success else 'Failed'}")

    with col4:
        # Calculate duration if available
        started = result.get("started_at", "")
        completed = result.get("completed_at", "")
        if started and completed:
            from datetime import datetime
            start_dt = datetime.fromisoformat(started)
            end_dt = datetime.fromisoformat(completed)
            duration = (end_dt - start_dt).total_seconds()
            st.metric("Duration", f"{int(duration)}s")

    st.markdown("---")

    # Parse and display candidate rankings in a beautiful format
    final_recs = result.get("final_recommendations", "")

    # Extract candidate ranking if present
    if "FINAL CANDIDATE RANKING" in final_recs:
        st.markdown("### 🏆 Candidate Rankings")

        # Try to extract candidate info
        import re

        # Look for candidate names and scores
        candidate_pattern = r"\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(\d+)/100"
        candidates = re.findall(candidate_pattern, final_recs)

        if candidates:
            for rank, name, score in candidates:
                score_int = int(score)

                # Color code based on score
                if score_int >= 70:
                    color = "#28a745"  # Green
                    status = "Strong Candidate"
                elif score_int >= 50:
                    color = "#ffc107"  # Yellow
                    status = "Moderate Fit"
                else:
                    color = "#dc3545"  # Red
                    status = "Weak Fit"

                # Create a card for each candidate
                st.markdown(f"""
                <div style='padding: 1rem; border-radius: 0.5rem; border-left: 4px solid {color}; background-color: rgba(0,0,0,0.05); margin: 0.5rem 0;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <h4 style='margin: 0;'>#{rank} {name.strip()}</h4>
                            <p style='margin: 0.25rem 0; color: {color};'>{status}</p>
                        </div>
                        <div style='text-align: right;'>
                            <h2 style='margin: 0; color: {color};'>{score}/100</h2>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Show progress bar for score
                st.progress(score_int / 100)

    st.markdown("---")

    # Tabbed interface for detailed results
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Summary", "📊 Detailed Analysis", "💡 Insights", "🔍 Quality Check", "📝 Execution Log"])

    with tab1:
        st.markdown("### Executive Summary")
        # Extract executive summary
        if "EXECUTIVE SUMMARY" in final_recs:
            summary_start = final_recs.find("EXECUTIVE SUMMARY")
            summary_end = final_recs.find("---", summary_start)
            if summary_end > summary_start:
                summary = final_recs[summary_start:summary_end]
                st.markdown(summary)

        # Show hiring insights
        if "HIRING INSIGHTS" in final_recs:
            st.markdown("### 📈 Hiring Insights")
            insights_start = final_recs.find("HIRING INSIGHTS")
            insights_end = final_recs.find("---", insights_start + 50)
            if insights_end > insights_start:
                insights = final_recs[insights_start:insights_end]
                st.markdown(insights)

    with tab2:
        st.markdown("### 📊 Detailed Analysis")

        # Show plan
        if result.get("plan"):
            with st.expander("🎯 Hiring Plan", expanded=False):
                st.markdown(result["plan"])

        # Show screening results
        if result.get("screening_results"):
            with st.expander("🔍 Resume Screening", expanded=False):
                st.markdown(result["screening_results"])

        # Show matching results
        if result.get("matching_results"):
            with st.expander("⚖️ Skill Matching", expanded=False):
                st.markdown(result["matching_results"])

        # Show ranking results
        if result.get("ranking_results"):
            with st.expander("📊 Candidate Ranking", expanded=False):
                st.markdown(result["ranking_results"])

    with tab3:
        st.markdown("### 💡 Recommendations & Insights")

        # Extract recommendations
        if "TOP RECOMMENDATIONS FOR INTERVIEW" in final_recs:
            st.markdown("#### 🎯 Interview Recommendations")
            recs_start = final_recs.find("TOP RECOMMENDATIONS FOR INTERVIEW")
            recs_end = final_recs.find("NOT RECOMMENDED FOR INTERVIEW", recs_start)
            if recs_end > recs_start:
                recs = final_recs[recs_start:recs_end]
                st.markdown(recs)

        # Show interview questions
        if "Suggested Interview Questions" in final_recs:
            st.markdown("#### ❓ Suggested Interview Questions")
            questions_start = final_recs.find("Suggested Interview Questions")
            questions_end = final_recs.find("---", questions_start)
            if questions_end > questions_start:
                questions = final_recs[questions_start:questions_end]
                st.markdown(questions)

    with tab4:
        st.markdown("### 🔍 Quality Check Results")
        if result.get("critique"):
            st.markdown(result["critique"])
        else:
            st.info("No critique data available")

    with tab5:
        st.markdown("### 📝 Execution Timeline")
        if result.get("execution_log"):
            for log_entry in result["execution_log"]:
                st.text(log_entry)
        else:
            st.info("No execution log available")


def show_results_page():
    """Display the results page."""
    st.markdown("# 📊 Workflow Results")

    # Auto-refresh toggle and manual refresh button
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        auto_refresh = st.checkbox("🔄 Auto-refresh every 5 seconds", value=False)
    with col2:
        if st.button("🔃 Refresh Now", use_container_width=True):
            st.rerun()
    with col3:
        if auto_refresh:
            time.sleep(5)
            st.rerun()

    try:
        response = requests.get(f"{API_URL}/api/v1/jobs", timeout=5)
        if response.status_code == 200:
            jobs = response.json().get("jobs", [])

            if not jobs:
                st.info("No workflows found. Start a new one!")
                return

            # Filter controls
            col1, col2 = st.columns(2)
            with col1:
                status_filter = st.selectbox(
                    "Filter by Status",
                    ["All", "completed", "running", "failed"]
                )

            # Display jobs
            st.markdown("---")

            filtered_jobs = jobs if status_filter == "All" else [j for j in jobs if j["status"] == status_filter]

            for job in reversed(filtered_jobs):
                status_icon = "🟢" if job['status'] == 'completed' else "🟡" if job['status'] == 'running' else "🔴"
                with st.expander(f"{status_icon} Job {job['job_id']} - {job['status'].upper()}", expanded=False):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown(f"**Status:** {job['status']}")
                    with col2:
                        st.markdown(f"**Started:** {job.get('started_at', 'N/A')}")
                    with col3:
                        st.markdown(f"**Completed:** {job.get('completed_at', 'N/A')}")

                    # Fetch full details
                    if st.button(f"📄 View Full Report", key=f"load_{job['job_id']}", use_container_width=True):
                        with st.spinner("Loading workflow details..."):
                            try:
                                detail_response = requests.get(
                                    f"{API_URL}/api/v1/workflow/status/{job['job_id']}",
                                    timeout=5
                                )
                                if detail_response.status_code == 200:
                                    details = detail_response.json()

                                    if details.get("status") == "running":
                                        st.info("🔄 This workflow is still running. Please check back in a few minutes.")
                                    elif details.get("result"):
                                        # Use the beautiful results summary instead of raw JSON
                                        show_results_summary(details["result"])
                                    else:
                                        st.warning("No results available yet.")
                                else:
                                    st.error(f"Failed to load details: {detail_response.status_code}")
                            except requests.exceptions.Timeout:
                                st.warning("⏳ Request timed out. The workflow might still be running.")
                            except Exception as e:
                                st.error(f"Error loading details: {str(e)}")

    except requests.exceptions.Timeout:
        st.error("⏳ Connection to API timed out. The API might be busy processing workflows.")
    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to API. Please ensure the server is running.")
    except Exception as e:
        st.error(f"Error fetching results: {str(e)}")


def show_documents_page():
    """Display the documents management page."""
    st.markdown("# 📁 Document Management")

    # Upload section
    st.markdown("### Upload Documents")

    col1, col2 = st.columns(2)

    with col1:
        uploaded_file = st.file_uploader(
            "Upload Resume or Job Description",
            type=["pdf", "txt", "md"],
            help="Supported formats: PDF, TXT, MD"
        )

    with col2:
        doc_type = st.selectbox(
            "Document Type",
            ["resume", "job_description"]
        )

    if uploaded_file and st.button("📤 Upload Document"):
        with st.spinner("Uploading..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                data = {"doc_type": doc_type}

                response = requests.post(
                    f"{API_URL}/api/v1/documents/upload",
                    files=files,
                    data=data,
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ Uploaded! {result.get('chunks_added', 0)} chunks added to database.")
                else:
                    st.error(f"Upload failed: {response.json().get('detail', 'Unknown error')}")

            except Exception as e:
                st.error(f"Error: {str(e)}")

    st.markdown("---")

    # Search section
    st.markdown("### Search Documents")

    search_query = st.text_input("Search query", placeholder="e.g., Python developer with 5 years experience")

    if search_query and st.button("🔍 Search"):
        with st.spinner("Searching..."):
            try:
                response = requests.post(
                    f"{API_URL}/api/v1/documents/search",
                    json={"query": search_query, "top_k": 5},
                    timeout=30
                )

                if response.status_code == 200:
                    results = response.json()
                    st.markdown(f"**Found {results['count']} results**")

                    for i, result in enumerate(results.get("results", [])):
                        with st.expander(f"Result {i+1} (Score: {result['score']:.2f})"):
                            st.markdown(result["content"])
                            st.json(result["metadata"])
                else:
                    st.warning("No results found")

            except Exception as e:
                st.error(f"Search error: {str(e)}")

    st.markdown("---")

    # Stats section
    st.markdown("### Database Stats")

    try:
        response = requests.get(f"{API_URL}/api/v1/documents/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            st.metric("Total Documents", stats.get("total_documents", 0))

            if st.button("🗑️ Reset Database", type="secondary"):
                if st.checkbox("I confirm I want to delete all documents"):
                    requests.delete(f"{API_URL}/api/v1/documents/reset")
                    st.success("Database reset!")
                    st.rerun()

    except Exception as e:
        st.warning(f"Could not fetch stats: {str(e)}")


def show_settings_page():
    """Display the settings page."""
    st.markdown("# ⚙️ Settings")

    # API Configuration
    st.markdown("### API Configuration")
    api_url = st.text_input("API URL", value=API_URL)

    st.markdown("---")

    # Run tests
    st.markdown("### Robustness Tests")

    if st.button("🧪 Run Tests"):
        with st.spinner("Running tests..."):
            try:
                response = requests.get(f"{API_URL}/api/v1/tests/robustness", timeout=60)
                if response.status_code == 200:
                    results = response.json()
                    summary = results.get("summary", {})

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Tests", summary.get("total_tests", 0))
                    with col2:
                        st.metric("Passed", summary.get("passed", 0))
                    with col3:
                        st.metric("Failed", summary.get("failed", 0))

                    st.markdown(f"**Pass Rate:** {summary.get('pass_rate', 'N/A')}")

                    with st.expander("View Details"):
                        st.json(results)

            except Exception as e:
                st.error(f"Error running tests: {str(e)}")

    st.markdown("---")

    # System info
    st.markdown("### System Information")
    st.markdown(f"- **Python Version:** {sys.version}")
    st.markdown(f"- **Working Directory:** {os.getcwd()}")


if __name__ == "__main__":
    main()
