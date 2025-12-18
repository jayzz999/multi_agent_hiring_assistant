# Multi-Agent Hiring Assistant 🤖

An AI-powered hiring workflow automation system using multiple specialized agents following the PEC (Planner-Executor-Critic) architecture pattern.

## 🌟 Features

- **Multi-Agent Architecture**: Specialized AI agents for each stage of the hiring process
- **PEC Pattern**: Planner, Executor, and Critic agents for quality assurance
- **RAG Integration**: Resume search and matching using vector embeddings
- **LangGraph Orchestration**: Stateful workflow with conditional routing
- **FastAPI Backend**: RESTful API for integration
- **Streamlit UI**: User-friendly web interface
- **Comprehensive Evaluation**: Metrics collection and robustness testing

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     HIRING WORKFLOW                              │
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ Planner  │───▶│ Screener │───▶│ Matcher  │───▶│ Ranker   │  │
│  │  Agent   │    │  Agent   │    │  Agent   │    │  Agent   │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│       │                                                │        │
│       │                                                ▼        │
│       │         ┌──────────────────────────────────────┐       │
│       │         │           Critic Agent               │       │
│       │         │  (Quality Assurance & Oversight)     │       │
│       │         └──────────────────────────────────────┘       │
│       │                         │                               │
│       │         ┌───────────────┼───────────────┐              │
│       │         ▼               ▼               ▼              │
│       │    [APPROVE]       [REVISE]        [REJECT]            │
│       │         │               │               │              │
│       │         ▼               │               │              │
│       │    ┌──────────┐        │               │              │
│       └───▶│ Finalize │◀───────┘               │              │
│            └──────────┘◀───────────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
multi_agent_hiring_assistant/
├── README.md
├── requirements.txt
├── .env.example
├── config/
│   └── settings.py              # Configuration management
├── data/
│   ├── resumes/                 # Sample PDF/text resumes
│   ├── job_descriptions/        # Sample JDs in JSON/text
│   └── vector_store/            # ChromaDB persistence
├── src/
│   ├── agents/                  # AI Agent implementations
│   │   ├── base_agent.py        # Abstract base agent
│   │   ├── planner_agent.py     # Planning agent
│   │   ├── resume_screener.py   # Resume screening executor
│   │   ├── skill_matcher.py     # Skill matching executor
│   │   ├── candidate_ranker.py  # Candidate ranking executor
│   │   ├── interview_scheduler.py # Interview scheduling
│   │   └── critic_agent.py      # Quality evaluation critic
│   ├── tools/                   # Agent tools
│   │   ├── resume_parser.py     # PDF/text resume extraction
│   │   ├── jd_parser.py         # Job description parser
│   │   ├── rag_retriever.py     # RAG search tool
│   │   ├── email_drafter.py     # Email drafting tool
│   │   └── calendar_tool.py     # Mock calendar integration
│   ├── rag/                     # RAG components
│   │   ├── document_loader.py   # Load and chunk documents
│   │   ├── embeddings.py        # Embedding generation
│   │   └── vector_store.py      # ChromaDB operations
│   ├── orchestration/           # Workflow orchestration
│   │   ├── state.py             # Shared state definitions
│   │   ├── graph.py             # LangGraph workflow
│   │   └── router.py            # Conditional routing
│   ├── prompts/                 # Agent prompts
│   │   ├── planner_prompts.py
│   │   ├── screener_prompts.py
│   │   ├── matcher_prompts.py
│   │   ├── ranker_prompts.py
│   │   └── critic_prompts.py
│   └── evaluation/              # Evaluation framework
│       ├── metrics.py           # Performance metrics
│       ├── robustness.py        # Robustness tests
│       └── reporter.py          # Report generation
├── api/
│   └── main.py                  # FastAPI application
├── ui/
│   └── streamlit_app.py         # Streamlit demo interface
└── tests/
    ├── test_agents.py
    ├── test_rag.py
    └── test_orchestration.py
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API key

### Installation

1. **Clone or navigate to the project**:
```bash
cd multi_agent_hiring_assistant
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

5. **Run the application**:

**Option A: Run the API**
```bash
uvicorn api.main:app --reload --port 8000
```

**Option B: Run the Streamlit UI**
```bash
streamlit run ui/streamlit_app.py
```

## 📚 Usage

### Using the API

```python
import requests

# Start a hiring workflow
response = requests.post(
    "http://localhost:8000/api/v1/workflow/start",
    json={
        "job_description": "Senior Python Developer with 5 years experience...",
        "num_candidates": 10,
        "num_to_interview": 3
    }
)

job_id = response.json()["job_id"]

# Check status
status = requests.get(f"http://localhost:8000/api/v1/workflow/status/{job_id}")
print(status.json())
```

### Using Python Directly

```python
from src.orchestration.router import HiringOrchestrator

orchestrator = HiringOrchestrator()

result = orchestrator.run(
    job_description="""
    Senior Python Developer

    Requirements:
    - 5+ years of Python experience
    - Django or FastAPI expertise
    - AWS experience
    """,
    num_candidates=10,
    num_to_interview=3
)

print(result["final_recommendations"])
```

### Uploading Resumes

```python
from src.rag.document_loader import DocumentLoader
from src.rag.vector_store import VectorStore

loader = DocumentLoader()
vector_store = VectorStore()

# Load and add resumes
documents = loader.load_directory("./data/resumes", doc_type="resume")
vector_store.add_documents(documents)

print(f"Added {len(documents)} document chunks")
```

## 🤖 Agents

### Planner Agent
- Analyzes job descriptions
- Creates evaluation criteria
- Defines workflow steps

### Resume Screener Agent
- Initial candidate screening
- PASS/FAIL decisions
- Uses RAG for candidate retrieval

### Skill Matcher Agent
- Detailed skill analysis
- Multi-dimensional scoring
- Experience evaluation

### Candidate Ranker Agent
- Final rankings
- Interview recommendations
- Hiring insights

### Critic Agent
- Quality assurance
- Bias detection
- Process improvement suggestions

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/workflow/start` | POST | Start hiring workflow |
| `/api/v1/workflow/status/{job_id}` | GET | Get workflow status |
| `/api/v1/workflow/run-sync` | POST | Run workflow synchronously |
| `/api/v1/parse/job-description` | POST | Parse job description |
| `/api/v1/documents/upload` | POST | Upload resume/document |
| `/api/v1/documents/search` | POST | Search documents |
| `/api/v1/documents/stats` | GET | Get document statistics |
| `/api/v1/tests/robustness` | GET | Run robustness tests |
| `/api/v1/reports/generate/{job_id}` | GET | Generate workflow report |

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_agents.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 📊 Metrics & Evaluation

The system includes comprehensive metrics collection:

```python
from src.evaluation.metrics import MetricsCollector

collector = MetricsCollector()
collector.start_workflow()

# ... run workflow ...

collector.end_workflow()
summary = collector.get_summary()
print(summary)
```

## 🔧 Configuration

Key configuration options in `.env`:

```env
# API Keys
OPENAI_API_KEY=your_key_here

# Model Configuration
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

# RAG Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
```

## 🏛️ Architecture Patterns

### PEC (Planner-Executor-Critic)
- **Planner**: Strategic planning and criteria definition
- **Executors**: Task-specific processing (screening, matching, ranking)
- **Critic**: Quality control and validation

### LangGraph StateGraph
- Stateful workflow management
- Conditional routing based on critic verdicts
- Automatic revision loops

### RAG (Retrieval-Augmented Generation)
- ChromaDB vector storage
- Semantic resume search
- Context-aware candidate matching

## 📈 Performance

Typical workflow execution:
- **Planning**: ~5 seconds
- **Screening**: ~10 seconds
- **Matching**: ~15 seconds
- **Ranking**: ~10 seconds
- **Critique**: ~5 seconds
- **Total**: ~45-60 seconds

## 🔒 Security Considerations

- API keys stored in environment variables
- No PII logged or stored beyond necessary processing
- Configurable data retention policies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- LangChain for the agent framework
- LangGraph for workflow orchestration
- ChromaDB for vector storage
- OpenAI for language models
