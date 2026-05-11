from fastapi import FastAPI

from app.models import ChatRequest
from app.orchestrator import generate_response

app = FastAPI()


@app.get("/health")
def health():

    return {
        "status": "ok"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    messages = [
        {
            "role": m.role,
            "content": m.content
        }
        for m in request.messages
    ]

    return generate_response(messages)