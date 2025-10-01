#!/usr/bin/env python3
"""
Setup script for Bee Cell Annotation Tool
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements():
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='bee-cell-annotation',
    version='2.0.0',
    description='A web-based tool for annotating bee cell types in honeycomb images',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='Bee Research Team',
    author_email='contact@example.com',
    url='https://github.com/your-username/bee-cell-annotation',
    license='MIT',
    
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    
    include_package_data=True,
    package_data={
        'app': [
            'templates/*.html',
            'static/css/*.css',
            'static/js/*.js',
            'static/images/*',
        ],
        '': [
            'locales/*/messages.json',
        ],
    },
    
    install_requires=read_requirements(),
    
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.800',
        ],
        'prod': [
            'gunicorn>=20.0',
            'gevent>=21.0',
        ],
    },
    
    python_requires='>=3.7',
    
    entry_points={
        'console_scripts': [
            'bee-annotation=main:main',
        ],
    },
    
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Framework :: Flask',
    ],
    
    keywords='bee annotation honeycomb cell classification research biology',
    
    project_urls={
        'Bug Reports': 'https://github.com/your-username/bee-cell-annotation/issues',
        'Source': 'https://github.com/your-username/bee-cell-annotation',
        'Documentation': 'https://github.com/your-username/bee-cell-annotation/wiki',
    },
)
