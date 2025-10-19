#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${GREEN}Starting Traffic Dashboard...${NC}\n"

# Start backend
echo -e "${YELLOW}Starting backend on port 8000...${NC}"
cd "$PROJECT_DIR/backend"
source venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo -e "${YELLOW}Starting frontend on port 3000...${NC}"
cd "$PROJECT_DIR/frontend"
npm start &
FRONTEND_PID=$!

echo -e "\n${GREEN}✓ Dashboard is starting!${NC}"
echo -e "${GREEN}✓ Backend: http://localhost:8000${NC}"
echo -e "${GREEN}✓ Frontend: http://localhost:3000${NC}"
echo -e "\n${YELLOW}Press Ctrl+C to stop both services${NC}\n"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
