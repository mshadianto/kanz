# KANZ - AI Investment Advisor

🇸🇦 **Uncover Hidden Opportunities in the Heart of the Desert**

KANZ (كنز - "Treasure") is an AI-powered Multi-Agent RAG system for Saudi Arabia investment analysis.

## 🎯 Features

- **Multi-Agent Architecture**: 4 specialized agents (Strategic, Financial, Risk, General)
- **RAG System**: Vector search dengan Supabase/pgvector  
- **Free Tier**: Groq API (Mixtral-8x7B) + Supabase free tier
- **MacOS UI/UX**: Clean, modern interface dengan design language macOS
- **Real-time Chat**: Session management dan chat history
- **Source Citations**: Transparansi dengan source references
- **Analytics**: Query tracking dan performance monitoring

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                      │
│  - MacOS-style UI dengan Tailwind CSS                       │
│  - Zustand state management                                 │
│  - Real-time chat interface                                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ REST API
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Coordinator Agent                          │  │
│  │  (Query routing & orchestration)                     │  │
│  └────┬──────────┬──────────┬──────────┬────────────────┘  │
│       │          │          │          │                    │
│  ┌────▼───┐ ┌───▼────┐ ┌───▼────┐ ┌───▼────┐             │
│  │Strategic│ │Financial│ │  Risk  │ │General │             │
│  │ Analyst │ │ Advisor │ │Assessor│ │Advisor │             │
│  └────┬───┘ └───┬────┘ └───┬────┘ └───┬────┘             │
│       │          │          │          │                    │
│       └──────────┴──────────┴──────────┘                    │
│                     │                                        │
│         ┌───────────▼────────────┐                          │
│         │  Document Processor    │                          │
│         │  - Chunking            │                          │
│         │  - Embedding           │                          │
│         └───────────┬────────────┘                          │
│                     │                                        │
└─────────────────────┼────────────────────────────────────────┘
                      │
                      │ pgvector
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Supabase (Postgres + pgvector)                  │
│  - Document storage                                          │
│  - Vector embeddings (384-dim)                               │
│  - Chat sessions & messages                                  │
│  - Analytics                                                 │
└──────────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

### Accounts & API Keys

1. **Groq API** (Free)
   - Sign up: https://console.groq.com
   - Get API key
   - Free tier: 30 requests/minute, 6,000 tokens/minute

2. **Supabase** (Free)
   - Sign up: https://supabase.com
   - Create new project
   - Get URL + anon key + service role key
   - Free tier: 500MB database, 1GB file storage

### Local Requirements

- Node.js 18+ & npm
- Python 3.9+
- Git

## 🚀 Quick Start

### 1. Clone & Setup

```bash
# Clone repository
git clone <your-repo>
cd kanz

# Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup frontend
cd ../frontend
npm install
```

### 2. Supabase Setup

#### a. Create Supabase Project
1. Go to https://supabase.com/dashboard
2. Create new project
3. Wait for provisioning (~2 minutes)

#### b. Run Database Setup
1. Go to SQL Editor in Supabase dashboard
2. Copy content dari `backend/setup_database.sql`
3. Run SQL script
4. Verify tables created: `documents`, `document_chunks`, `chat_sessions`, dll

#### c. Get API Credentials
- Project URL: Settings → API → Project URL
- Anon Key: Settings → API → anon (public)
- Service Key: Settings → API → service_role (secret)

### 3. Environment Configuration

#### Backend (.env)
```bash
cd backend
cp .env.example .env
nano .env  # atau text editor favorit
```

Update dengan credentials:
```env
GROQ_API_KEY=gsk_your_actual_groq_key
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key
DATABASE_URL=postgresql://postgres:your_password@db.xxxxx.supabase.co:5432/postgres
```

#### Frontend (.env.local)
```bash
cd ../frontend
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

### 4. Load Initial Documents

```bash
cd backend

# Pastikan venv active
source venv/bin/activate

# Run ingestion script
python ingest_documents.py
```

Output yang diharapkan:
```
✓ Ingested: Saudi Arabia Market Entry Strategy - Full Report
✓ Ingested: Executive One-Pager - Board Decision Brief
Total documents: 2
Total chunks: ~150-200
```

### 5. Start Application

#### Terminal 1 - Backend
```bash
cd backend
source venv/bin/activate
python main.py

# atau
uvicorn main:app --reload --port 8000
```

Verify: http://localhost:8000/health

#### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

Open: http://localhost:3000

## 🎨 UI Preview

### Main Chat Interface
- **MacOS-style design**: Rounded corners, subtle shadows, SF Pro font
- **Agent selection**: 4 specialized advisors + auto-routing
- **Real-time responses**: Streaming dari Groq LLM
- **Source citations**: Transparent references ke original documents

### Sidebar
- **Session management**: Create, load, delete conversations
- **Agent selector**: Visual cards untuk setiap agent
- **History**: Persistent chat sessions

## 🤖 Available Agents

### 1. Strategic Analyst 🎯
**Specialty**: Market entry, Vision 2030, competitive positioning
```
Example query:
"Compare NEOM vs KAEC for AI infrastructure investment"
```

### 2. Financial Advisor 💰
**Specialty**: Tax optimization, ROI, incentive calculations
```
Example query:
"Calculate NPV for $200M data center with CAPEX reimbursement"
```

### 3. Risk Assessor ⚠️
**Specialty**: Regulatory compliance, geopolitical risk, mitigation
```
Example query:
"What are data sovereignty requirements and how to comply?"
```

### 4. General Advisor 💡
**Specialty**: Overview, general questions, routing
```
Example query:
"Give me an overview of Saudi investment opportunities"
```

## 📊 Technical Details

### Backend Stack
- **Framework**: FastAPI 0.109
- **LLM**: Groq (Mixtral-8x7B-32K)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2, 384-dim)
- **Vector DB**: Supabase/pgvector
- **RAG**: LangChain 0.1

### Frontend Stack
- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS 3.3
- **State**: Zustand 4.5
- **UI**: Lucide Icons, Framer Motion
- **Markdown**: react-markdown + remark-gfm

### Database Schema
```sql
documents
├── id (uuid)
├── title (text)
├── content (text)
├── source (text)
└── metadata (jsonb)

document_chunks
├── id (uuid)
├── document_id (uuid FK)
├── content (text)
├── embedding (vector(384))
└── metadata (jsonb)

chat_sessions
├── id (uuid)
├── session_name (text)
└── metadata (jsonb)

chat_messages
├── id (uuid)
├── session_id (uuid FK)
├── role (text: user/assistant)
├── content (text)
├── agent_type (text)
└── sources (jsonb)
```

## 🔧 Advanced Configuration

### LLM Model Selection
Edit `backend/.env`:
```env
# Options:
# - mixtral-8x7b-32768 (best quality, slower)
# - llama3-70b-8192 (balanced)
# - llama3-8b-8192 (fastest, lower quality)
LLM_MODEL=mixtral-8x7b-32768
```

### Chunk Size Optimization
Edit `backend/.env`:
```env
CHUNK_SIZE=1000  # Smaller = more precise, larger = more context
CHUNK_OVERLAP=200  # Higher = better continuity
TOP_K_RESULTS=5  # Number of chunks to retrieve
```

### UI Customization
Edit `frontend/tailwind.config.js` untuk custom colors/fonts.

## 📝 API Documentation

Backend automatically generates OpenAPI docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

```typescript
// Query endpoint
POST /query
{
  "query": "What are tax incentives in NEOM?",
  "session_id": "optional-uuid",
  "agent_type": "financial"  // optional
}

// Create session
POST /sessions
{
  "session_name": "Board Meeting Analysis"
}

// List agents
GET /agents

// Upload document
POST /documents
{
  "title": "New Analysis Report",
  "content": "Document text...",
  "source": "user_upload"
}
```

## 🐛 Troubleshooting

### Backend tidak start
```bash
# Check ports
lsof -i :8000

# Verify dependencies
pip list | grep -E "fastapi|langchain|supabase"

# Check logs
tail -f logs/app_*.log
```

### Frontend connection error
```bash
# Verify backend running
curl http://localhost:8000/health

# Check environment
cat .env.local

# Clear Next.js cache
rm -rf .next
npm run dev
```

### Supabase connection issues
```bash
# Test connection
psql $DATABASE_URL

# Verify pgvector extension
psql $DATABASE_URL -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

### Embedding errors
```bash
# Re-download model
rm -rf ~/.cache/torch/sentence_transformers
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

## 📈 Performance Tips

1. **Groq Rate Limits**: Free tier = 30 req/min
   - Implement request queuing jika high traffic
   - Monitor via Groq dashboard

2. **Embedding Speed**: 
   - Batch processing untuk multiple chunks
   - Cache embeddings untuk repeated queries

3. **Database Performance**:
   - Supabase indexes already optimized in setup script
   - Monitor query performance di Dashboard → Performance

## 🔐 Security Best Practices

1. **Never commit .env files**
   ```bash
   git rm --cached backend/.env frontend/.env.local
   ```

2. **Use environment-specific keys**
   - Development: `.env.development`
   - Production: `.env.production`

3. **Supabase RLS** (Row Level Security)
   - Already configured in setup script
   - Adjust policies untuk multi-user scenarios

## 📦 Deployment

### Backend (Railway/Render/Fly.io)
```bash
# Install dependencies
pip install -r requirements.txt

# Run with gunicorn
gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

### Frontend (Vercel/Netlify)
```bash
# Build
npm run build

# Environment variables
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

## 🤝 Contributing

Contributions welcome! Steps:
1. Fork repository
2. Create feature branch
3. Test thoroughly
4. Submit pull request

## 📄 License

MIT License - feel free to use for your projects.

## 🙏 Credits

- **LLM**: Groq (Mixtral-8x7B)
- **Vector DB**: Supabase/pgvector
- **UI Inspiration**: macOS Big Sur design language
- **Data**: Saudi Arabia investment analysis (August 2025)

## 📞 Support

Issues? Questions?
1. Check troubleshooting section
2. Open GitHub issue
3. Check Groq/Supabase status pages

---

**Built with ❤️ for Indonesian investors exploring Saudi opportunities**
