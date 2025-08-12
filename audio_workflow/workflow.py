"""
Core workflow orchestration logic for audio processing.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. .env files will not be loaded.")


class AudioWorkflowOrchestrator:
    """Orchestrates audio workflow: transcribe → deepcast → notion-upload."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize the orchestrator with configuration."""
        self.config_file = config_file
        self.config = self._load_config()
        
        # Get output and temp directories from config
        output_dir = self.config.get("defaults", {}).get("output_dir", ".")
        temp_dir = self.config.get("defaults", {}).get("temp_dir", "/tmp")
        
        # Convert to Path objects, handling relative vs absolute paths
        # Get the original working directory where the user ran the command
        original_cwd = os.getenv("AUDIO_WORKFLOW_ORIGINAL_CWD")
        if original_cwd:
            original_cwd = Path(original_cwd)
        else:
            original_cwd = Path.cwd()
            
        if output_dir == ".":
            # Use the original working directory where the user ran the command
            self.output_dir = original_cwd
        elif output_dir.startswith("/"):
            # Absolute path
            self.output_dir = Path(output_dir)
        else:
            # Relative path from the original working directory
            self.output_dir = original_cwd / output_dir
            
        if temp_dir.startswith("/"):
            # Absolute path (like /tmp)
            self.temp_dir = Path(temp_dir)
        else:
            # Relative path
            self.temp_dir = Path.cwd() / temp_dir
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file with smart discovery."""
        if self.config_file:
            # Use explicitly specified config file
            return self._load_single_config(self.config_file)
        
        # Get the original working directory from environment variable
        # This preserves the directory where the user ran the command
        original_cwd = os.getenv("AUDIO_WORKFLOW_ORIGINAL_CWD")
        if original_cwd:
            original_cwd = Path(original_cwd)
        else:
            original_cwd = Path.cwd()
        
        # Smart configuration discovery with priority order
        config_locations = [
            # 1. Explicit --config flag (handled above)
            # 2. Original working directory (where user ran the command)
            original_cwd / "audio-workflow.yaml",
            original_cwd / "config.yaml",
            # 3. User's config directory (highest priority for user configs)
            Path.home() / ".config" / "audio-workflow" / "config.yaml",
            # 4. User's home directory
            Path.home() / ".audio-workflow.yaml",
            # 5. Environment variable
            Path(os.getenv("AUDIO_WORKFLOW_CONFIG", "")) if os.getenv("AUDIO_WORKFLOW_CONFIG") else None,
            # 6. Project directory (where the script is located) - fallback
            Path(sys.argv[0]).resolve().parent / "config.yaml" if len(sys.argv) > 0 else None
        ]
        
        # Filter out None values
        config_locations = [loc for loc in config_locations if loc is not None]
        
        for config_path in config_locations:
            if config_path.exists():
                print(f"📁 Using configuration: {config_path}")
                return self._load_single_config(config_path)
        
        print("⚠️  No configuration file found, using defaults")
        print("   Create one of these files:")
        print("   - ./audio-workflow.yaml (current directory)")
        print("   - ~/.audio-workflow.yaml (home directory)")
        print("   - ~/.config/audio-workflow/config.yaml (config directory)")
        print("   - Set AUDIO_WORKFLOW_CONFIG environment variable")
        return {}
    
    def _load_single_config(self, config_path: Path) -> Dict[str, Any]:
        """Load a single configuration file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Could not load config file {config_path}: {e}")
            return {}
    
    def _get_database_id(self, database_name: str) -> str:
        """Get database ID from config or environment."""
        # Priority: CLI arg → config file → environment variable
        if database_name in self.config.get("databases", {}):
            return self.config["databases"][database_name]
        
        # Fallback to environment variable
        env_key = f"{database_name.upper()}_DATABASE_ID"
        return os.getenv(env_key) or os.getenv("NOTION_DATABASE_ID")
    
    def _get_workflow_config(self, workflow_name: str) -> Dict[str, Any]:
        """Get workflow configuration."""
        return self.config.get("workflows", {}).get(workflow_name, {})
    
    def _validate_environment(self) -> bool:
        """Validate required environment variables."""
        required_vars = ["OPENAI_API_KEY", "NOTION_API_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
            print("Please set these in your .env file or environment")
            return False
        
        return True
    
    def run_workflow(self, audio_file: str, title: Optional[str] = None, 
                    database: Optional[str] = None, workflow: Optional[str] = None,
                    keep_files: Optional[bool] = None) -> bool:
        """Run the complete audio workflow."""
        
        if not self._validate_environment():
            return False
        
        # Use config defaults if not specified
        if database is None:
            database = self.config.get("defaults", {}).get("database", "meetings")
        if workflow is None:
            workflow = self.config.get("defaults", {}).get("workflow", "quick_notes")
        if keep_files is None:
            keep_files = self.config.get("defaults", {}).get("keep_files", False)
        
        # Generate title if not provided
        if not title:
            title = Path(audio_file).stem
        
        # Get database ID
        database_id = self._get_database_id(database)
        if not database_id:
            print(f"❌ No database ID found for '{database}'")
            return False
        
        # Get workflow configuration
        workflow_config = self._get_workflow_config(workflow)
        steps = workflow_config.get("steps", ["transcribe", "deepcast", "notion-upload"])
        
        print(f"🎵 Starting Audio Workflow")
        print(f"   File: {audio_file}")
        print(f"   Title: {title}")
        print(f"   Database: {database} ({database_id})")
        print(f"   Workflow: {workflow}")
        print(f"   Steps: {' → '.join(steps)}")
        print()
        
        try:
            # Step 1: Transcribe
            if "transcribe" in steps:
                transcript_file = self._run_transcribe(audio_file)
                if not transcript_file:
                    return False
            else:
                transcript_file = audio_file  # Skip transcription
            
            # Step 2: Deepcast (if in workflow)
            if "deepcast" in steps and transcript_file != audio_file:
                deepcast_file = self._run_deepcast(transcript_file, workflow_config)
                if not deepcast_file:
                    return False
                markdown_file = deepcast_file
            else:
                markdown_file = transcript_file
            
            # Step 3: Notion Upload
            if "notion-upload" in steps:
                if not self._run_notion_upload(markdown_file, title, database_id):
                    return False
            
            # Cleanup
            if not keep_files:
                self._cleanup_files([transcript_file, deepcast_file] if 'deepcast' in steps else [transcript_file])
            
            print(f"\n✅ Workflow completed successfully!")
            print(f"   Output directory: {self.output_dir}")
            return True
            
        except Exception as e:
            print(f"\n❌ Workflow failed: {e}")
            return False
    
    def _run_transcribe(self, audio_file: str) -> Optional[str]:
        """Run the transcribe step."""
        print("🎤 Step 1: Transcribing audio...")
        
        # Generate descriptive filename: input-name.transcript
        input_stem = Path(audio_file).stem
        output_file = self.output_dir / f"{input_stem}.transcript"
        
        try:
            # transcribe uses --output-dir (directory) and --formats (output format)
            output_dir = output_file.parent
            cmd = ["transcribe", audio_file, "--output-dir", str(output_dir), "--formats", "md"]
            print(f"   Running: {' '.join(cmd)}")
            # Get the original working directory where the user ran the command
            original_cwd = os.getenv("AUDIO_WORKFLOW_ORIGINAL_CWD")
            if original_cwd:
                subprocess_cwd = original_cwd
            else:
                subprocess_cwd = str(output_dir)
            
            print(f"   Working directory: {Path.cwd()}")
            print(f"   Subprocess working directory: {subprocess_cwd}")
            print(f"   PATH: {os.getenv('PATH', 'Not set')[:100]}...")
            # Run without capturing output so user can see progress
            result = subprocess.run(cmd, check=True, cwd=subprocess_cwd)
            
            # Check if the transcript file was created (transcribe creates it with -transcript.md extension)
            transcript_file = output_dir / f"{Path(audio_file).stem}-transcript.md"
            if transcript_file.exists():
                print(f"   ✅ Transcription completed: {transcript_file.name}")
                return str(transcript_file)
            else:
                print(f"   ❌ Transcription output file not found")
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Transcription failed with exit code {e.returncode}")
            return None
        except Exception as e:
            print(f"   ❌ Transcription error: {e}")
            return None
    
    def _run_deepcast(self, transcript_file: str, workflow_config: Dict[str, Any]) -> Optional[str]:
        """Run the deepcast step."""
        print("📡 Step 2: Generating deepcast breakdown...")
        
        # Generate descriptive filename: input-name-deepcast.md
        input_stem = Path(transcript_file).stem
        output_file = self.output_dir / f"{input_stem}-deepcast.md"
        
        try:
            # Build deepcast command with workflow-specific settings
            cmd = ["deepcast", transcript_file, "--output-path", str(output_file)]
            
            # Add model and temperature if specified in workflow
            if "deepcast_model" in workflow_config:
                cmd.extend(["--model", workflow_config["deepcast_model"]])
            if "deepcast_temperature" in workflow_config:
                cmd.extend(["--temperature", str(workflow_config["deepcast_temperature"])])
            
            print(f"   Running: {' '.join(cmd)}")
            # Run without capturing output so user can see progress
            result = subprocess.run(cmd, check=True)
            
            if output_file.exists():
                print(f"   ✅ Deepcast breakdown generated: {output_file.name}")
                return str(output_file)
            else:
                print(f"   ❌ Deepcast output file not found")
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Deepcast generation failed: {e.stderr}")
            return None
        except Exception as e:
            print(f"   ❌ Deepcast error: {e}")
            return None
    
    def _run_notion_upload(self, markdown_file: str, title: str, database_id: str) -> bool:
        """Run the notion-upload step."""
        print("📤 Step 3: Uploading to Notion...")
        
        try:
            cmd = ["notion-upload", markdown_file, "--title", title, "--database-id", database_id]
            print(f"   Running: {' '.join(cmd)}")
            # Run without capturing output so user can see progress
            result = subprocess.run(cmd, check=True)
            
            print(f"   ✅ Notion upload completed for: {title}")
            return True
                
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Notion upload failed: {e.stderr}")
            return False
        except Exception as e:
            print(f"   ❌ Notion upload error: {e}")
            return False
    
    def _cleanup_files(self, files: list):
        """Clean up temporary files."""
        for file_path in files:
            if file_path and file_path != "audio_file" and Path(file_path).exists():
                try:
                    Path(file_path).unlink()
                    print(f"   🗑️  Cleaned up: {file_path}")
                except Exception as e:
                    print(f"   ⚠️  Could not clean up {file_path}: {e}")
    
    def list_workflows(self):
        """List available workflows."""
        workflows = self.config.get("workflows", {})
        if not workflows:
            print("No workflows configured")
            return
        
        print("Available workflows:")
        for name, config in workflows.items():
            description = config.get("description", "No description")
            steps = " → ".join(config.get("steps", []))
            print(f"  {name}: {description}")
            print(f"    Steps: {steps}")
            print()
    
    def list_databases(self):
        """List available databases."""
        databases = self.config.get("databases", {})
        if not databases:
            print("No databases configured")
            return
        
        print("Available databases:")
        for name, db_id in databases.items():
            print(f"  {name}: {db_id}")
        print()
    
    def show_config(self):
        """Display the loaded configuration in a readable format."""
        print("🔧 Loaded Configuration")
        print("=" * 50)
        
        # Show which config file was loaded
        if self.config_file:
            print(f"📁 Config Source: {self.config_file}")
        else:
            print("📁 Config Source: Auto-discovered")
        print()
        
        # Show defaults
        defaults = self.config.get("defaults", {})
        if defaults:
            print("⚙️  Default Settings:")
            for key, value in defaults.items():
                print(f"   {key}: {value}")
            print()
        
        # Show databases
        databases = self.config.get("databases", {})
        if databases:
            print("🗄️  Database Mappings:")
            for name, db_id in databases.items():
                # Truncate long database IDs for readability
                display_id = db_id[:20] + "..." if len(db_id) > 20 else db_id
                print(f"   {name}: {display_id}")
            print()
        
        # Show workflows
        workflows = self.config.get("workflows", {})
        if workflows:
            print("🔄 Available Workflows:")
            for name, config in workflows.items():
                description = config.get("description", "No description")
                steps = " → ".join(config.get("steps", []))
                print(f"   {name}: {description}")
                print(f"     Steps: {steps}")
                
                # Show workflow-specific settings
                if "deepcast_model" in config:
                    print(f"     Model: {config['deepcast_model']}")
                if "deepcast_temperature" in config:
                    print(f"     Temperature: {config['deepcast_temperature']}")
                print()
        
        # Show output and temp directories
        print("📁 File Locations:")
        print(f"   Output Directory: {self.output_dir}")
        print(f"   Temp Directory: {self.temp_dir}")
        print()
        
        # Show environment variables status
        print("🔑 Environment Variables:")
        required_vars = ["OPENAI_API_KEY", "NOTION_API_KEY"]
        for var in required_vars:
            status = "✅ Set" if os.getenv(var) else "❌ Missing"
            print(f"   {var}: {status}")
        

