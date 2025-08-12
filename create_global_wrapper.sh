#!/bin/bash
# Create global wrapper for audio-to-notion tool
# This follows the same pattern as your other tools (deepcast_post, notion_uploader)

set -e

# Get the project directory
PROJECT_DIR="$HOME/code/audio_workflow"

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Project directory not found: $PROJECT_DIR"
    echo "Please run this script from the audio_workflow project directory"
    exit 1
fi

# Create the global wrapper script
WRAPPER_SCRIPT="$HOME/.local/bin/audio-to-notion"

echo "🔧 Creating global wrapper for audio-to-notion..."
echo "   Project: $PROJECT_DIR"
echo "   Wrapper: $WRAPPER_SCRIPT"

# Create the wrapper script
cat > "$WRAPPER_SCRIPT" << 'EOF'
#!/bin/bash
# Global wrapper for audio-to-notion tool

# Get the project directory
PROJECT_DIR="$HOME/code/audio_workflow"

# Store the original working directory where the user ran the command
export AUDIO_WORKFLOW_ORIGINAL_CWD="$PWD"

# Run the tool using the virtual environment Python directly
cd "$PROJECT_DIR"
"$PROJECT_DIR/.venv/bin/python3" "$PROJECT_DIR/scripts/audio-to-notion" "$@"
EOF

# Make the wrapper executable
chmod +x "$WRAPPER_SCRIPT"

echo "✅ Global wrapper created successfully!"
echo ""
echo "You can now run audio-to-notion from anywhere:"
echo "  audio-to-notion meeting.wav"
echo "  audio-to-notion --list-workflows"
echo "  audio-to-notion --list-databases"
echo ""
echo "The tool will automatically:"
echo "  - Use your shell's environment variables (OPENAI_API_KEY, NOTION_API_KEY)"
echo "  - Use the appropriate config file based on your current directory"
echo "  - Run from the correct working directory"
echo ""
echo "Note: Make sure OPENAI_API_KEY and NOTION_API_KEY are set in your shell environment"
