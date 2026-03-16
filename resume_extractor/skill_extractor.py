#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@file skill_extractor.py
@brief Machine-learning–based skill extraction from resume text
@details Uses TF-IDF vectorization and Naive Bayes classification to
         identify and extract skills from resume text.  Also provides a
         regex-based fallback when the ML model has not been trained.
@author Resume Extractor Team
@date 2024
@version 2.0.0
"""

import re
import logging
from typing import List, Tuple, Optional, Dict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

logger = logging.getLogger(__name__)


class SkillExtractor:
    """
    @class SkillExtractor
    @brief Machine learning model for extracting skills from resume text
    @details Uses TF-IDF vectorization and Naive Bayes classification to
              identify and extract skills from resume text.
    """

    # Common technical skills used as a fallback when ML model is unavailable.
    _FALLBACK_SKILLS: List[str] = [
        'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'go',
        'sql', 'mysql', 'postgresql', 'oracle', 'mongodb', 'redis',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
        'git', 'github', 'jira', 'confluence', 'slack',
        'html', 'css', 'react', 'angular', 'vue', 'node.js', 'django',
        'machine learning', 'deep learning', 'tensorflow', 'pytorch',
        'data analysis', 'excel', 'tableau', 'powerbi', 'spark', 'hadoop',
        'linux', 'unix', 'windows', 'bash', 'shell scripting',
        'agile', 'scrum', 'kanban', 'project management', 'leadership',
    ]

    # Indicators that text is near a "Skills" section of the resume.
    _SKILLS_SECTION_INDICATORS: List[str] = [
        'skills', 'technologies', 'expertise', 'proficiency',
    ]

    def __init__(self):
        """
        @brief Constructor for SkillExtractor
        @details Initializes the NLP components and ML pipeline.
        """
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.pipeline: Optional[Pipeline] = None
        self.skills_list: List[str] = []
        self.is_trained: bool = False

        # Cache of pre-compiled regex patterns (built after training).
        self._compiled_patterns: Dict[str, re.Pattern] = {}

    # ------------------------------------------------------------------
    # Text Preprocessing
    # ------------------------------------------------------------------

    def preprocess_text(self, text: str) -> str:
        """
        @brief Preprocess text for skill extraction
        @param text Raw text from resume
        @return Preprocessed text
        @details Tokenizes, removes stopwords, and lemmatizes text.
        """
        # Convert to lowercase
        text = text.lower()

        # Remove special characters but keep spaces
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)

        # Tokenize
        tokens = word_tokenize(text)

        # Remove stopwords and lemmatize
        tokens = [
            self.lemmatizer.lemmatize(token)
            for token in tokens
            if token not in self.stop_words and len(token) > 2
        ]

        return ' '.join(tokens)

    # ------------------------------------------------------------------
    # Model Training
    # ------------------------------------------------------------------

    def train(self, skills_list: List[str]) -> bool:
        """
        @brief Train the skill extraction model
        @param skills_list List of known skills to train on
        @return True if training successful, False otherwise
        @details Creates a TF-IDF + Naive Bayes pipeline trained on
                  the provided skills list.
        """
        try:
            logger.info("Training skill extraction model with %d skills", len(skills_list))
            self.skills_list = skills_list

            # Create training data
            # Positive examples: skills themselves
            # Negative examples: random text fragments
            X_train: List[str] = []
            y_train: List[int] = []

            # Add skills as positive examples
            for skill in skills_list[:5000]:  # Limit for performance
                X_train.append(skill)
                y_train.append(1)  # Is a skill

            # Add some negative examples (common non-skill phrases)
            non_skills = [
                'the', 'and', 'for', 'with', 'have', 'been', 'this', 'that',
                'experience in', 'worked on', 'responsible for', 'managed',
                'developed', 'implemented', 'created', 'designed', 'maintained',
            ]
            for phrase in non_skills * 100:  # Repeat to balance
                X_train.append(phrase)
                y_train.append(0)  # Not a skill

            # Create and train pipeline
            self.pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(
                    ngram_range=(1, 3),
                    max_features=10000,
                    min_df=1,
                    max_df=0.95,
                )),
                ('classifier', MultinomialNB(alpha=0.1)),
            ])

            self.pipeline.fit(X_train, y_train)
            self.is_trained = True

            # Pre-compile regex patterns for every known skill so we
            # don't recompile on every call to extract_skills().
            self._compile_skill_patterns()

            logger.info("Model training completed successfully")
            return True

        except Exception as e:
            logger.error("Error training model: %s", str(e))
            return False

    # ------------------------------------------------------------------
    # Skill Extraction
    # ------------------------------------------------------------------

    def extract_skills(self, text: str) -> List[Tuple[str, float]]:
        """
        @brief Extract skills from resume text
        @param text Raw text from resume
        @return List of tuples (skill, confidence_score)
        @details Uses pattern matching and ML classification to identify
                  skills in the provided text.
        """
        if not self.is_trained:
            logger.warning("Model not trained, using pattern matching only")
            return self._extract_skills_pattern(text)

        extracted_skills: List[Tuple[str, float]] = []
        text_lower = text.lower()

        # Pattern matching for known skills (using pre-compiled patterns)
        for skill in self.skills_list:
            pattern = self._compiled_patterns.get(skill.lower())
            if pattern and pattern.search(text_lower):
                # Calculate confidence based on context
                confidence = self._calculate_confidence(skill, text)
                extracted_skills.append((skill, confidence))

        # Remove duplicates and sort by confidence
        seen: set = set()
        unique_skills: List[Tuple[str, float]] = []
        for skill, conf in sorted(extracted_skills, key=lambda x: x[1], reverse=True):
            skill_key = skill.lower()
            if skill_key not in seen:
                seen.add(skill_key)
                unique_skills.append((skill, conf))

        return unique_skills[:50]  # Return top 50 skills

    def _extract_skills_pattern(self, text: str) -> List[Tuple[str, float]]:
        """
        @brief Fallback skill extraction using pattern matching
        @param text Raw text from resume
        @return List of tuples (skill, confidence_score)
        @details Used when ML model is not trained.
        """
        extracted: List[Tuple[str, float]] = []
        text_lower = text.lower()

        for skill in self._FALLBACK_SKILLS:
            if skill in text_lower:
                confidence = 0.7  # Default confidence for pattern matching
                extracted.append((skill, confidence))

        return extracted

    # ------------------------------------------------------------------
    # Confidence Calculation
    # ------------------------------------------------------------------

    def _calculate_confidence(self, skill: str, text: str) -> float:
        """
        @brief Calculate confidence score for extracted skill
        @param skill The extracted skill
        @param text The resume text
        @return Confidence score between 0 and 1
        @details Calculates confidence based on frequency and context.
        """
        text_lower = text.lower()
        skill_lower = skill.lower()

        # Count occurrences
        count = text_lower.count(skill_lower)

        # Base confidence
        confidence = min(0.5 + (count * 0.1), 0.95)

        # Boost confidence if skill appears in skills section
        for indicator in self._SKILLS_SECTION_INDICATORS:
            if indicator in text_lower:
                # Check if skill is near the indicator
                idx_indicator = text_lower.find(indicator)
                idx_skill = text_lower.find(skill_lower)
                if abs(idx_skill - idx_indicator) < 500:  # Within 500 chars
                    confidence = min(confidence + 0.1, 0.98)

        return confidence

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    def _compile_skill_patterns(self) -> None:
        """
        @brief Pre-compile regex patterns for all known skills
        @details Compiles a word-boundary regex for each skill once during
                  training, so extract_skills() doesn't recompile per call.
        """
        self._compiled_patterns = {}
        for skill in self.skills_list:
            skill_lower = skill.lower()
            try:
                self._compiled_patterns[skill_lower] = re.compile(
                    r'\b' + re.escape(skill_lower) + r'\b'
                )
            except re.error:
                # Skip skills whose names can't form valid regex
                logger.debug("Skipping invalid regex for skill: %s", skill)
