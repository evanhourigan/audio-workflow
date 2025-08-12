#!/bin/bash
# Quick Notes Workflow
# Fast transcription and basic notes - minimal processing

set -e

AUDIO_FILE="$1"
TITLE="${2:-$(basename "$AUDIO_FILE" .wav | sed 's/_/ /g')}"

if [ -z "$AUDIO_FILE" ]; then
    echo "Usage: $0 <audio_file> [title]"
    echo "Example: $0 meeting.wav 'Team Standup'"
    exit 1
fi

if [ ! -f "$AUDIO_FILE" ]; then
    echo "❌ Audio file not found: $AUDIO_FILE"
    exit 1
fi

echo "🚀 Quick Notes Workflow"
echo "   File: $AUDIO_FILE"
echo "   Title: $TITLE"
echo "   Workflow: quick_notes"
echo

# Run the workflow
audio-to-notion "$AUDIO_FILE" \
    --title "$TITLE" \
    --workflow quick_notes \
    --database meetings

echo "✅ Quick notes workflow completed!"
