#!/usr/bin/env python3
"""
Flask Application Initialization
"""

from flask import Flask
import os
import sys
import mimetypes

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Development environment uses current directory
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def create_app():
    """Create Flask application instance"""
    # Get template and static file paths relative to src directory
    src_dir = os.path.dirname(os.path.abspath(__file__))
    template_folder = os.path.join(os.path.dirname(src_dir), 'templates')
    static_folder = os.path.join(os.path.dirname(src_dir), 'static')

    app = Flask(__name__,
                template_folder=template_folder,
                static_folder=static_folder)

    # Load configuration
    # Add project root to path for config import
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    from config import get_config
    config_class = get_config()
    app.config.from_object(config_class)

    # Enable template auto-reload in development
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True
    config_class.init_app(app)

    # Add font file MIME type support
    mimetypes.add_type('font/woff', '.woff')
    mimetypes.add_type('font/woff2', '.woff2')
    mimetypes.add_type('application/font-woff', '.woff')
    mimetypes.add_type('application/font-woff2', '.woff2')

    # Initialize internationalization
    from app.i18n import init_i18n
    init_i18n(app, default_language='en')

    # Register blueprints
    from app.routes import bp
    app.register_blueprint(bp)

    return app