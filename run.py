#!/usr/bin/env python3
"""
Bee Cell Annotation Tool - Quick Start Script
A convenient script to run the application with proper environment setup.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        print(f"✅ Flask version: {flask.__version__}")
    except ImportError:
        print("❌ Error: Flask is not installed")
        print("   Please run: pip install -r requirements.txt")
        sys.exit(1)

def setup_environment():
    """Setup environment variables and directories"""
    # Ensure we're in the project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Add src to Python path
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Create necessary directories
    directories = [
        "data/uploads",
        "data/annotations", 
        "data/exports",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Environment setup complete")

def check_config():
    """Check if configuration is properly set up"""
    env_file = Path(".env")
    config_file = Path("config/config.py")
    
    if not env_file.exists():
        print("⚠️  Warning: .env file not found")
        print("   You can copy .env.example to .env and customize it")
    
    if not config_file.exists():
        print("⚠️  Warning: config/config.py not found")
        print("   You can copy config/config.template.py to config/config.py")
    
    print("✅ Configuration check complete")

def run_application():
    """Run the Flask application"""
    print("\n🚀 Starting Bee Cell Annotation Tool...")
    print("=" * 50)
    
    try:
        # Import and run the application
        from main import main
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check that all dependencies are installed: pip install -r requirements.txt")
        print("2. Verify your configuration files are set up correctly")
        print("3. Check the logs directory for error details")
        sys.exit(1)

def main():
    """Main entry point"""
    print("🐝 Bee Cell Annotation Tool - Quick Start")
    print("=" * 50)
    
    # Run checks
    check_python_version()
    check_dependencies()
    setup_environment()
    check_config()
    
    # Run the application
    run_application()

if __name__ == "__main__":
    main()
