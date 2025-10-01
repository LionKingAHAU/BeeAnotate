#!/usr/bin/env python3
"""
Internationalization (i18n) support for Bee Cell Annotation Tool
Provides multi-language support for the application
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional
from flask import session, request

class I18nManager:
    """Internationalization manager"""
    
    def __init__(self, app=None, default_language='en'):
        self.app = app
        self.default_language = default_language
        self.supported_languages = ['en', 'zh']
        self.translations = {}
        self.locales_dir = None
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the i18n manager with Flask app"""
        self.app = app
        # Look for locales directory in the src folder
        src_path = Path(app.root_path).parent if 'src' in str(app.root_path) else Path(app.root_path)
        self.locales_dir = src_path / 'locales'
        
        # Load all translations
        self.load_translations()
        
        # Register template functions
        app.jinja_env.globals['_'] = self.gettext
        app.jinja_env.globals['get_current_language'] = self.get_current_language
        app.jinja_env.globals['get_supported_languages'] = lambda: self.supported_languages
        
        # Add before_request handler
        app.before_request(self.before_request)
    
    def load_translations(self):
        """Load all translation files"""
        if not self.locales_dir.exists():
            print(f"Warning: Locales directory not found: {self.locales_dir}")
            return
        
        for lang in self.supported_languages:
            lang_file = self.locales_dir / lang / 'messages.json'
            if lang_file.exists():
                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        self.translations[lang] = json.load(f)
                    print(f"Loaded translations for language: {lang}")
                except Exception as e:
                    print(f"Error loading translations for {lang}: {e}")
                    self.translations[lang] = {}
            else:
                print(f"Translation file not found: {lang_file}")
                self.translations[lang] = {}
    
    def before_request(self):
        """Set language before each request"""
        # Priority: URL parameter > session > browser preference > default
        lang = request.args.get('lang')
        
        if lang and lang in self.supported_languages:
            session['language'] = lang
        elif 'language' not in session:
            # Try to get from browser Accept-Language header
            lang = request.accept_languages.best_match(self.supported_languages)
            session['language'] = lang or self.default_language
    
    def get_current_language(self) -> str:
        """Get current language"""
        return session.get('language', self.default_language)
    
    def set_language(self, language: str):
        """Set current language"""
        if language in self.supported_languages:
            session['language'] = language
    
    def gettext(self, key: str, **kwargs) -> str:
        """Get translated text"""
        current_lang = self.get_current_language()
        
        # Try current language first
        if current_lang in self.translations:
            text = self._get_nested_value(self.translations[current_lang], key)
            if text:
                return self._format_text(text, **kwargs)
        
        # Fallback to default language
        if self.default_language in self.translations:
            text = self._get_nested_value(self.translations[self.default_language], key)
            if text:
                return self._format_text(text, **kwargs)
        
        # Return key if no translation found
        return key
    
    def _get_nested_value(self, data: Dict, key: str):
        """Get value from nested dictionary using dot notation"""
        keys = key.split('.')
        value = data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return None
    
    def _format_text(self, text: str, **kwargs) -> str:
        """Format text with parameters"""
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, ValueError):
                return text
        return text
    
    def get_language_name(self, lang_code: str) -> str:
        """Get language display name"""
        language_names = {
            'en': 'English',
            'zh': '中文'
        }
        return language_names.get(lang_code, lang_code)

# Global i18n manager instance
i18n = I18nManager()

# Convenience function for templates and views
def _(key: str, **kwargs) -> str:
    """Shorthand for gettext"""
    return i18n.gettext(key, **kwargs)

def init_i18n(app, default_language='en'):
    """Initialize i18n for the Flask app"""
    i18n.init_app(app)
    i18n.default_language = default_language

    # Register template functions
    app.jinja_env.globals['_'] = _
    app.jinja_env.globals['gettext'] = _

    return i18n
