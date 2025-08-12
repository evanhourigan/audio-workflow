#!/bin/bash
# Setup personal configuration for audio workflow orchestrator
# This creates configuration files in your home directory

set -e

echo "🏠 Setting up personal audio workflow configuration..."
echo ""

# Get home directory
HOME_DIR="$HOME"
PERSONAL_CONFIG="$HOME_DIR/.audio-workflow.yaml"
CONFIG_DIR="$HOME_DIR/.config/audio-workflow"

echo "📁 Creating personal configuration..."

# Create config directory if it doesn't exist
mkdir -p "$CONFIG_DIR"

# Check if personal config already exists
if [ -f "$PERSONAL_CONFIG" ]; then
    echo "⚠️  Personal config already exists: $PERSONAL_CONFIG"
    echo "   Edit it to add your database IDs:"
    echo "   nano $PERSONAL_CONFIG"
else
    # Copy template and create personal config
    cp config.yaml "$PERSONAL_CONFIG"
    echo "✅ Created personal config: $PERSONAL_CONFIG"
    echo "   Edit it to add your database IDs:"
    echo "   nano $PERSONAL_CONFIG"
fi

# Create alternative config location
ALT_CONFIG="$CONFIG_DIR/config.yaml"
if [ -f "$ALT_CONFIG" ]; then
    echo "⚠️  Alternative config already exists: $ALT_CONFIG"
else
    cp config.yaml "$ALT_CONFIG"
    echo "✅ Created alternative config: $ALT_CONFIG"
    echo "   Edit it to add your database IDs:"
    echo "   nano $ALT_CONFIG"
fi

echo ""
echo "🎯 Configuration Priority (highest to lowest):"
echo "   1. --config flag (explicit file)"
echo "   2. ./audio-workflow.yaml (current directory)"
echo "   3. ./config.yaml (current directory)"
echo "   4. ~/.audio-workflow.yaml (home directory)"
echo "   5. ~/.config/audio-workflow/config.yaml (config directory)"
echo "   6. AUDIO_WORKFLOW_CONFIG environment variable"
echo "   7. Project config.yaml (fallback)"
echo ""
echo "💡 Usage examples:"
echo "   # Use personal config from anywhere"
echo "   audio-to-notion meeting.wav"
echo ""
echo "   # Use specific config file"
echo "   audio-to-notion --config ~/.audio-workflow.yaml meeting.wav"
echo ""
echo "   # Use environment variable"
echo "   export AUDIO_WORKFLOW_CONFIG=~/my-config.yaml"
echo "   audio-to-notion meeting.wav"
