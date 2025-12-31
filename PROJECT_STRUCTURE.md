# KANZ - Project Structure

```
kanz/
├── README.md                          # Comprehensive documentation
├── .gitignore                         # Git ignore patterns
├── setup.sh                           # Automated setup script
├── run.sh                             # Start both backend & frontend
│
├── backend/                           # FastAPI backend
│   ├── requirements.txt               # Python dependencies
│   ├── .env.example                   # Environment template
│   ├── setup_database.sql             # Supabase schema setup
│   │
│   ├── config.py                      # Configuration management
│   ├── database.py                    # Supabase/pgvector operations
│   ├── embeddings.py                  # Sentence transformers embeddings
│   ├── document_processor.py          # Chunking & indexing
│   ├── agents.py                      # Multi-agent system
│   ├── main.py                        # FastAPI application
│   │
│   └── ingest_documents.py            # Initial document ingestion
│
├── frontend/                          # Next.js frontend
│   ├── package.json                   # Node dependencies
│   ├── next.config.js                 # Next.js configuration
│   ├── tailwind.config.js             # Tailwind CSS (MacOS theme)
│   ├── tsconfig.json                  # TypeScript configuration
│   ├── postcss.config.js              # PostCSS configuration
│   │
│   ├── app/                           # Next.js App Router
│   │   ├── layout.tsx                 # Root layout
│   │   ├── page.tsx                   # Main page
│   │   └── globals.css                # Global styles (MacOS)
│   │
│   ├── components/                    # React components
│   │   ├── ChatInterface.tsx          # Main chat UI
│   │   └── Sidebar.tsx                # Session & agent selector
│   │
│   └── lib/                           # Utilities
│       ├── api.ts                     # API client
│       └── store.ts                   # Zustand state management
│
└── data/                              # (auto-created) Documents to index
```

## 🔑 Key Files Explained

### Backend Core

**`config.py`**
- Loads environment variables
- Configures LLM, embeddings, RAG parameters
- Provides settings singleton

**`database.py`**
- Supabase client wrapper
- CRUD operations for documents, chunks, sessions
- Vector similarity search via pgvector

**`embeddings.py`**
- sentence-transformers integration
- Batch embedding processing
- Cosine similarity calculations

**`document_processor.py`**
- Text cleaning & normalization
- Recursive character text splitting
- Document chunking & indexing pipeline

**`agents.py`**
- Multi-agent architecture
- 4 specialized agents + coordinator
- Query routing logic
- LangChain + Groq integration

**`main.py`**
- FastAPI application
- REST API endpoints
- CORS configuration
- Error handling

### Frontend Core

**`app/page.tsx`**
- Main application entry
- Layout composition

**`components/ChatInterface.tsx`**
- Message display
- Input handling
- Markdown rendering
- Source citations

**`components/Sidebar.tsx`**
- Session management UI
- Agent selector
- Navigation

**`lib/api.ts`**
- Axios client
- Type-safe API calls
- Error handling

**`lib/store.ts`**
- Zustand state store
- Async actions
- Session management

## 🎨 Styling System

**MacOS Design Tokens** (`tailwind.config.js`):
- Colors: `macos-blue`, `macos-gray-*`, `saudi-green`
- Fonts: SF Pro (system font stack)
- Shadows: `shadow-macos`, `shadow-macos-lg`
- Border radius: `rounded-macos`, `rounded-macos-lg`

**Utility Classes** (`globals.css`):
- `.card-macos`: Card component
- `.btn-macos`: Button base
- `.input-macos`: Input field
- `.message-bubble`: Chat bubble
- `.markdown-content`: Markdown styling

## 🔄 Data Flow

### Query Processing Flow

```
User Input
  ↓
Frontend (store.sendMessage)
  ↓
API Client (POST /query)
  ↓
Backend (main.py)
  ↓
Coordinator Agent
  ↓
Query Routing (determine agent type)
  ↓
Document Processor (retrieve context)
  ↓
Vector Search (Supabase/pgvector)
  ↓
Specialized Agent (generate response)
  ↓
Database (save message)
  ↓
Response to Frontend
  ↓
UI Update (add message to chat)
```

### Document Ingestion Flow

```
Document Text
  ↓
Document Processor
  ↓
Text Cleaning
  ↓
Chunking (RecursiveCharacterTextSplitter)
  ↓
Embedding Generation (sentence-transformers)
  ↓
Supabase Storage
  ├── documents table (metadata)
  └── document_chunks table (text + vector)
```

## 🧪 Testing Endpoints

```bash
# Health check
curl http://localhost:8000/health

# List agents
curl http://localhost:8000/agents

# Create session
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"session_name": "Test Session"}'

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are NEOM tax benefits?",
    "agent_type": "financial"
  }'
```

## 📊 Database Tables

**documents**
- Primary storage for source documents
- Fields: id, title, content, source, metadata

**document_chunks**
- Chunked text with embeddings
- Fields: id, document_id, content, embedding (vector), metadata
- Index: ivfflat for fast similarity search

**chat_sessions**
- User conversation sessions
- Fields: id, session_name, metadata

**chat_messages**
- Individual messages in sessions
- Fields: id, session_id, role, content, agent_type, sources

**query_analytics**
- Performance tracking
- Fields: id, session_id, query, agent_type, response_time_ms

## 🔐 Environment Variables

### Backend Required
```env
GROQ_API_KEY=gsk_...              # Groq API key
SUPABASE_URL=https://...          # Supabase project URL
SUPABASE_KEY=eyJ...               # Supabase anon key
SUPABASE_SERVICE_KEY=eyJ...       # Supabase service role key
DATABASE_URL=postgresql://...     # Postgres connection string
```

### Backend Optional
```env
LLM_MODEL=mixtral-8x7b-32768     # Groq model selection
CHUNK_SIZE=1000                   # Text chunk size
CHUNK_OVERLAP=200                 # Chunk overlap
TOP_K_RESULTS=5                   # Number of retrieval results
```

### Frontend
```env
NEXT_PUBLIC_API_URL=http://localhost:8000  # Backend API URL
```

## 🚀 Quick Commands

```bash
# Setup (one-time)
./setup.sh

# Run application
./run.sh

# Manual backend start
cd backend && source venv/bin/activate && python main.py

# Manual frontend start
cd frontend && npm run dev

# Ingest documents
cd backend && python ingest_documents.py

# View logs
tail -f backend/logs/app_*.log
```

## 📈 Performance Considerations

### Backend
- **Embedding caching**: Prevents re-computing same query embeddings
- **Batch processing**: Chunks processed in batches for speed
- **Connection pooling**: Supabase client reuses connections

### Frontend
- **Optimistic UI**: Messages appear immediately
- **Lazy loading**: Sessions loaded on-demand
- **Debouncing**: Input handling optimized

### Database
- **Vector indexes**: ivfflat index for fast similarity search
- **RLS policies**: Row-level security enabled
- **Prepared statements**: SQL injection prevention

## 🔧 Customization Points

1. **Add new agents**: Extend `agents.py` with new agent classes
2. **Change LLM**: Update `LLM_MODEL` in `.env`
3. **Adjust chunking**: Modify `CHUNK_SIZE` and `CHUNK_OVERLAP`
4. **Custom UI theme**: Edit `tailwind.config.js` colors
5. **Add documents**: Upload via UI or run `ingest_documents.py`

## 📝 Code Quality

- **Type hints**: Python type annotations throughout
- **TypeScript**: Full type safety in frontend
- **Error handling**: Try-catch blocks, proper error messages
- **Logging**: Loguru for structured logging
- **Validation**: Pydantic models for request/response validation
