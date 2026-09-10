# RAG Studio

A full-stack RAG (Retrieval-Augmented Generation) application with built-in evaluation metrics. Upload PDFs, chat with your documents, and measure retrieval quality, answer faithfulness, and answer relevance.

## Features

### Document Ingestion
- Drag-and-drop PDF upload
- Automatic text extraction, chunking with overlap, and embedding
- Deduplication via MD5 hashing (re-uploading won't create duplicates)
- Vector storage in Qdrant with cross-encoder reranking

### RAG Chat
- Ask questions about your uploaded documents
- Streaming responses (token-by-token)
- Provider selection: OpenRouter (cloud) or Ollama (local)

### Evaluation Suite
- **Retrieval Evaluation** — Hit Rate, Recall, Precision, Mean Reciprocal Rank
- **Faithfulness Evaluation** — LLM-as-judge scores whether answers are supported by context (0-1)
- **Relevance Evaluation** — LLM-as-judge scores whether answers address the question (0-1) with explanations
- Configurable question range (From/To) and top-K
- Provider selection for answer generation and judging

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI, Python 3.14 |
| Vector DB | Qdrant (localhost:6333) |
| Embeddings | all-MiniLM-L6-v2 (384-dim) |
| Reranker | cross-encoder/ms-marco-MiniLM-L-6-v2 |
| LLM (Cloud) | OpenRouter — liquid/lfm-2.5-2.6b:free |
| LLM (Local) | Ollama — qwen3.5:4b |
| Frontend | Vanilla HTML/CSS/JS (no framework) |

## Project Structure

```
Task/
├── backend/
│   ├── main.py                    # FastAPI entry point
│   ├── .env                       # API keys
│   ├── routers/
│   │   ├── documents.py           # PDF upload endpoint
│   │   ├── chat.py                # RAG chat endpoint
│   │   └── evaluation.py          # Evaluation endpoints
│   ├── services/
│   │   ├── ingestion.py           # PDF loader
│   │   ├── chunker.py             # Sentence-based chunker
│   │   ├── embeder.py             # Sentence-transformers embedder
│   │   ├── vector_store.py        # Qdrant client + deduplication
│   │   ├── reranker.py            # Cross-encoder reranker
│   │   └── llm.py                 # LLM generation (OpenRouter + Ollama)
│   ├── evaluation/
│   │   ├── dataset.py             # 10-question evaluation dataset
│   │   ├── retrieval_metrics.py   # Hit rate, recall, precision, MRR
│   │   ├── answer_metrics.py      # Evaluation orchestration
│   │   ├── faithfulness.py        # Faithfulness LLM-as-judge
│   │   └── relevance.py           # Relevance LLM-as-judge
│   └── schemas/
│       └── chat.py                # Pydantic request models
├── frontend/
│   ├── index.html                 # Single-page app
│   ├── script.js                  # Frontend logic
│   └── style.css                  # Dark-themed UI
```

## Prerequisites

1. **Python 3.14**
2. **Qdrant** running at `localhost:6333`
3. **Ollama** (optional) with `qwen3.5:4b` pulled — `ollama pull qwen3.5:4b`
4. **OpenRouter API key** in `backend/.env`

## Setup

### 1. Install dependencies

```bash
cd backend
uv sync
```

### 2. Configure environment

Create `backend/.env`:

```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### 3. Start Qdrant

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### 4. Start Ollama (optional, for local inference)

```bash
ollama serve
ollama pull qwen3.5:4b
```

### 5. Start the backend

```bash
cd backend
python main.py
```

API docs at `http://127.0.0.1:8000/docs`

### 6. Start the frontend

Open `frontend/index.html` in a browser, or serve it:

```bash
cd frontend
python -m http.server 3000
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/documents/uploads` | Upload and ingest a PDF |
| POST | `/chat/?provider=openrouter\|ollama` | RAG chat with streaming response |
| GET | `/evaluation/retrieval?k=5` | Retrieval metrics evaluation |
| GET | `/evaluation/faithfulness?k=5&provider=openrouter&start=0&end=10` | Faithfulness evaluation |
| GET | `/evaluation/relevance?k=5&provider=openrouter&start=0&end=10` | Relevance evaluation |

## Configuration

Hardcoded in source (adjust in code if needed):

| Setting | Value | File |
|---------|-------|------|
| Qdrant URL | `http://localhost:6333` | `services/vector_store.py` |
| Embedding model | `all-MiniLM-L6-v2` | `services/embeder.py` |
| Reranker model | `ms-marco-MiniLM-L-6-v2` | `services/reranker.py` |
| OpenRouter model | `liquid/lfm-2.5-2.6b:free` | `services/llm.py` |
| Ollama model | `qwen3.5:4b` | `services/llm.py` |
| Chunk size | 500 chars | `services/chunker.py` |
| Chunk overlap | 3 sentences | `services/chunker.py` |
| Search candidates | 30 | `services/vector_store.py` |
