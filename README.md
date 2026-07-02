# SHL Assessment Recommendation Agent

An AI-powered conversational recommendation system that helps recruiters identify the most relevant SHL assessments based on hiring requirements. The system combines semantic search, rule-based ranking, and Gemini-powered response generation to deliver accurate, contextual, and grounded recommendations.

---

## Features

- Semantic retrieval using Sentence Transformers + FAISS
- Hybrid reranking based on role, skills, seniority, and assessment type
- Multi-turn conversational recommendation flow
- Intelligent clarification for incomplete hiring requirements
- Assessment comparison (e.g., OPQ vs DSI)
- Guardrails for off-topic and competitor requests
- Grounded LLM responses using Gemini
- FastAPI REST API with OpenAPI documentation
- Automated evaluation pipeline

---

## Tech Stack

- Python 3.10
- FastAPI
- Sentence Transformers
- FAISS
- Google Gemini API
- NumPy
- Scikit-learn

---

## Project Structure

```
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
├── scripts/
│   ├── create_embeddings.py
│   ├── create_faiss_index.py
│   └── create_metadata.py
│
├── evaluation/
│   └── eval.py
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
Retriever (Sentence Transformers + FAISS)
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

Create a virtual environment

```bash
python -m venv venv
```

Activate the environment

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

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

## Build Embeddings

```bash
python scripts/create_embeddings.py
python scripts/create_faiss_index.py
```

---

## Run the Server

```bash
python run.py
```

Server runs on

```
http://localhost:8000
```

Swagger UI

```
http://localhost:8000/docs
```

---

## Example Request

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

---

## Example Response

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
- Guardrail Enforcement
- Context-Aware Ranking

---

## Evaluation

The evaluation pipeline measures:

- Recommendation Quality
- Recall@10
- Schema Validation
- Latency
- Guardrail Behaviour
- Comparison Accuracy

Run evaluation

```bash
python evaluation/eval.py
```

---

## Future Improvements

- Hybrid BM25 + FAISS retrieval
- Cross-encoder reranking
- Streaming responses
- Docker deployment
- CI/CD integration
- Expanded evaluation benchmarks

---

## Author

**Mrityunjay Tiwari**

- GitHub: https://github.com/mrityunjay5004
- LinkedIn: https://www.linkedin.com/in/mrityunjaytiwari5004/

---

## License

This project was developed as part of the SHL AI Assessment Recommendation assignment and is intended for educational and demonstration purposes.