#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@file models.py
@brief Data models for the Resume Extractor application
@details Contains pure data-structure definitions (dataclasses) used across
         the application to represent extracted resume information.
         This module has no external dependencies beyond the standard library
         so it can be imported safely by any other module.
@author Resume Extractor Team
@date 2024
@version 2.0.0
"""

from typing import List, Dict
from dataclasses import dataclass


@dataclass
class ExtractedInfo:
    """
    @class ExtractedInfo
    @brief Data class to store extracted resume information
    @details Stores skills, education, experience, and contact information
              extracted from a resume file.

    Attributes:
        skills:           List of extracted skill names.
        education:        List of dicts with keys 'degree', 'institution', 'date'.
        experience:       List of dicts with keys 'title', 'company', 'date'.
        contact_info:     Dict with keys 'email', 'phone', 'linkedin'.
        raw_text:         Preview of the raw text extracted from the resume.
        confidence_score: Overall extraction confidence (0.0 – 1.0).
    """
    skills: List[str]
    education: List[Dict]
    experience: List[Dict]
    contact_info: Dict
    raw_text: str
    confidence_score: float
