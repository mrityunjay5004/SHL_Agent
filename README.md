# SHL Assessment Recommendation Agent

An AI-powered conversational recommendation system that helps recruiters identify the most relevant SHL assessments using semantic retrieval, hybrid ranking, and Gemini-powered reasoning. The system supports conversational recommendations, clarification questions, assessment comparisons, and grounded responses through a FastAPI REST API.

---

## 🚀 Live Deployment

| Resource | Link |
|----------|------|
| **Live API** | https://shl-agent-fw8x.onrender.com |
| **Swagger Docs** | https://shl-agent-fw8x.onrender.com/docs |
| **Health Endpoint** | https://shl-agent-fw8x.onrender.com/health |
| **Chat Endpoint** | POST https://shl-agent-fw8x.onrender.com/chat |
| **GitHub Repository** | https://github.com/mrityunjay5004/SHL_Agent |

---

## Features

- Semantic Retrieval using Sentence Transformers + FAISS
- Hybrid Ranking based on role, skills, seniority and assessment type
- Conversational multi-turn recommendation flow
- Intelligent clarification for incomplete recruiter queries
- Assessment comparison (e.g., OPQ vs DSI)
- Guardrails against off-topic and competitor requests
- Grounded LLM responses using Google Gemini
- FastAPI REST API with Swagger/OpenAPI documentation
- Automated evaluation pipeline

---

## Tech Stack

- Python 3.10
- FastAPI
- Sentence Transformers
- FAISS
- Google Gemini
- NumPy
- Scikit-learn

---

## Project Structure

```text
SHL_Agent/
│
├── app/
│   ├── guardrails.py
│   ├── llm.py
│   ├── orchestrator.py
│   ├── ranker.py
│   ├── retriever.py
│   ├── state_extractor.py
│   └── utils.py
│
├── data/
│   ├── processed_catalog.json
│   ├── embeddings.npy
│   └── faiss_index/
│
├── evaluation/
│   └── eval.py
│
├── scripts/
│   ├── create_embeddings.py
│   ├── create_faiss_index.py
│   ├── create_metadata.py
│   └── parse_traces.py
│
├── run.py
├── requirements.txt
└── README.md
```

---

## Architecture

```
User Query
      │
      ▼
Guardrails
      │
      ▼
State Extraction
      │
      ▼
Semantic Retrieval
(FAISS + Sentence Transformers)
      │
      ▼
Hybrid Ranker
      │
      ▼
Gemini Response Generation
      │
      ▼
FastAPI JSON Response
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/mrityunjay5004/SHL_Agent.git
cd SHL_Agent
```

Create virtual environment

```bash
python -m venv venv
```

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root.

```env
GEMINI_API_KEY=YOUR_API_KEY
```

---

## Build Retrieval Index

```bash
python scripts/create_embeddings.py
python scripts/create_faiss_index.py
```

---

## Run Locally

```bash
python run.py
```

Application:

```
http://localhost:8000
```

Swagger:

```
http://localhost:8000/docs
```

---

## API Endpoints

### Health

```http
GET /health
```

### Chat

```http
POST /chat
```

Example request

```json
{
  "messages": [
    {
      "role": "user",
      "content": "I am hiring a Java backend developer with 4 years of experience."
    }
  ]
}
```

Example response

```json
{
  "reply": "...",
  "recommendations": [
    {
      "name": "Java Web Services (New)",
      "url": "...",
      "test_type": "K"
    }
  ],
  "end_of_conversation": false
}
```

---

## Supported Capabilities

- Assessment Recommendation
- Assessment Comparison
- Clarification Questions
- Semantic Retrieval
- Multi-turn Conversations
- Context-Aware Ranking
- Guardrail Enforcement

---

## Evaluation

The evaluation pipeline measures:

- Recommendation Quality
- Retrieval Accuracy
- Recall@10
- Response Groundedness
- Schema Validation
- Guardrail Behaviour
- Comparison Accuracy
- Latency

Run evaluation

```bash
python evaluation/eval.py
```

---

## Future Improvements

- Hybrid BM25 + FAISS Retrieval
- Cross-Encoder Re-ranking
- Streaming Responses
- CI/CD Pipeline
- Expanded Evaluation Benchmarks

---

## Author

**Mrityunjay Tiwari**

- GitHub: https://github.com/mrityunjay5004
- LinkedIn: https://www.linkedin.com/in/mrityunjaytiwari5004/

---

## License

This project was developed as part of the SHL Research Intern Assignment and is intended solely for educational and demonstration purposes.
