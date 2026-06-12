# RAG Customer Support — Full Stack

A complete RAG (Retrieval-Augmented Generation) app:
- **Backend**: FastAPI + Claude (Python)
- **Frontend**: Plain HTML/CSS/JS (no framework needed)

---

## Folder Structure

```
rag_fullstack/
├── backend/
│   ├── main.py           ← FastAPI app
│   └── requirements.txt
└── frontend/
    └── index.html        ← Chat UI (just open in browser)
```

---

## Setup & Run

### Step 1 — Backend

```bash
cd backend
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."   # Windows: set ANTHROPIC_API_KEY=...
uvicorn main:app --reload --port 8000
```

### Step 2 — Frontend

Just open `frontend/index.html` in your browser. No build step needed.

---

## How to use

1. **Paste your content** in the left panel (FAQs, return policy, product info, etc.)
2. Click **Load Knowledge Base**
3. Type a customer question in the chat box
4. Claude answers using only your content ✅

---

## API Endpoints

| Method | Endpoint     | Description                        |
|--------|--------------|------------------------------------|
| GET    | /status      | Check if knowledge base is loaded  |
| POST   | /ingest      | Load your knowledge base text      |
| POST   | /ask         | Ask a customer question            |
| DELETE | /knowledge   | Clear the knowledge base           |

---

## Example `/ingest` payload

```json
{
  "text": "Return Policy: We accept returns within 30 days...\n\nShipping: Standard delivery takes 5-7 days...",
  "replace": true
}
```

## Example `/ask` payload

```json
{
  "question": "What is your return policy?"
}
```

## Example response

```json
{
  "answer": "You can return items within 30 days of purchase as long as they are unused and in original packaging. To start a return, email returns@company.com.",
  "sources_used": 3
}
```

---

## Production Tips

- Add API key auth to the backend (FastAPI `Depends` + header check)
- Swap keyword retrieval for vector embeddings (ChromaDB, Pinecone)
- Host the frontend on Netlify/Vercel, backend on Railway/Render
