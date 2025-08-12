#!/bin/bash
# Podcast Episode Workflow
# Podcast-specific processing with enhanced analysis

set -e

AUDIO_FILE="$1"
TITLE="${2:-$(basename "$AUDIO_FILE" .wav | sed 's/_/ /g')}"
EPISODE_NUM="${3:-}"

if [ -z "$AUDIO_FILE" ]; then
    echo "Usage: $0 <audio_file> [title] [episode_number]"
    echo "Example: $0 podcast.wav 'Episode 42: AI Revolution' 42"
    echo "Example: $0 interview.wav 'Interview with John Doe'"
    exit 1
fi

if [ ! -f "$AUDIO_FILE" ]; then
    echo "❌ Audio file not found: $AUDIO_FILE"
    exit 1
fi

echo "🚀 Podcast Episode Workflow"
echo "   File: $AUDIO_FILE"
echo "   Title: $TITLE"
if [ -n "$EPISODE_NUM" ]; then
    echo "   Episode: $EPISODE_NUM"
fi
echo "   Workflow: podcast_episode"
echo "   Database: podcasts"
echo

# Run the workflow
audio-to-notion "$AUDIO_FILE" \
    --title "$TITLE" \
    --workflow podcast_episode \
    --database podcasts \
    --keep-files

echo "✅ Podcast episode workflow completed!"
echo "   Enhanced analysis with podcast-specific metadata"
