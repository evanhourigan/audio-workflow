# Audio Workflow Orchestrator

An audio workflow orchestrator that chains `transcribe` → `deepcast` → `notion-upload` with hybrid configuration support.

## 🎯 What It Does

This tool automates the complete audio processing pipeline:

1. **Transcribe** audio files using your `transcribe` tool
2. **Generate deepcast breakdowns** using your `deepcast` tool
3. **Upload to Notion** using your `notion-upload` tool

## 🚀 Quick Start

### 1. Install Dependencies

The tool requires Python 3 and some dependencies. Run the setup script to create a virtual environment and install dependencies:

```bash
./setup.sh
```

Or manually:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and fill in your credentials:

```bash
cp env.example .env
# Edit .env with your API keys
```

### 3. Configure Workflows

Edit `config.yaml` with your database IDs and workflow preferences.

**For Testing**: Create a `config.test.yaml` file with real database IDs to test the tool without affecting the template configuration.

### 4. Run a Workflow

```bash
# Use defaults
./audio-to-notion meeting.wav

# Override title
./audio-to-notion meeting.wav --title "Team Standup"

# Use specific database
./audio-to-notion meeting.wav --database meetings

# Use specific workflow
./audio-to-notion meeting.wav --workflow full_analysis
```

## 📁 Project Structure

```
~/code/audio_workflow/
├── .env                    # Default credentials
├── config.yaml            # Database mappings, workflows
├── audio-to-notion        # Main script
├── workflows/             # Different workflow types
│   ├── quick_notes.sh
│   ├── full_analysis.sh
│   └── podcast_episode.sh
└── README.md
```

## ⚙️ Configuration Priority

The tool automatically discovers configuration files in this order (highest to lowest priority):

1. **Command line arguments** (most specific)
2. **Explicit `--config` file** (if specified)
3. **Current directory** (`./audio-workflow.yaml`, `./config.yaml`)
4. **User config directory** (`~/.config/audio-workflow/config.yaml`)
5. **User home directory** (`~/.audio-workflow.yaml`)
6. **Environment variable** (`AUDIO_WORKFLOW_CONFIG`)
7. **Project `config.yaml`** (fallback)

## 🔧 Configuration

### Environment Variables (.env)

```bash
# OpenAI API Configuration (for deepcast)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7

# Notion API Configuration (for notion-upload)
NOTION_API_KEY=your-notion-api-key-here
NOTION_DATABASE_ID=your-default-database-id-here

# Workflow Configuration
WORKFLOW_OUTPUT_DIR=.
WORKFLOW_TEMP_DIR=/tmp
WORKFLOW_LOG_LEVEL=INFO

# Database-specific configurations (optional)
PODCAST_DATABASE_ID=your-podcast-database-id
MEETING_DATABASE_ID=your-meeting-database-id
INTERVIEW_DATABASE_ID=your-interview-database-id
```

### Configuration File (config.yaml)

```yaml
# Database mappings
databases:
  meetings: "your-meeting-database-id-here"
  podcasts: "your-podcast-database-id-here"
  interviews: "your-interview-database-id-here"

# Default settings
defaults:
  database: "meetings"
  workflow: "quick_notes"
  output_dir: "." # Outputs go directly to current directory
  temp_dir: "/tmp" # Temp files go to system temp

# Workflow definitions
workflows:
  quick_notes:
    description: "Fast transcription and basic notes"
    steps: ["transcribe", "notion-upload"]

  full_analysis:
    description: "Complete transcription, deepcast breakdown, and upload"
    steps: ["transcribe", "deepcast", "notion-upload"]
    deepcast_model: "gpt-4o"
    deepcast_temperature: 0.7
```

### 📁 Output File Naming

The tool generates descriptive filenames based on your input file:

- **Transcription**: `{input-name}.transcript`
- **Deepcast Analysis**: `{input-name}-deepcast.md`
- **Logs**: `{input-name}.notion-upload.log`

All files are created directly in your current working directory (where you run the command).

## 📋 Usage Examples

### Basic Usage

```bash
# Use defaults (meetings database, quick_notes workflow)
./audio-to-notion meeting.wav

# Override title
./audio-to-notion meeting.wav --title "Team Standup"

# Use specific database
./audio-to-notion meeting.wav --database podcasts

# Use specific workflow
./audio-to-notion meeting.wav --workflow full_analysis
```

### Advanced Usage

```bash
# Full customization
./audio-to-notion meeting.wav \
  --title "Custom Title" \
  --database podcasts \
  --workflow quick_notes \
  --keep-files

# List available workflows
./audio-to-notion --list-workflows

# List available databases
./audio-to-notion --list-databases
```

### Workflow Scripts

```bash
# Quick notes (fast processing)
./workflows/quick_notes.sh meeting.wav "Team Standup"

# Full analysis (complete processing)
./workflows/full_analysis.sh meeting.wav "Team Standup" meetings

# Podcast episode (enhanced analysis)
./workflows/podcast_episode.sh podcast.wav "Episode 42: AI Revolution" 42
```

## 🔄 Workflow Types

### Quick Notes

- **Steps**: transcribe → notion-upload
- **Use case**: Fast meeting notes, quick transcriptions
- **Processing**: Minimal, fast

### Full Analysis

- **Steps**: transcribe → deepcast → notion-upload
- **Use case**: Detailed analysis, research, important content
- **Processing**: Complete with AI breakdown

### Podcast Episode

- **Steps**: transcribe → deepcast → notion-upload
- **Use case**: Podcast episodes, interviews, long-form content
- **Processing**: Enhanced with podcast-specific metadata

## 🛠️ Prerequisites

This tool requires your existing CLI tools to be installed and accessible:

- `transcribe` - Audio transcription tool
- `deepcast` - AI-powered content breakdown tool
- `notion-upload` - Notion upload tool

**Note**: The tool requires `pyyaml` for configuration support. The `python-dotenv` package is optional but recommended for `.env` file support.

## 🧪 Testing

### Test Configuration

Create a `config.test.yaml` file with your real database IDs for testing:

```bash
# Copy the template and edit with real IDs
cp config.yaml config.test.yaml
# Edit config.test.yaml with your actual database IDs

# Test the configuration
./test.sh

# Test with specific config
./audio-to-notion --config config.test.yaml --list-workflows
```

**Note**: `config.test.yaml` is ignored by git, so you can safely add real credentials.

## 🏠 Personal Configuration

### Use From Any Directory

The tool automatically discovers configuration files in multiple locations, so you can use it from anywhere:

```bash
# Setup personal configuration (one-time)
./setup-personal.sh

# Use from any directory (automatically finds personal config)
cd /some/other/directory
audio-to-notion meeting.wav
```

### Configuration Priority

The tool searches for configuration in this order:

1. **`--config` flag** (explicit file)
2. **`./audio-workflow.yaml`** (current directory)
3. **`./config.yaml`** (current directory)
4. **`~/.config/audio-workflow/config.yaml`** (config directory) ⭐ **Personal config**
5. **`~/.audio-workflow.yaml`** (home directory)
6. **`AUDIO_WORKFLOW_CONFIG`** environment variable
7. **Project `config.yaml`** (fallback)

### Personal Configuration Files

- **`~/.audio-workflow.yaml`** - Your personal config (created by `setup-personal.sh`)
- **`~/.config/audio-workflow/config.yaml`** - Alternative personal config location
- **Environment variable**: `export AUDIO_WORKFLOW_CONFIG=~/my-config.yaml`

## 🚨 Troubleshooting

### Common Issues

**Missing API Keys**

```bash
❌ Missing required environment variables: OPENAI_API_KEY, NOTION_API_KEY
```

Solution: Set the required environment variables in your `.env` file.

**Database Not Found**

```bash
❌ No database ID found for 'meetings'
```

Solution: Add the database ID to `config.yaml` or set the environment variable.

**Tool Not Found**

```bash
❌ Transcription failed: [Errno 2] No such file or directory: 'transcribe'
```

Solution: Ensure your CLI tools are installed and accessible in your PATH.

### Debug Mode

Use the `--keep-files` flag to retain intermediate files for debugging:

```bash
./audio-to-notion meeting.wav --keep-files
```

## 🤝 Contributing

This tool follows the same patterns as your other tools (`deepcast_post`, `notion_uploader`). To extend:

1. Add new workflow types to `config.yaml`
2. Create new workflow scripts in `workflows/`
3. Extend the main script with new features

## 📝 License

MIT License - see LICENSE file for details.
