#!/bin/bash
# Full Analysis Workflow
# Complete transcription, deepcast breakdown, and upload

set -e

AUDIO_FILE="$1"
TITLE="${2:-$(basename "$AUDIO_FILE" .wav | sed 's/_/ /g')}"
DATABASE="${3:-meetings}"

if [ -z "$AUDIO_FILE" ]; then
    echo "Usage: $0 <audio_file> [title] [database]"
    echo "Example: $0 meeting.wav 'Team Standup' meetings"
    echo "Example: $0 podcast.wav 'Episode 42' podcasts"
    exit 1
fi

if [ ! -f "$AUDIO_FILE" ]; then
    echo "❌ Audio file not found: $AUDIO_FILE"
    exit 1
fi

echo "🚀 Full Analysis Workflow"
echo "   File: $AUDIO_FILE"
echo "   Title: $TITLE"
echo "   Database: $DATABASE"
echo "   Workflow: full_analysis"
echo

# Run the workflow
audio-to-notion "$AUDIO_FILE" \
    --title "$TITLE" \
    --workflow full_analysis \
    --database "$DATABASE" \
    --keep-files

echo "✅ Full analysis workflow completed!"
echo "   Intermediate files kept for review"
