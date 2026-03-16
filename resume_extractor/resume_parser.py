#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@file resume_parser.py
@brief Resume file parsing and information extraction
@details Coordinates text extraction from PDF / plain-text files and
         delegates skill identification to SkillExtractor.  Also handles
         extraction of education, experience, and contact information
         using regex heuristics.
@author Resume Extractor Team
@date 2024
@version 2.0.0
"""

import re
import logging
from typing import List, Dict, Tuple

import PyPDF2

from resume_extractor.models import ExtractedInfo
from resume_extractor.skill_extractor import SkillExtractor

logger = logging.getLogger(__name__)


class ResumeParser:
    """
    @class ResumeParser
    @brief Main class for parsing resume files and extracting information
    @details Coordinates text extraction, skill identification, and
              information structuring from various resume formats.
    """

    # Pre-compiled patterns for contact-info extraction.
    _EMAIL_RE = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    _PHONE_RE = re.compile(r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
    _LINKEDIN_RE = re.compile(r'linkedin\.com/in/[a-zA-Z0-9-]+', re.IGNORECASE)

    # Pre-compiled pattern for date detection inside experience sections.
    _DATE_RE = re.compile(
        r'(19|20)\d{2}|present|current|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec',
        re.IGNORECASE,
    )

    # Pre-compiled pattern for degree detection inside education sections.
    _DEGREE_RE = re.compile(
        r'(bachelor|master|phd|bs|ms|mba|b\.s\.|m\.s\.|b\.a\.|m\.a\.)',
        re.IGNORECASE,
    )

    def __init__(self, skill_extractor: SkillExtractor):
        """
        @brief Constructor for ResumeParser
        @param skill_extractor Instance of SkillExtractor for skill identification
        """
        self.skill_extractor = skill_extractor

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse_file(self, file_path: str) -> ExtractedInfo:
        """
        @brief Parse a resume file and extract information
        @param file_path Path to the resume file
        @return ExtractedInfo object containing all extracted data
        @details Handles PDF and text files, extracting skills, education,
                  experience, and contact information.
        """
        logger.info("Parsing file: %s", file_path)

        # Extract text based on file type
        if file_path.lower().endswith('.pdf'):
            raw_text = self._extract_pdf_text(file_path)
        else:
            raw_text = self._extract_text_file(file_path)

        # Extract skills
        skills = self.skill_extractor.extract_skills(raw_text)

        # Extract education
        education = self._extract_education(raw_text)

        # Extract experience
        experience = self._extract_experience(raw_text)

        # Extract contact info
        contact_info = self._extract_contact_info(raw_text)

        # Calculate overall confidence
        confidence = self._calculate_overall_confidence(skills, education, experience)

        return ExtractedInfo(
            skills=[s[0] for s in skills],
            education=education,
            experience=experience,
            contact_info=contact_info,
            raw_text=raw_text[:1000] + "..." if len(raw_text) > 1000 else raw_text,
            confidence_score=confidence,
        )

    # ------------------------------------------------------------------
    # Text Extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_pdf_text(file_path: str) -> str:
        """
        @brief Extract text from PDF file
        @param file_path Path to PDF file
        @return Extracted text content
        @details Uses PyPDF2 to extract text from all pages of the PDF.
        """
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error("Error extracting PDF text: %s", str(e))
            text = f"Error reading PDF: {str(e)}"

        return text

    @staticmethod
    def _extract_text_file(file_path: str) -> str:
        """
        @brief Extract text from plain text file
        @param file_path Path to text file
        @return File content as string
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                return file.read()
        except Exception as e:
            logger.error("Error reading text file: %s", str(e))
            return f"Error reading file: {str(e)}"

    # ------------------------------------------------------------------
    # Section Extraction — Education
    # ------------------------------------------------------------------

    def _extract_education(self, text: str) -> List[Dict]:
        """
        @brief Extract education information from resume text
        @param text Resume text content
        @return List of education entries
        @details Identifies education sections and extracts degree,
                  institution, and date information.
        """
        education: List[Dict] = []

        # Common education keywords
        edu_keywords = ['education', 'academic', 'degree', 'university', 'college',
                        'bachelor', 'master', 'phd', 'bs', 'ms', 'mba']

        # Split into lines and look for education section
        lines = text.split('\n')
        in_education_section = False

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()

            # Check if we're entering education section
            if any(keyword in line_lower for keyword in edu_keywords[:3]):
                in_education_section = True
                continue

            # If in education section, extract entries
            if in_education_section and line.strip():
                # Look for degree patterns
                degree_match = self._DEGREE_RE.search(line)
                if degree_match:
                    edu_entry: Dict = {
                        'degree': line.strip(),
                        'institution': '',
                        'date': '',
                    }

                    # Try to get next line for institution
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line and not any(k in next_line.lower() for k in edu_keywords[:3]):
                            edu_entry['institution'] = next_line

                    education.append(edu_entry)

                # Stop if we hit another section
                if any(keyword in line_lower for keyword in ['experience', 'skills', 'work']):
                    in_education_section = False

        return education[:5]  # Return top 5 education entries

    # ------------------------------------------------------------------
    # Section Extraction — Experience
    # ------------------------------------------------------------------

    def _extract_experience(self, text: str) -> List[Dict]:
        """
        @brief Extract work experience from resume text
        @param text Resume text content
        @return List of experience entries
        @details Identifies experience sections and extracts job titles,
                  companies, and dates.
        """
        experience: List[Dict] = []

        # Common experience keywords
        exp_keywords = ['experience', 'work', 'employment', 'career', 'professional']

        lines = text.split('\n')
        in_experience_section = False

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()

            # Check if entering experience section
            if any(keyword in line_lower for keyword in exp_keywords):
                in_experience_section = True
                continue

            # Extract experience entries
            if in_experience_section and line.strip():
                # Look for date patterns (indicates job entry)
                if self._DATE_RE.search(line) and len(line) < 100:
                    exp_entry: Dict = {
                        'title': '',
                        'company': '',
                        'date': line.strip(),
                    }

                    # Try to get previous line for title
                    if i > 0:
                        prev_line = lines[i - 1].strip()
                        if prev_line and len(prev_line) < 100:
                            exp_entry['title'] = prev_line

                    # Try to get next line for company
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line and len(next_line) < 100:
                            exp_entry['company'] = next_line

                    experience.append(exp_entry)

                # Stop if we hit another section
                if any(keyword in line_lower for keyword in ['education', 'skills', 'projects']):
                    in_experience_section = False

        return experience[:5]  # Return top 5 experience entries

    # ------------------------------------------------------------------
    # Section Extraction — Contact Information
    # ------------------------------------------------------------------

    def _extract_contact_info(self, text: str) -> Dict:
        """
        @brief Extract contact information from resume
        @param text Resume text content
        @return Dictionary with contact details
        @details Extracts email, phone, and LinkedIn information.
        """
        contact: Dict = {
            'email': '',
            'phone': '',
            'linkedin': '',
        }

        # Extract email
        email_match = self._EMAIL_RE.search(text)
        if email_match:
            contact['email'] = email_match.group(0)

        # Extract phone
        phone_match = self._PHONE_RE.search(text)
        if phone_match:
            contact['phone'] = phone_match.group(0)

        # Extract LinkedIn
        linkedin_match = self._LINKEDIN_RE.search(text)
        if linkedin_match:
            contact['linkedin'] = linkedin_match.group(0)

        return contact

    # ------------------------------------------------------------------
    # Confidence Scoring
    # ------------------------------------------------------------------

    @staticmethod
    def _calculate_overall_confidence(
        skills: List[Tuple[str, float]],
        education: List[Dict],
        experience: List[Dict],
    ) -> float:
        """
        @brief Calculate overall confidence score for extraction
        @param skills List of extracted skills (with confidence tuples)
        @param education List of extracted education entries
        @param experience List of extracted experience entries
        @return Overall confidence score between 0 and 1
        """
        scores: List[float] = []

        # Skills confidence
        if skills:
            avg_skill_conf = sum(s[1] for s in skills) / len(skills)
            scores.append(avg_skill_conf)

        # Education confidence (based on number of entries found)
        if education:
            scores.append(min(len(education) * 0.2, 0.8))

        # Experience confidence
        if experience:
            scores.append(min(len(experience) * 0.15, 0.8))

        return sum(scores) / len(scores) if scores else 0.5
