#!/usr/bin/env python3
"""
Configuration classes for different environments
"""

import os
import secrets
from pathlib import Path

class Config:
    """Base configuration class"""
    
    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # File upload settings
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'data/images')
    
    # Pagination settings
    DEFAULT_PER_PAGE = int(os.environ.get('DEFAULT_PER_PAGE', 20))
    MAX_PER_PAGE = int(os.environ.get('MAX_PER_PAGE', 100))
    
    # Language settings
    DEFAULT_LANGUAGE = os.environ.get('DEFAULT_LANGUAGE', 'en')
    SUPPORTED_LANGUAGES = os.environ.get('SUPPORTED_LANGUAGES', 'en,zh').split(',')
    
    # Data directories
    DATA_DIR = os.environ.get('DATA_DIR', 'data')
    IMAGES_DIR = os.environ.get('IMAGES_DIR', 'data/images')
    ANNOTATIONS_DIR = os.environ.get('ANNOTATIONS_DIR', 'data/annotations')
    EXPORTS_DIR = os.environ.get('EXPORTS_DIR', 'data/exports')
    
    # Security settings
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    
    @staticmethod
    def init_app(app):
        """Initialize application with this configuration"""
        # Ensure all required directories exist
        Config.ensure_directories()
    
    @staticmethod
    def ensure_directories():
        """Ensure all required directories exist"""
        directories = [
            Config.DATA_DIR,
            Config.IMAGES_DIR,
            Config.ANNOTATIONS_DIR,
            Config.EXPORTS_DIR
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Production-specific initialization
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug:
            # Set up file logging
            if not os.path.exists('logs'):
                os.mkdir('logs')
            
            file_handler = RotatingFileHandler(
                'logs/bee_annotation.log',
                maxBytes=10240000,
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('Bee Cell Annotation Tool startup')

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    
    # Use in-memory or temporary directories for testing
    DATA_DIR = 'test_data'
    IMAGES_DIR = 'test_data/images'
    ANNOTATIONS_DIR = 'test_data/annotations'
    EXPORTS_DIR = 'test_data/exports'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
