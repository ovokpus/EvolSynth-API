# EvolSynth API 🚀

**Advanced Synthetic Data Generation using LangGraph-based Evol-Instruct methodology**

Transform your documents into sophisticated evaluation datasets with intelligent question evolution, concurrent processing, and comprehensive quality assessment.

## 🎯 What Makes EvolSynth Special?

EvolSynth implements the cutting-edge **Evol-Instruct methodology** using **LangGraph workflows** to generate high-quality synthetic evaluation data. Unlike simple question generators, EvolSynth creates progressively complex questions through three sophisticated evolution strategies:

### 🧠 Evolution Strategies

| Strategy | Complexity | Purpose | Example Transformation |
|----------|------------|---------|----------------------|
| **🎯 Simple Evolution** | Level 2 | Detail enhancement | "What is a loan?" → "What are the specific eligibility requirements and application procedures for federal student loans?" |
| **🌐 Multi-Context Evolution** | Level 3 | Cross-document synthesis | "What is financial aid?" → "How do Pell Grant eligibility requirements compare with Direct Loan criteria across different academic programs?" |
| **🧠 Reasoning Evolution** | Level 4 | Multi-step logical inference | "What affects loan amounts?" → "If a student's dependency status changes mid-year, how would this impact their loan eligibility and disbursement schedule?" |

### ⚡ Performance Features

- **🔄 Concurrent Execution**: 3x faster question generation through LangGraph's fan-out/fan-in pattern
- **📊 Real-time Monitoring**: Track generation progress with detailed status endpoints
- **🎚️ Quality Control**: Built-in LLM-as-judge evaluation for question quality, answer accuracy, and evolution effectiveness
- **🔧 Flexible Configuration**: Customize evolution parameters, execution modes, and quality thresholds

## 🚀 Quick Start

### 1. Installation

```bash
# Clone and setup
cd api/
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file with your API keys:

```bash
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_API_KEY=your_langchain_api_key_here

# LangSmith Configuration
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=EvolSynth-API

# Optional: Customize settings
DEFAULT_EXECUTION_MODE=concurrent
SIMPLE_EVOLUTION_COUNT=3
MULTI_CONTEXT_EVOLUTION_COUNT=2
REASONING_EVOLUTION_COUNT=2
```

### 3. Launch the API

```bash
# Development mode
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. Explore the API

- **📖 Interactive Docs**: http://localhost:8000/docs
- **🔍 Health Check**: http://localhost:8000/health
- **🎯 Sample Data**: http://localhost:8000/documents/sample

## 💡 API Usage Examples

### Generate Synthetic Data

```python
import requests

# Get sample documents for testing
response = requests.get("http://localhost:8000/documents/sample")
sample_documents = response.json()

# Generate synthetic data
generation_request = {
    "documents": sample_documents,
    "settings": {
        "execution_mode": "concurrent",
        "simple_evolution_count": 3,
        "multi_context_evolution_count": 2,
        "reasoning_evolution_count": 2,
        "temperature": 0.7
    },
    "max_iterations": 1
}

response = requests.post(
    "http://localhost:8000/generate",
    json=generation_request
)

result = response.json()
print(f"Generated {len(result['evolved_questions'])} questions!")
```

### Evaluate Quality

```python
# Evaluate the generated synthetic data
evaluation_request = {
    "evolved_questions": result["evolved_questions"],
    "question_answers": result["question_answers"], 
    "question_contexts": result["question_contexts"],
    "evaluation_metrics": [
        "question_quality",
        "answer_accuracy", 
        "evolution_effectiveness"
    ]
}

eval_response = requests.post(
    "http://localhost:8000/evaluate",
    json=evaluation_request
)

scores = eval_response.json()["overall_scores"]
print(f"Quality Scores: {scores}")
```

### Batch Processing

```python
# Process multiple document sets
batch_request = {
    "document_batches": [
        [sample_documents[0], sample_documents[1]],  # Batch 1
        [sample_documents[2]]                        # Batch 2
    ],
    "batch_names": ["Financial Aid Docs", "Academic Policies"],
    "settings": {"execution_mode": "concurrent"}
}

batch_response = requests.post(
    "http://localhost:8000/generate/batch",
    json=batch_request
)
```

## 🏗️ Architecture Overview

```
📁 EvolSynth API/
├── 🔧 config.py           # Environment & settings management
├── 📊 models/             # Pydantic models for requests/responses
│   ├── core.py           # Core domain models (EvolutionType, etc.)
│   ├── requests.py       # API request models
│   └── responses.py      # API response models
├── ⚙️ services/          # Core business logic
│   ├── evol_instruct_service.py    # LangGraph workflow engine
│   ├── evaluation_service.py       # Quality assessment
│   └── document_service.py         # Document processing
├── 🛠️ utils/            # Helper functions
└── 🚀 main.py           # FastAPI application
```

## 🎯 API Endpoints

### Core Generation
- `POST /generate` - Generate synthetic data from documents
- `POST /generate/batch` - Batch process multiple document sets
- `GET /generate/status/{id}` - Check generation progress

### Quality Assessment  
- `POST /evaluate` - Evaluate synthetic data quality

### Utilities
- `GET /health` - Health check and service status
- `GET /documents/sample` - Get sample documents for testing
- `GET /docs` - Interactive API documentation

## 📊 Performance Metrics

EvolSynth provides comprehensive performance tracking:

```json
{
  "performance_metrics": {
    "execution_time_seconds": 25.64,
    "questions_generated": 7,
    "answers_generated": 7, 
    "contexts_extracted": 7,
    "questions_per_second": 0.27,
    "execution_mode": "concurrent"
  }
}
```

## 🔧 Configuration Options

### Execution Modes

- **🚀 Concurrent** (Recommended): All evolution types run in parallel (~3x faster)
- **🐌 Sequential**: Evolution types run one after another (easier debugging)

### Evolution Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `simple_evolution_count` | 3 | Number of simple evolution questions |
| `multi_context_evolution_count` | 2 | Number of multi-context questions |
| `reasoning_evolution_count` | 2 | Number of reasoning questions |
| `max_base_questions_per_doc` | 3 | Base questions extracted per document |
| `temperature` | 0.7 | LLM creativity setting |

### Document Processing

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_document_size_mb` | 10 | Maximum document size |
| `chunk_size` | 1000 | Text chunk size for processing |
| `chunk_overlap` | 50 | Overlap between chunks |
| `max_content_length` | 2000 | Maximum content length for LLM |

## 🎭 Quality Evaluation

EvolSynth includes sophisticated quality assessment using LLM-as-judge approaches:

### Evaluation Metrics

- **🎯 Question Quality**: Clarity, specificity, and educational value
- **✅ Answer Accuracy**: Correctness and completeness of generated answers  
- **⚡ Evolution Effectiveness**: Success of complexity enhancement

### Sample Evaluation Results

```json
{
  "overall_scores": {
    "question_quality": 0.85,
    "answer_accuracy": 0.78, 
    "evolution_effectiveness": 0.92
  },
  "summary_statistics": {
    "total_questions_evaluated": 7,
    "average_complexity": 2.8,
    "evolution_type_distribution": {
      "simple_evolution": 3,
      "multi_context_evolution": 2,
      "reasoning_evolution": 2
    }
  }
}
```

## 🛡️ Error Handling

EvolSynth provides comprehensive error handling with detailed error responses:

```json
{
  "success": false,
  "error": "ValidationError",
  "message": "Document validation failed",
  "details": {
    "field": "documents[0].content",
    "issue": "Content cannot be empty"
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

## 🚀 Production Deployment

### Environment Variables

```bash
# Production settings
DEBUG=false
MAX_CONCURRENCY=5
REQUEST_TIMEOUT=600

# Security
CORS_ORIGINS=https://your-domain.com

# Performance optimization
DEFAULT_EXECUTION_MODE=concurrent
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🎯 Use Cases

### AI System Evaluation
Generate challenging evaluation datasets for testing RAG systems, QA models, and knowledge retrieval applications.

### Educational Assessment  
Create sophisticated exam questions with varying difficulty levels for educational platforms.

### Research Applications
Generate synthetic data for academic research in natural language processing and machine learning.

### Quality Assurance
Test chatbots and AI assistants with progressively complex scenarios.

## 📈 Performance Benchmarks

| Configuration | Questions/Minute | Typical Use Case |
|---------------|------------------|------------------|
| Concurrent Mode | ~15-20 | Production environments |
| Sequential Mode | ~5-8 | Development & debugging |
| Batch Processing | ~25-30 | Large-scale data generation |

## 🤝 Contributing

We welcome contributions! The EvolSynth API is built on solid foundations:

- **🏗️ FastAPI**: High-performance, standards-based API framework
- **🔗 LangChain**: Robust LLM integration and document processing
- **🌐 LangGraph**: Advanced workflow orchestration with concurrent execution
- **📊 Pydantic**: Type-safe data validation and serialization

## 📄 License

Built with ❤️ for the AI community. Based on the Evol-Instruct methodology from the WizardLM research.

---

**Ready to evolve your data?** 🚀 

Start generating sophisticated synthetic evaluation datasets that push the boundaries of AI system assessment! 