#!/bin/bash

# Navigate to the project directory (optional, only needed if script might be called from elsewhere)
cd "$(dirname "$0")"

# Activate the virtual environment
source venv/bin/activate

# Run the server
# python src/server.py
PYTHONWARNINGS="ignore" python src/server.py 2>/dev/null
