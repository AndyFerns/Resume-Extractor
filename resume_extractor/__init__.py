#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@file __init__.py
@brief Package initializer for the resume_extractor package
@details Provides convenient top-level imports so consumers can write::

             from resume_extractor import DataLoader, SkillExtractor, ...

         Importing this package also triggers ``config.py`` side-effects
         (logging setup, NLTK downloads, directory creation).
@author Resume Extractor Team
@date 2024
@version 2.0.0
"""

# Trigger configuration side-effects (logging, NLTK, directories)
from resume_extractor.config import (          # noqa: F401
    ALLOWED_EXTENSIONS,
    MAX_CONTENT_LENGTH,
    UPLOAD_FOLDER,
    DATA_PATH,
)

# Public API — re-export for convenient access
from resume_extractor.models import ExtractedInfo           # noqa: F401
from resume_extractor.data_loader import DataLoader         # noqa: F401
from resume_extractor.skill_extractor import SkillExtractor # noqa: F401
from resume_extractor.resume_parser import ResumeParser     # noqa: F401

__all__ = [
    'ALLOWED_EXTENSIONS',
    'MAX_CONTENT_LENGTH',
    'UPLOAD_FOLDER',
    'DATA_PATH',
    'ExtractedInfo',
    'DataLoader',
    'SkillExtractor',
    'ResumeParser',
]
