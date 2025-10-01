#!/usr/bin/env python3
"""
Configuration validation script
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.env_loader import load_environment
from config import get_config

def validate_config():
    """Validate current configuration"""
    print("Configuration Validation")
    print("=" * 40)
    
    # Load environment
    load_environment()
    
    # Get configuration
    config_class = get_config()
    
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"Configuration class: {config_class.__name__}")
    print()
    
    # Check required settings
    checks = [
        ("SECRET_KEY", config_class.SECRET_KEY, "Secret key for session security"),
        ("DEBUG", config_class.DEBUG, "Debug mode setting"),
        ("MAX_CONTENT_LENGTH", config_class.MAX_CONTENT_LENGTH, "Maximum file upload size"),
        ("DEFAULT_LANGUAGE", config_class.DEFAULT_LANGUAGE, "Default application language"),
        ("DATA_DIR", config_class.DATA_DIR, "Data directory path"),
        ("IMAGES_DIR", config_class.IMAGES_DIR, "Images directory path"),
        ("ANNOTATIONS_DIR", config_class.ANNOTATIONS_DIR, "Annotations directory path"),
    ]
    
    all_good = True
    
    for name, value, description in checks:
        if value:
            status = "✓"
            if name == "SECRET_KEY":
                display_value = "***" if len(str(value)) > 10 else "⚠ TOO SHORT"
            else:
                display_value = value
        else:
            status = "✗"
            display_value = "NOT SET"
            all_good = False
        
        print(f"{status} {name}: {display_value}")
        print(f"   {description}")
        print()
    
    # Check directories
    print("Directory Status:")
    print("-" * 20)
    
    directories = [
        config_class.DATA_DIR,
        config_class.IMAGES_DIR,
        config_class.ANNOTATIONS_DIR,
        config_class.EXPORTS_DIR
    ]
    
    for directory in directories:
        path = Path(directory)
        if path.exists():
            print(f"✓ {directory} (exists)")
        else:
            print(f"⚠ {directory} (will be created)")
    
    print()
    
    if all_good:
        print("✓ Configuration validation passed!")
        return True
    else:
        print("✗ Configuration validation failed!")
        print("Please check the missing settings above.")
        return False

if __name__ == '__main__':
    success = validate_config()
    sys.exit(0 if success else 1)
