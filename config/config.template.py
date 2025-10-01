#!/usr/bin/env python3
"""
Configuration template for Bee Cell Annotation Tool
Copy this file to config.py and modify the values as needed
"""

import os
import secrets
from pathlib import Path

class Config:
    """Base configuration class"""
    
    # Security Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Application Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Language Settings
    DEFAULT_LANGUAGE = os.environ.get('DEFAULT_LANGUAGE', 'en')
    SUPPORTED_LANGUAGES = ['en', 'zh']
    
    # Directory Configuration
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / 'data'
    STATIC_DIR = BASE_DIR / 'src' / 'static'
    UPLOAD_DIR = DATA_DIR / 'uploads'
    ANNOTATIONS_DIR = DATA_DIR / 'annotations'
    EXPORTS_DIR = DATA_DIR / 'exports'
    
    # File Settings
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff'}
    
    # Cell Classification Configuration
    CELL_CLASSES = {
        'eggs': {
            'name_key': 'cell_class.eggs.name',
            'color': '#FFE6E6',
            'border': '#FF4444',
            'description_key': 'cell_class.eggs.description'
        },
        'larvae': {
            'name_key': 'cell_class.larvae.name',
            'color': '#E6F3FF',
            'border': '#4488FF',
            'description_key': 'cell_class.larvae.description'
        },
        'capped_brood': {
            'name_key': 'cell_class.capped_brood.name',
            'color': '#FFF4E6',
            'border': '#FFB344',
            'description_key': 'cell_class.capped_brood.description'
        },
        'pollen': {
            'name_key': 'cell_class.pollen.name',
            'color': '#F0E6FF',
            'border': '#AA44FF',
            'description_key': 'cell_class.pollen.description'
        },
        'nectar': {
            'name_key': 'cell_class.nectar.name',
            'color': '#E6FFE6',
            'border': '#44FF44',
            'description_key': 'cell_class.nectar.description'
        },
        'honey': {
            'name_key': 'cell_class.honey.name',
            'color': '#FFFFE6',
            'border': '#FFFF44',
            'description_key': 'cell_class.honey.description'
        },
        'other': {
            'name_key': 'cell_class.other.name',
            'color': '#F0F0F0',
            'border': '#888888',
            'description_key': 'cell_class.other.description'
        },
        'honeycomb': {
            'name_key': 'cell_class.honeycomb.name',
            'color': '#F4E4BC',
            'border': '#8B4513',
            'description_key': 'cell_class.honeycomb.description'
        }
    }
    
    @classmethod
    def init_directories(cls):
        """Initialize all necessary directories"""
        directories = [
            cls.DATA_DIR,
            cls.STATIC_DIR,
            cls.UPLOAD_DIR,
            cls.ANNOTATIONS_DIR,
            cls.EXPORTS_DIR,
            cls.STATIC_DIR / 'css',
            cls.STATIC_DIR / 'js'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
