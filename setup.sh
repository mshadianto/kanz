#!/bin/bash

# KANZ - Setup Script
# Automated setup untuk backend dan frontend

set -e  # Exit on error

echo "═══════════════════════════════════════════════════════════"
echo "  KANZ - Automated Setup"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.9+${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js found${NC}"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm not found. Please install npm${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npm found${NC}"

echo ""
echo "─────────────────────────────────────────────────────────────"
echo "Step 1: Backend Setup"
echo "─────────────────────────────────────────────────────────────"

cd backend

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating from template...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit backend/.env with your API keys:${NC}"
    echo "   - GROQ_API_KEY (get from https://console.groq.com)"
    echo "   - SUPABASE_URL"
    echo "   - SUPABASE_KEY"
    echo "   - SUPABASE_SERVICE_KEY"
    echo "   - DATABASE_URL"
    echo ""
    read -p "Press Enter after you've updated .env file..."
fi

echo -e "${GREEN}✓ Backend setup complete${NC}"

cd ..

echo ""
echo "─────────────────────────────────────────────────────────────"
echo "Step 2: Frontend Setup"
echo "─────────────────────────────────────────────────────────────"

cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

# Check for .env.local file
if [ ! -f .env.local ]; then
    echo -e "${YELLOW}⚠️  No .env.local file found. Creating...${NC}"
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
fi

echo -e "${GREEN}✓ Frontend setup complete${NC}"

cd ..

echo ""
echo "─────────────────────────────────────────────────────────────"
echo "Step 3: Database Setup"
echo "─────────────────────────────────────────────────────────────"

echo "Before proceeding, make sure you have:"
echo "  1. Created a Supabase project at https://supabase.com"
echo "  2. Run the SQL script from backend/setup_database.sql in Supabase SQL Editor"
echo "  3. Updated backend/.env with your Supabase credentials"
echo ""
read -p "Have you completed these steps? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⚠️  Please complete database setup and run this script again${NC}"
    exit 0
fi

echo ""
echo "─────────────────────────────────────────────────────────────"
echo "Step 4: Document Ingestion"
echo "─────────────────────────────────────────────────────────────"

read -p "Do you want to ingest initial documents now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd backend
    source venv/bin/activate
    
    echo "Ingesting documents..."
    python ingest_documents.py
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Documents ingested successfully${NC}"
    else
        echo -e "${RED}❌ Document ingestion failed${NC}"
        echo "You can run it manually later: cd backend && python ingest_documents.py"
    fi
    
    cd ..
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "To start the application:"
echo ""
echo "  Terminal 1 (Backend):"
echo "    cd backend"
echo "    source venv/bin/activate"
echo "    python main.py"
echo ""
echo "  Terminal 2 (Frontend):"
echo "    cd frontend"
echo "    npm run dev"
echo ""
echo "Then open: http://localhost:3000"
echo ""
echo "═══════════════════════════════════════════════════════════"
