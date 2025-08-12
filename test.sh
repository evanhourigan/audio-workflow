#!/bin/bash
# Test script for audio workflow orchestrator
# Uses config.test.yaml for testing

set -e

echo "🧪 Testing Audio Workflow Orchestrator with test configuration"
echo "   Config: config.test.yaml"
echo ""

# Check if test config exists
if [ ! -f "config.test.yaml" ]; then
    echo "❌ Test configuration file not found: config.test.yaml"
    echo "   Please create this file with your test database IDs"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Test basic functionality
echo "📋 Testing basic functionality..."
echo ""

echo "📊 Available databases:"
python3 audio-to-notion --config config.test.yaml --list-databases
echo ""

echo "🔄 Available workflows:"
python3 audio-to-notion --config config.test.yaml --list-workflows
echo ""

echo "✅ Test configuration loaded successfully!"
echo ""
echo "To test with a real audio file:"
echo "  python3 audio-to-notion --config config.test.yaml meeting.wav"
echo ""
echo "To use the test config by default, rename it:"
echo "  mv config.test.yaml config.yaml"
echo "  # (Remember to restore the template with: git checkout config.yaml)"
