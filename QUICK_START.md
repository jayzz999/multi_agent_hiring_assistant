# Quick Start Guide - HR Automation System

## 🚀 Get Started in 5 Minutes

This guide will get your HR automation system up and running quickly.

---

## Prerequisites

- Python 3.10 or higher
- PostgreSQL (or use SQLite for development)
- Redis (optional, for async tasks)
- OpenAI API key

---

## Installation Steps

### 1. Clone and Setup Environment

```bash
# Navigate to project directory
cd multi_agent_hiring_assistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
# Required: OpenAI API Key
OPENAI_API_KEY=sk-your-key-here

# LLM Configuration
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

# Database (SQLite for quick start, PostgreSQL for production)
DATABASE_URL=sqlite:///./data/hr_automation.db
# For PostgreSQL:
# DATABASE_URL=postgresql://username:password@localhost:5432/hr_automation

# ChromaDB for resume vector storage
CHROMA_PERSIST_DIR=./data/vector_store

# Email Configuration (Optional - for testing, logs to console)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourcompany.com
FROM_NAME=YourCompany Talent Team

# Redis (Optional - for background tasks)
REDIS_URL=redis://localhost:6379/0
```

### 3. Initialize Database

```bash
python -c "from src.models.database import init_db; init_db()"
```

This creates all necessary database tables.

### 4. Load Sample Data (Optional)

```bash
# Upload sample resumes to vector store
python -c "
from src.rag.document_loader import DocumentLoader
from src.rag.vector_store import VectorStore

loader = DocumentLoader()
vector_store = VectorStore()

# Load resumes from data/resumes/
documents = loader.load_directory('./data/resumes', doc_type='resume')
vector_store.add_documents(documents)

print(f'Loaded {len(documents)} resume chunks into vector store')
"
```

---

## 🎯 Running the System

### Option 1: Run the API Server

```bash
# Start the FastAPI server
uvicorn api.main:app --reload --port 8000

# API will be available at:
# - Swagger UI: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

### Option 2: Run the Streamlit UI

```bash
# Start the Streamlit admin interface
streamlit run ui/streamlit_app.py

# UI will open automatically in your browser
# Usually at: http://localhost:8501
```

### Option 3: Run Both (Recommended)

```bash
# Terminal 1: API Server
uvicorn api.main:app --reload --port 8000

# Terminal 2: Streamlit UI
streamlit run ui/streamlit_app.py
```

---

## 📝 Quick Test Examples

### Test 1: Parse a Resume

```python
from src.services.resume_parser_service import ResumeParserService

parser = ResumeParserService()

# Parse a resume
result = parser.parse_resume("./data/resumes/john_smith.txt")

print(f"Name: {result['contact_info']['name']}")
print(f"Email: {result['contact_info']['email']}")
print(f"Skills: {result['skills']}")
print(f"Experience: {result['years_of_experience']} years")
```

### Test 2: Generate an Email

```python
from src.agents.communication_agent import CommunicationAgent

comm_agent = CommunicationAgent()

# Generate interview invitation
email = comm_agent.generate_interview_invitation(
    candidate_name="John Smith",
    job_title="Senior Python Developer",
    interview_type="Technical Interview",
    interview_date="January 15, 2024 at 2:00 PM EST",
    interview_duration=60,
    meeting_link="https://zoom.us/j/123456789"
)

print(email)
```

### Test 3: Run Complete Workflow

```python
from src.orchestration.router import HiringOrchestrator

orchestrator = HiringOrchestrator()

result = orchestrator.run(
    job_description="""
    Senior Python Developer

    Requirements:
    - 5+ years Python experience
    - Django or FastAPI expertise
    - AWS experience
    - Strong problem-solving skills
    """,
    num_candidates=10,
    num_to_interview=3
)

print(result['final_recommendations'])
print(result['interview_schedule'])
```

### Test 4: Use Job Posting Service

```python
from src.services.job_posting_service import JobPostingService, JobBoard

posting_service = JobPostingService()

# Post to multiple boards
result = posting_service.create_job_posting(
    job_id="job_001",
    job_data={
        "title": "Senior Python Developer",
        "description": "Looking for an experienced Python developer...",
        "location": "San Francisco, CA",
        "job_type": "full-time",
        "salary_min": 120000,
        "salary_max": 160000,
        "company_name": "Tech Company Inc."
    },
    boards=[JobBoard.LINKEDIN, JobBoard.INDEED, JobBoard.GLASSDOOR]
)

print(f"Posted to {result['boards_posted']} boards")
print(result['results'])
```

### Test 5: Get Analytics

```python
from src.services.analytics_service import AnalyticsService
from datetime import datetime, timedelta

analytics = AnalyticsService()

# Get hiring funnel
funnel = analytics.get_hiring_funnel(
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now()
)

print("Hiring Funnel:")
print(f"Applications: {funnel['funnel']['applications']}")
print(f"Interviews: {funnel['funnel']['interviewed']}")
print(f"Offers: {funnel['funnel']['offers_made']}")
print(f"Hires: {funnel['funnel']['offers_accepted']}")

# Get source effectiveness
sources = analytics.get_source_effectiveness()
for source in sources['sources']:
    print(f"{source['source']}: {source['conversion_rate']}% conversion, ${source['cost_per_hire']} per hire")
```

---

## 🔧 API Usage Examples

### Via cURL:

```bash
# Health check
curl http://localhost:8000/health

# Start a hiring workflow
curl -X POST http://localhost:8000/api/v1/workflow/start \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Senior Python Developer with 5 years experience",
    "num_candidates": 10,
    "num_to_interview": 3
  }'

# Check workflow status
curl http://localhost:8000/api/v1/workflow/status/{job_id}

# Upload a resume
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@resume.pdf" \
  -F "doc_type=resume"

# Search resumes
curl -X POST http://localhost:8000/api/v1/documents/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Python developer with AWS experience",
    "top_k": 5
  }'
```

### Via Python Requests:

```python
import requests

# Start workflow
response = requests.post(
    "http://localhost:8000/api/v1/workflow/start",
    json={
        "job_description": "Senior Python Developer with 5 years experience",
        "num_candidates": 10,
        "num_to_interview": 3
    }
)

job_id = response.json()["job_id"]
print(f"Started job: {job_id}")

# Check status
status = requests.get(f"http://localhost:8000/api/v1/workflow/status/{job_id}")
print(status.json())
```

---

## 🎨 Using Individual Agents

Each agent can be used independently:

```python
# Sourcing Agent
from src.agents.sourcing_agent import SourcingAgent

sourcing = SourcingAgent()
boolean_search = sourcing.generate_boolean_search(
    skills=["Python", "Django", "AWS"],
    titles=["Senior Developer", "Lead Engineer"]
)
print(boolean_search)

# Assessment Agent
from src.agents.assessment_agent import AssessmentAgent

assessment = AssessmentAgent()
challenge = assessment.generate_coding_challenge(
    skills_required=["Python", "Algorithms", "Data Structures"],
    difficulty="medium",
    time_limit_minutes=60
)
print(challenge)

# Compliance Agent
from src.agents.compliance_agent import ComplianceAgent

compliance = ComplianceAgent()
jd_check = compliance.check_job_description_compliance(
    job_description="Looking for a young, energetic developer..."
)
print(jd_check)  # Will flag age-related language

# Offer Agent
from src.agents.offer_agent import OfferAgent

offer = OfferAgent()
compensation = offer.recommend_compensation(
    candidate_profile={"years_experience": 7, "skills": ["Python", "AWS"]},
    job_requirements={"level": "senior"},
    salary_range={"min": 120000, "max": 160000}
)
print(compensation)
```

---

## 📊 Testing the Full System

### End-to-End Test:

```python
from src.models.database import SessionLocal, Job, Candidate, Application
from src.models.database import JobCreate, CandidateCreate, ApplicationCreate
from datetime import datetime
import uuid

# Create database session
db = SessionLocal()

try:
    # 1. Create a job
    job = Job(
        id=str(uuid.uuid4()),
        title="Senior Python Developer",
        department="Engineering",
        location="San Francisco, CA",
        job_type="full-time",
        description="We're looking for an experienced Python developer...",
        skills_required=["Python", "Django", "AWS", "PostgreSQL"],
        experience_min=5,
        experience_max=10,
        salary_min=120000,
        salary_max=160000,
        status="open",
        openings=2,
        posted_at=datetime.utcnow()
    )
    db.add(job)
    db.commit()
    print(f"✅ Created job: {job.id}")

    # 2. Create a candidate
    candidate = Candidate(
        id=str(uuid.uuid4()),
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@email.com",
        phone="+1-555-0123",
        linkedin_url="https://linkedin.com/in/janedoe",
        current_title="Senior Software Engineer",
        current_company="Tech Corp",
        location="San Francisco, CA",
        years_of_experience=7,
        skills=["Python", "Django", "FastAPI", "AWS", "Docker"],
        source="LinkedIn"
    )
    db.add(candidate)
    db.commit()
    print(f"✅ Created candidate: {candidate.id}")

    # 3. Create an application
    application = Application(
        id=str(uuid.uuid4()),
        job_id=job.id,
        candidate_id=candidate.id,
        status="applied",
        source="LinkedIn",
        applied_at=datetime.utcnow()
    )
    db.add(application)
    db.commit()
    print(f"✅ Created application: {application.id}")

    print("\n🎉 Full system test passed!")
    print(f"Job: {job.title}")
    print(f"Candidate: {candidate.first_name} {candidate.last_name}")
    print(f"Application Status: {application.status}")

finally:
    db.close()
```

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution**: Make sure you're in the virtual environment and ran `pip install -r requirements.txt`

### Issue: "Database connection failed"
**Solution**: Check your `DATABASE_URL` in `.env`. For quick start, use SQLite (default).

### Issue: "OpenAI API error"
**Solution**: Verify your `OPENAI_API_KEY` is set correctly in `.env`

### Issue: "ChromaDB error"
**Solution**: Ensure the `data/vector_store` directory exists: `mkdir -p data/vector_store`

### Issue: "SMTP connection failed"
**Solution**: Email is optional for testing. Emails will log to console if SMTP isn't configured.

---

## 📚 Next Steps

1. **Read the Implementation Guide**: [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for detailed architecture

2. **Explore the API**: Visit http://localhost:8000/docs for interactive API documentation

3. **Add External Integrations**:
   - Set up LinkedIn API credentials
   - Configure Google Calendar OAuth
   - Connect assessment platforms

4. **Build the UI**:
   - Extend Streamlit dashboard
   - Create candidate portal
   - Add analytics visualizations

5. **Deploy**:
   - Set up production database
   - Configure Redis for background tasks
   - Deploy with Docker/Kubernetes
   - Add authentication

---

## 💡 Pro Tips

- **Use SQLite for Development**: No need to set up PostgreSQL initially
- **Test with Sample Data**: Use the provided sample resumes in `data/resumes/`
- **Check Logs**: FastAPI logs are very helpful for debugging
- **Use the Docs**: Swagger UI at `/docs` has interactive API testing
- **Start Small**: Test individual agents before running full workflows

---

## 🎯 Common Workflows

### Workflow 1: Post a Job
1. Create job in database (or via API)
2. Use `JobPostingService` to post to boards
3. Monitor applications coming in

### Workflow 2: Screen Candidates
1. Upload resumes via API
2. Run resume parser on each
3. Use screening agent to evaluate
4. Store results in database

### Workflow 3: Schedule Interviews
1. Get list of qualified candidates
2. Use `CalendarService` to find slots
3. Create interview events
4. Send invitations via `EmailService`

### Workflow 4: Make Offer
1. Select final candidate
2. Use `OfferAgent` to recommend compensation
3. Generate offer letter
4. Track acceptance/negotiation

---

## 🔗 Useful Commands

```bash
# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Run API server
uvicorn api.main:app --reload --port 8000

# Run Streamlit UI
streamlit run ui/streamlit_app.py

# Run tests
pytest tests/ -v

# Initialize database
python -c "from src.models.database import init_db; init_db()"

# Python shell for testing
python -i -c "from src.models.database import *; from src.agents import *; from src.services import *"
```

---

## 📞 Getting Help

- **Documentation**: Check [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
- **API Docs**: http://localhost:8000/docs
- **Code Examples**: See `tests/` directory
- **Agent Details**: Read source code in `src/agents/` - well documented

---

**You're all set! Start automating your hiring process! 🚀**
