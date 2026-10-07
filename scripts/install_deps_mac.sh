#!/bin/bash
set -e

echo "=== SlopeGuard Local Setup Script ==="

if ! command -v brew &> /dev/null
then
    echo "Homebrew not found. Please install Homebrew first."
    exit 1
fi

echo "[1/4] Installing PostgreSQL, PostGIS, and Redis..."
brew update
brew install postgresql postgis redis || true

echo "[2/4] Starting services..."
brew services start postgresql || true
brew services start redis || true

echo "[3/4] Creating SlopeGuard database..."
# Give postgres a moment to start
sleep 3
createdb slopeguard || echo "Database might already exist, continuing..."
psql -d slopeguard -c "CREATE EXTENSION IF NOT EXISTS postgis;" || echo "Failed to create postgis extension, please check Postgres."

echo "[4/4] Installing Python Dependencies..."
cd "$(dirname "$0")/.."

if [ ! -d "backend/venv" ]; then
    echo "Creating backend venv..."
    python3 -m venv backend/venv
fi
echo "Installing backend dependencies..."
source backend/venv/bin/activate
pip install -r backend/requirements.txt
cd backend
alembic init migrations || true
cd ..

if [ ! -d "ml/venv" ]; then
    echo "Creating ml venv..."
    python3 -m venv ml/venv
fi
echo "Installing ML dependencies..."
source ml/venv/bin/activate
pip install -r ml/requirements.txt

echo "=== Setup Complete! ==="
echo "To start the backend API:"
echo "cd backend && source venv/bin/activate && uvicorn main:app --reload"
