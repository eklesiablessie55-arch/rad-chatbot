"""
RAG Customer Support — FastAPI Backend
"""

import os
import re
from typing import Optional
import anthropic
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="RAG Customer Support API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# ── In-memory knowledge store ─────────────────────────────────────────────────
knowledge_chunks: list[str] = []
CHUNK_SIZE = 400
CHUNK_OVERLAP = 80
TOP_K = 5


# ── Models ────────────────────────────────────────────────────────────────────
class IngestRequest(BaseModel):
    text: str
    replace: bool = True

class AskRequest(BaseModel):
    question: str
    system_prompt: Optional[str] = None


# ── Helpers ───────────────────────────────────────────────────────────────────
def chunk_text(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    chunks, start = [], 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end].strip())
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return [c for c in chunks if c]


def retrieve(question: str, k: int = TOP_K) -> list[str]:
    if not knowledge_chunks:
        return []
    q_words = set(re.findall(r"\w+", question.lower()))
    ranked = sorted(knowledge_chunks, key=lambda c: len(q_words & set(re.findall(r"\w+", c.lower()))), reverse=True)
    return ranked[:k]


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/status")
def status():
    return {"total_chunks": len(knowledge_chunks), "ready": len(knowledge_chunks) > 0}


@app.post("/ingest")
def ingest(req: IngestRequest):
    global knowledge_chunks
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="text cannot be empty")
    new_chunks = chunk_text(req.text)
    if req.replace:
        knowledge_chunks = new_chunks
    else:
        knowledge_chunks.extend(new_chunks)
    return {"message": f"Knowledge base loaded — {len(knowledge_chunks)} chunks ready.", "total_chunks": len(knowledge_chunks)}


@app.post("/ask")
def ask(req: AskRequest):
    if not knowledge_chunks:
        raise HTTPException(status_code=400, detail="Knowledge base is empty. Load your content first.")
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    chunks = retrieve(req.question)
    context = "\n\n---\n\n".join(chunks)

    system = req.system_prompt or (
        "You are a helpful customer support assistant. "
        "Answer the customer's question using ONLY the information in the provided context. "
        "If the answer isn't in the context, politely say you don't have that information and suggest "
        "they contact support directly. Be concise, clear, and friendly."
    )

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=system,
        messages=[{"role": "user", "content": f"Context:\n\n{context}\n\nCustomer question: {req.question}"}],
    )

    return {"answer": response.content[0].text, "sources_used": len(chunks)}


@app.delete("/knowledge")
def clear():
    global knowledge_chunks
    knowledge_chunks = []
    return {"message": "Knowledge base cleared.", "total_chunks": 0}
