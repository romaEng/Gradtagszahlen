#!/bin/bash

# Define color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check whether system is macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}Dieses Skript ist nur für macOS gedacht!${NC}"
    exit 1
fi

# Get absolute path to the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR" || exit

# Refresh Git-Repository
echo -e "${CYAN}Git Pull...${NC}"
git pull

# Activate virtual environment
echo -e "${CYAN}Aktiviere virtuelle Umgebung...${NC}"
if [ -d ".venv" ]; then
    source .venv/bin/activate
    pip install -r requirements.txt
else
    echo -e "${RED}Virtuelle Umgebung nicht gefunden. Erstelle neue Umgebung...${NC}"
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
fi

# Start python script
echo -e "${CYAN}Starte Anwendung...${NC}"

# Check for python version
if command -v python3 &> /dev/null; then
    python3 main.py
    check_error "Python-Skript wurde mit Fehler beendet"
elif command -v python &> /dev/null; then
    python main.py
    check_error "Python-Skript wurde mit Fehler beendet"
else
    handle_error "Python wurde nicht gefunden!"
fi

# Keep terminal open after execution
echo -e "${GREEN}Vorgang abgeschlossen. Zum Beenden [ENTER]...${NC}"
read
