#!/bin/bash

# KANZ - Run Script
# Start backend dan frontend dalam satu command

set -e

echo "═══════════════════════════════════════════════════════════"
echo "  KANZ - Starting Application"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

# Start backend
echo -e "${GREEN}Starting backend...${NC}"
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "Waiting for backend to initialize..."
sleep 3

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${YELLOW}Warning: Backend may not have started properly${NC}"
fi

# Start frontend
echo -e "${GREEN}Starting frontend...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "═══════════════════════════════════════════════════════════"
echo -e "${GREEN}✓ Application started!${NC}"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:3000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo "═══════════════════════════════════════════════════════════"

# Wait for processes
wait
