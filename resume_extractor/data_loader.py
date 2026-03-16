#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@file data_loader.py
@brief Dataset loading and preprocessing for the Resume Extractor
@details Handles loading CSV files from the data directory and creating
         mappings between people, skills, education, and experience.
         Also provides skill categorization by domain.
@author Resume Extractor Team
@date 2024
@version 2.0.0
"""

import os
import re
import logging
from functools import lru_cache
from typing import List, Dict, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class DataLoader:
    """
    @class DataLoader
    @brief Handles loading and preprocessing of resume dataset
    @details Loads CSV files from data directory and creates mappings between
              people, skills, education, and experience.
    """

    def __init__(self, data_path: str = 'data/2'):
        """
        @brief Constructor for DataLoader
        @param data_path Path to the data directory containing CSV files
        """
        self.data_path = data_path
        self.people_df: Optional[pd.DataFrame] = None
        self.skills_df: Optional[pd.DataFrame] = None
        self.person_skills_df: Optional[pd.DataFrame] = None
        self.education_df: Optional[pd.DataFrame] = None
        self.experience_df: Optional[pd.DataFrame] = None
        self.abilities_df: Optional[pd.DataFrame] = None

    # ------------------------------------------------------------------
    # Data Loading
    # ------------------------------------------------------------------

    def load_all_data(self) -> bool:
        """
        @brief Load all CSV files from the data directory
        @return True if all files loaded successfully, False otherwise
        @details Attempts to load people, skills, education, experience,
                  and abilities data from CSV files.
        """
        try:
            logger.info("Loading data from %s", self.data_path)

            # Load people data
            people_path = os.path.join(self.data_path, '01_people.csv')
            if os.path.exists(people_path):
                self.people_df = pd.read_csv(people_path)
                logger.info("Loaded %d people records", len(self.people_df))

            # Load skills data
            skills_path = os.path.join(self.data_path, '06_skills.csv')
            if os.path.exists(skills_path):
                self.skills_df = pd.read_csv(skills_path)
                logger.info("Loaded %d unique skills", len(self.skills_df))

            # Load person-skills mapping
            person_skills_path = os.path.join(self.data_path, '05_person_skills.csv')
            if os.path.exists(person_skills_path):
                self.person_skills_df = pd.read_csv(person_skills_path)
                logger.info("Loaded %d person-skill mappings", len(self.person_skills_df))

            # Load education data
            education_path = os.path.join(self.data_path, '03_education.csv')
            if os.path.exists(education_path):
                self.education_df = pd.read_csv(education_path)
                logger.info("Loaded %d education records", len(self.education_df))

            # Load experience data
            experience_path = os.path.join(self.data_path, '04_experience.csv')
            if os.path.exists(experience_path):
                self.experience_df = pd.read_csv(experience_path)
                logger.info("Loaded %d experience records", len(self.experience_df))

            # Load abilities data
            abilities_path = os.path.join(self.data_path, '02_abilities.csv')
            if os.path.exists(abilities_path):
                self.abilities_df = pd.read_csv(abilities_path)
                logger.info("Loaded %d ability records", len(self.abilities_df))

            return True

        except Exception as e:
            logger.error("Error loading data: %s", str(e))
            return False

    # ------------------------------------------------------------------
    # Skills Retrieval
    # ------------------------------------------------------------------

    def get_skills_list(self) -> List[str]:
        """
        @brief Get list of all unique skills from the dataset
        @return List of skill names
        @details Extracts unique skills from the skills dataframe,
                  cleaning and normalizing skill names.

        NOTE: Results are cached via lru_cache so repeated calls are O(1)
              after the first invocation.  Call `_invalidate_skills_cache()`
              if the underlying data changes at runtime.
        """
        return self._get_skills_list_cached()

    @lru_cache(maxsize=1)
    def _get_skills_list_cached(self) -> List[str]:
        """Internal cached implementation of get_skills_list."""
        if self.skills_df is None:
            return []

        skills = self.skills_df['skill'].dropna().unique().tolist()

        # Clean skills — remove duplicates and normalize
        cleaned_skills: List[str] = []
        for skill in skills:
            if isinstance(skill, str):
                # Remove years in parentheses and clean
                cleaned = re.sub(r'\s*\(\d+\s*years?\)', '', skill, flags=re.IGNORECASE)
                cleaned = cleaned.strip()
                if cleaned and len(cleaned) > 1:
                    cleaned_skills.append(cleaned)

        return list(set(cleaned_skills))

    def _invalidate_skills_cache(self) -> None:
        """Clear the skills cache (e.g. after reloading data)."""
        self._get_skills_list_cached.cache_clear()

    # ------------------------------------------------------------------
    # Skill Categorization
    # ------------------------------------------------------------------

    # Pre-defined keyword lists used for categorization.
    _CATEGORY_KEYWORDS = {
        'programming': [
            'python', 'java', 'c++', 'javascript', 'sql', 'programming',
            'coding', 'development', 'algorithm', 'data structure',
        ],
        'database': [
            'database', 'sql', 'oracle', 'mysql', 'postgresql', 'mongodb',
            'db2', 'sqlite', 'redis', 'cassandra', 'dynamodb',
        ],
        'web_technologies': [
            'html', 'css', 'react', 'angular', 'vue', 'node', 'django', 'flask',
            'web', 'frontend', 'backend', 'api', 'rest',
        ],
        'cloud': [
            'aws', 'azure', 'gcp', 'cloud', 'docker', 'kubernetes', 'devops',
            'terraform', 'ansible', 'jenkins',
        ],
        'tools': [
            'git', 'github', 'jira', 'confluence', 'slack', 'excel', 'word',
            'powerpoint', 'tableau', 'powerbi', 'splunk',
        ],
        'soft_skills': [
            'communication', 'leadership', 'teamwork', 'problem solving',
            'analytical', 'creative', 'adaptable', 'organized',
        ],
        'management': [
            'project management', 'agile', 'scrum', 'kanban', 'planning',
            'scheduling', 'budget', 'resource', 'stakeholder',
        ],
    }

    def get_skill_categories(self) -> Dict[str, List[str]]:
        """
        @brief Categorize skills by type (technical, soft skills, etc.)
        @return Dictionary mapping category names to skill lists
        @details Groups skills into categories based on keywords and patterns.
        """
        skills = self.get_skills_list()

        categories: Dict[str, List[str]] = {key: [] for key in self._CATEGORY_KEYWORDS}
        categories['other'] = []

        for skill in skills:
            skill_lower = skill.lower()
            categorized = False

            for category, keywords in self._CATEGORY_KEYWORDS.items():
                if any(kw in skill_lower for kw in keywords):
                    categories[category].append(skill)
                    categorized = True

            if not categorized:
                categories['other'].append(skill)

        return categories
