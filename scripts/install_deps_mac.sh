#!/bin/bash
echo "Installing PostgreSQL, PostGIS, and Redis..."
brew install postgresql postgis redis

echo "Starting services..."
brew services start postgresql
brew services start redis

echo "Creating SlopeGuard database..."
createdb slopeguard || echo "Database might already exist"
psql -d slopeguard -c "CREATE EXTENSION IF NOT EXISTS postgis;"
