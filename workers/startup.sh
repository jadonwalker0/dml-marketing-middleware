#!/usr/bin/env bash
set -euo pipefail

echo "Starting Lead Processing Worker..."
cd /home/site/wwwroot

echo "Python version:"
python --version

echo "Installing dependencies..."
pip install -r workers/requirements.txt

echo "Starting worker process..."
exec python workers/process_leads.py