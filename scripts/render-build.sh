#!/bin/bash

# Render.com build script for Email Bot
# This script prepares the application for deployment

echo "🚀 Starting Render.com build process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Verify critical packages
echo "🔍 Verifying installation..."
python -c "import fastapi; print('✅ FastAPI installed')"
python -c "import uvicorn; print('✅ Uvicorn installed')"
python -c "import pymongo; print('✅ PyMongo installed')"

echo "✅ Build completed successfully!"
echo "🎯 Ready for deployment with command: python3 -m uvicorn server.main:app --host 0.0.0.0 --port \$PORT" 