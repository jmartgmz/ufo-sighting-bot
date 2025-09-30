#!/bin/bash
"""
UFO Sighting Bot Setup Script
Helps set up the bot for first-time use.
"""

echo "🛸 UFO Sighting Bot Setup"
echo "========================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your Discord bot token"
else
    echo "✅ .env file already exists"
fi

# Create data directory structure
mkdir -p data logs

echo ""
echo "🚀 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your Discord bot token"
echo "2. Run the bot with: python run_bot.py"
echo ""
echo "For more information, see README.md"