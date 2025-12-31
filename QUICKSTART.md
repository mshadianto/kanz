# 🚀 Quick Start Guide - KANZ

**Get running in 5 minutes!**

## 📋 Prerequisites

1. **Groq API Key** (FREE)
   - Go to: https://console.groq.com
   - Sign up → Get API Key
   - Copy key: `gsk_...`

2. **Supabase Account** (FREE)
   - Go to: https://supabase.com
   - Sign up → Create new project
   - Wait 2 minutes for provisioning

## ⚡ 5-Minute Setup

### Step 1: Clone & Install (2 min)

```bash
# Run automated setup
./setup.sh

# Follow prompts - will install all dependencies
```

### Step 2: Supabase Setup (1 min)

1. Open Supabase dashboard → Your Project → SQL Editor
2. Copy ALL content from `backend/setup_database.sql`
3. Paste in SQL Editor → Run
4. Verify: You should see 5 tables created

### Step 3: Get API Credentials (1 min)

In Supabase Dashboard:
1. Settings → API → Copy:
   - Project URL: `https://xxxxx.supabase.co`
   - anon (public): `eyJh...`
   - service_role: `eyJh...`

2. Settings → Database → Connection string:
   - Copy "URI" format
   - Replace `[YOUR-PASSWORD]` with your database password

### Step 4: Configure Environment (30 sec)

```bash
# Edit backend/.env
nano backend/.env

# Add your credentials:
GROQ_API_KEY=gsk_your_key_here
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key
DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres
```

### Step 5: Load Documents (30 sec)

```bash
cd backend
source venv/bin/activate  # Mac/Linux
# OR: venv\Scripts\activate  (Windows)

python ingest_documents.py
```

You should see:
```
✓ Ingested: Saudi Arabia Market Entry Strategy - Full Report
✓ Ingested: Executive One-Pager - Board Decision Brief
Total documents: 2
Total chunks: ~180
```

## 🎉 Start Application

### Option A: One Command (Recommended)

```bash
./run.sh
```

### Option B: Manual Start

Terminal 1:
```bash
cd backend
source venv/bin/activate
python main.py
```

Terminal 2:
```bash
cd frontend
npm run dev
```

## ✅ Verify It Works

1. **Backend**: http://localhost:8000/health
   - Should return: `{"status": "healthy"}`

2. **Frontend**: http://localhost:3000
   - You should see KANZ interface

3. **Test Query**:
   - Type: "What are the tax benefits in NEOM?"
   - Should get detailed response with sources

## 🎯 Usage Examples

### 1. Financial Analysis
```
Agent: Financial Advisor 💰
Query: "Calculate ROI for $200M data center investment"
```

### 2. Strategic Planning
```
Agent: Strategic Analyst 🎯
Query: "Compare NEOM vs KAEC for tech infrastructure"
```

### 3. Risk Assessment
```
Agent: Risk Assessor ⚠️
Query: "What are data sovereignty compliance requirements?"
```

### 4. General Questions
```
Agent: Auto (or General Advisor)
Query: "Give me an overview of Vision 2030 opportunities"
```

## 🐛 Troubleshooting

### "Module not found" errors
```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd frontend && npm install
```

### "Connection refused" to backend
```bash
# Check if backend is running
curl http://localhost:8000/health

# Restart backend
cd backend
source venv/bin/activate
python main.py
```

### "Database connection error"
```bash
# Test database connection
psql $DATABASE_URL

# If fails, verify DATABASE_URL in .env
```

### "No embeddings found"
```bash
# Re-run ingestion
cd backend
python ingest_documents.py
```

## 📚 What's Next?

- **Add documents**: Upload via UI or `POST /documents` API
- **Customize agents**: Edit `backend/agents.py`
- **Change UI theme**: Edit `frontend/tailwind.config.js`
- **Deploy**: See README.md deployment section

## 🆘 Need Help?

1. Check full documentation: `README.md`
2. View API docs: http://localhost:8000/docs
3. Check logs: `backend/logs/app_*.log`

---

**You're ready to analyze Saudi investment opportunities! 🇸🇦**
