#!/bin/bash
# CipherGuard — Ek hi command se poora project start karo
# Engineered & Crafted by Raj
# Usage: bash run.sh
# Note: You may need to run 'chmod +x run.sh' before using it.

# -------------------------------------------------------
# Colors set karo terminal output ke liye
# -------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# -------------------------------------------------------
# Banner print karo startup pe
# -------------------------------------------------------
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════╗"
echo "║           C I P H E R G U A R D                 ║"
echo "║       Password Credential Audit Suite            ║"
echo "║         Engineered & Crafted by Raj              ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

# -------------------------------------------------------
# Python check karo — zaruri hai
# -------------------------------------------------------
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python3 nahi mila. Please install Python 3.10 or higher.${NC}"
    exit 1
fi

# -------------------------------------------------------
# Node.js check karo — zaruri hai
# -------------------------------------------------------
if ! command -v node &> /dev/null; then
    echo -e "${RED}[ERROR] Node.js nahi mila. Please install Node.js 18 or higher.${NC}"
    exit 1
fi

# -------------------------------------------------------
# .env file check karo
# -------------------------------------------------------
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}[WARNING] .env file nahi mili. Default values use ho rahe hain.${NC}"
fi

# -------------------------------------------------------
# Output directory banana — agar nahi hai toh
# -------------------------------------------------------
mkdir -p backend/output
echo -e "${GREEN}[1/4] Output directory ready hai.${NC}"

# -------------------------------------------------------
# Flask backend start karo background mein
# -------------------------------------------------------
echo -e "${GREEN}[2/4] Flask backend port 5000 pe start ho raha hai...${NC}"
python3 backend/app.py &
FLASK_PID=$!
sleep 2

# Flask check karo — sahi se start hua ya nahi
if kill -0 $FLASK_PID 2>/dev/null; then
    echo -e "${GREEN}      Flask backend successfully start hua! PID: $FLASK_PID${NC}"
else
    echo -e "${RED}[ERROR] Flask backend start nahi hua. Logs check karo.${NC}"
    exit 1
fi

# -------------------------------------------------------
# Node.js server start karo background mein
# -------------------------------------------------------
echo -e "${GREEN}[3/4] Node.js server port 3001 pe start ho raha hai...${NC}"
node backend/node_server/server.js &
NODE_PID=$!
sleep 1

if kill -0 $NODE_PID 2>/dev/null; then
    echo -e "${GREEN}      Node.js server successfully start hua! PID: $NODE_PID${NC}"
else
    echo -e "${YELLOW}[WARNING] Node.js server start nahi hua — Flask pe kaam chalega.${NC}"
fi

# -------------------------------------------------------
# Web UI open karo browser mein
# -------------------------------------------------------
echo -e "${GREEN}[4/4] Web UI browser mein open ho raha hai...${NC}"
sleep 1
xdg-open frontend/index.html 2>/dev/null || \
open frontend/index.html 2>/dev/null || \
echo -e "${YELLOW}      Browser automatically nahi khula. Manually open karo: frontend/index.html${NC}"

# -------------------------------------------------------
# Final status print karo
# -------------------------------------------------------
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  CipherGuard successfully start ho gaya!${NC}"
echo ""
echo -e "${YELLOW}  Web UI      :${NC} http://localhost:5000"
echo -e "${YELLOW}  Flask API   :${NC} http://localhost:5000/api"
echo -e "${YELLOW}  Node Server :${NC} http://localhost:3001"
echo -e "${YELLOW}  CLI Mode    :${NC} python3 backend/cli.py"
echo ""
echo -e "${YELLOW}  Rokna ho toh:${NC} Press Ctrl+C"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${CYAN}  Engineered & Crafted by Raj${NC}"
echo ""

# -------------------------------------------------------
# Cleanup karo jab Ctrl+C press ho
# -------------------------------------------------------
cleanup() {
    echo ""
    echo -e "${YELLOW}[SHUTDOWN] CipherGuard band ho raha hai...${NC}"
    kill $FLASK_PID 2>/dev/null
    kill $NODE_PID 2>/dev/null
    echo -e "${GREEN}[DONE] Sab servers band ho gaye. Goodbye!${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Processes ke saath wait karo
wait $FLASK_PID $NODE_PID
