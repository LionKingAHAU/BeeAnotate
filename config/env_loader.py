#!/usr/bin/env python3
"""
Environment variable loader
Loads environment variables from .env files
"""

import os
from pathlib import Path

def load_dotenv(dotenv_path=None):
    """Load environment variables from .env file"""
    if dotenv_path is None:
        # Look for .env file in current directory and parent directories
        current_dir = Path.cwd()
        for parent in [current_dir] + list(current_dir.parents):
            env_file = parent / '.env'
            if env_file.exists():
                dotenv_path = env_file
                break
    
    if dotenv_path and Path(dotenv_path).exists():
        print(f"Loading environment from: {dotenv_path}")
        
        with open(dotenv_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse key=value pairs
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    # Only set if not already in environment
                    if key not in os.environ:
                        os.environ[key] = value
        
        return True
    
    return False

def load_environment():
    """Load appropriate environment configuration"""
    # Try to load from .env file first
    if not load_dotenv():
        # If no .env file, try environment-specific files
        env = os.environ.get('FLASK_ENV', 'development')
        env_file = f'.env.{env}'
        
        if not load_dotenv(env_file):
            print(f"No environment file found. Using system environment variables.")
    
    # Validate required environment variables
    required_vars = ['SECRET_KEY']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"Warning: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file or set these variables in your environment.")
