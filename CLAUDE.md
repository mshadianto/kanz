# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**KANZ** (كنز - "Treasure") - A multi-agent RAG system for Saudi Arabia investment analysis. Full-stack application with FastAPI backend and Next.js frontend, using Groq LLM and Supabase pgvector for semantic search.

**Tagline**: "Uncover Hidden Opportunities in the Heart of the Desert"

## Development Commands

### Backend (from `/backend`)
```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start development server
python main.py
# OR with hot reload
uvicorn main:app --reload --port 8000

# Ingest documents into vector database
python ingest_documents.py
```

### Frontend (from `/frontend`)
```bash
npm install          # Install dependencies
npm run dev          # Development server (port 3000)
npm run build        # Production build
npm run lint         # ESLint
```

### Combined Startup
```bash
./setup.sh           # First-time setup (checks prereqs, creates venv, npm install)
./run.sh             # Start both backend and frontend concurrently
```

### API Testing
- Swagger UI: http://localhost:8000/docs
- Health check: `curl http://localhost:8000/health`

## Architecture

### Multi-Agent System
The system uses a **Coordinator pattern** in `backend/agents.py`:
- **CoordinatorAgent** routes queries using a fast LLM (llama3-8b) to determine the appropriate specialist
- **StrategicAnalystAgent** - Vision 2030, market entry, competitive positioning
- **FinancialAdvisorAgent** - Tax, ROI, incentives, financial modeling
- **RiskAssessmentAgent** - Regulatory compliance, geopolitical risk, mitigation
- **GeneralAdvisorAgent** - Fallback for non-specialized queries

Query routing: `CoordinatorAgent.route_query()` → specialized agent → RAG context injection → LLM response

### RAG Pipeline
1. Document ingestion (`ingest_documents.py`) → text cleaning → chunking (1000 chars, 200 overlap)
2. Embedding generation via sentence-transformers (all-MiniLM-L6-v2, 384-dim vectors)
3. Vector storage in Supabase pgvector with IVFFlat indexing
4. Query → embed → similarity search → context injection → agent response

### Key Files
| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI app with 11 REST endpoints |
| `backend/agents.py` | Multi-agent system with BaseAgent class and 4 specialized agents |
| `backend/config.py` | Pydantic Settings - all env vars and app configuration |
| `backend/database.py` | Supabase CRUD operations and vector search |
| `backend/document_processor.py` | Text chunking, embedding, and indexing |
| `frontend/lib/store.ts` | Zustand state management (sessions, messages, agents) |
| `frontend/lib/api.ts` | Axios client with typed API methods |
| `frontend/components/ChatInterface.tsx` | Main chat UI component |

### Database Schema (Supabase)
5 tables: `documents`, `document_chunks` (with vector embeddings), `chat_sessions`, `chat_messages`, `query_analytics`

Schema defined in `backend/setup_database.sql`

## Environment Variables

### Backend (`backend/.env`)
```
GROQ_API_KEY=gsk_...          # Required - Groq API key
SUPABASE_URL=https://...      # Required - Supabase project URL
SUPABASE_KEY=...              # Required - Supabase anon key
SUPABASE_SERVICE_KEY=...      # Required - Supabase service role key
DATABASE_URL=postgresql://... # Required - Supabase connection string

# Optional (with defaults)
LLM_MODEL=mixtral-8x7b-32768
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
```

### Frontend (`frontend/.env.local`)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Code Patterns

### Adding a New Agent
1. Create new class extending `BaseAgent` in `agents.py`
2. Define specialized `system_prompt` in constructor
3. Add to `AgentType` enum
4. Register in `CoordinatorAgent.__init__` and `agent_map`
5. Update routing prompt in `route_query()`

### API Endpoints Pattern
All endpoints in `main.py` follow:
- Pydantic models for request/response validation
- Try/except with logger.error and HTTPException
- Async database operations via `db` module

### Frontend State
Zustand store in `lib/store.ts` manages: current session, messages, available agents, loading states. Actions are async and call `lib/api.ts` methods.

## Deployment

### Backend (Railway/Render)
```bash
gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

### Frontend (Vercel)
Set `NEXT_PUBLIC_API_URL` to production backend URL.
