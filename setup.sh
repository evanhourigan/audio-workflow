#!/bin/bash
# Setup script for Audio Workflow Orchestrator

set -e

echo "🚀 Setting up Audio Workflow Orchestrator..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "❌ pip is required but not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Install required dependencies
echo "📦 Installing required dependencies..."
source .venv/bin/activate
pip install -r requirements.txt

# Check if optional dependencies are available
echo "📦 Checking optional dependencies..."
if ! python3 -c "import dotenv" 2>/dev/null; then
    echo "⚠️  python-dotenv not installed. Install with: pip install python-dotenv"
fi

echo "✅ Dependencies checked"

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x audio-to-notion
chmod +x workflows/*.sh

# Create output and temp directories
echo "📁 Creating output directories..."
mkdir -p output temp

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Please copy env.example to .env and fill in your credentials:"
    echo "   cp env.example .env"
    echo "   # Then edit .env with your API keys"
else
    echo "✅ .env file found"
fi

# Check if config.yaml exists
if [ ! -f config.yaml ]; then
    echo "⚠️  config.yaml file not found. Please create it with your database mappings."
else
    echo "✅ config.yaml file found"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy env.example to .env and fill in your API keys"
echo "2. Edit config.yaml with your database IDs"
echo "3. Test with: ./audio-to-notion --list-workflows"
echo ""
echo "Usage examples:"
echo "  ./audio-to-notion meeting.wav"
echo "  ./workflows/quick_notes.sh meeting.wav 'Team Standup'"
echo "  ./workflows/full_analysis.sh meeting.wav 'Team Standup' meetings"
