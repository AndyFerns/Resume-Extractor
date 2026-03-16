#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@file config.py
@brief Application configuration and initialization utilities
@details Centralizes all configuration constants, logging setup, NLTK data
         downloads, and directory initialization for the Resume Extractor app.
         This module is imported early by other modules to ensure the runtime
         environment is ready before any processing begins.
@author Resume Extractor Team
@date 2024
@version 2.0.0
"""

import os
import logging

import nltk

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------
# Set up a consistent log format used throughout the application.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# NLTK Data Downloads
# ---------------------------------------------------------------------------
# Ensure all required NLTK corpora / tokenizer models are present.
# Downloads are silent so they don't clutter first-run output.
_NLTK_RESOURCES = [
    ('tokenizers/punkt',   'punkt'),
    ('tokenizers/punkt_tab', 'punkt_tab'),   # Required by newer NLTK versions
    ('corpora/stopwords',  'stopwords'),
    ('corpora/wordnet',    'wordnet'),
]

for _resource_path, _resource_name in _NLTK_RESOURCES:
    try:
        nltk.data.find(_resource_path)
    except LookupError:
        nltk.download(_resource_name, quiet=True)

# ---------------------------------------------------------------------------
# Application Constants
# ---------------------------------------------------------------------------

# File extensions accepted for resume uploads.
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}

# Maximum upload size (16 MB).
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# Default folder where uploaded files are temporarily stored.
UPLOAD_FOLDER = 'uploads'

# Default path to the CSV dataset used for skill training.
DATA_PATH = 'data/2'

# ---------------------------------------------------------------------------
# Directory Initialization
# ---------------------------------------------------------------------------
# Create required directories if they don't already exist so the application
# never fails because of a missing folder.
for _directory in (UPLOAD_FOLDER, 'static/css', 'static/js', 'templates'):
    os.makedirs(_directory, exist_ok=True)
