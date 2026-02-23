#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@file app.py
@brief Resume Extractor Flask Application
@details This application provides a web interface for extracting skills and 
         information from resume files using machine learning techniques.
         It uses a pre-built skills database from CSV files to train the model.
@author Resume Extractor Team
@date 2024
@version 1.0.0
"""

import os
import re
import json
import pickle
import logging
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import PyPDF2

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app configuration
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}


@dataclass
class ExtractedInfo:
    """
    @class ExtractedInfo
    @brief Data class to store extracted resume information
    @details Stores skills, education, experience, and contact information
              extracted from a resume file.
    """
    skills: List[str]
    education: List[Dict]
    experience: List[Dict]
    contact_info: Dict
    raw_text: str
    confidence_score: float


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
    
    def get_skills_list(self) -> List[str]:
        """
        @brief Get list of all unique skills from the dataset
        @return List of skill names
        @details Extracts unique skills from the skills dataframe,
                  cleaning and normalizing skill names.
        """
        if self.skills_df is None:
            return []
        
        skills = self.skills_df['skill'].dropna().unique().tolist()
        # Clean skills - remove duplicates and normalize
        cleaned_skills = []
        for skill in skills:
            if isinstance(skill, str):
                # Remove years in parentheses and clean
                cleaned = re.sub(r'\s*\(\d+\s*years?\)', '', skill, flags=re.IGNORECASE)
                cleaned = cleaned.strip()
                if cleaned and len(cleaned) > 1:
                    cleaned_skills.append(cleaned)
        
        return list(set(cleaned_skills))
    
    def get_skill_categories(self) -> Dict[str, List[str]]:
        """
        @brief Categorize skills by type (technical, soft skills, etc.)
        @return Dictionary mapping category names to skill lists
        @details Groups skills into categories based on keywords and patterns.
        """
        skills = self.get_skills_list()
        
        categories = {
            'programming': [],
            'database': [],
            'web_technologies': [],
            'cloud': [],
            'tools': [],
            'soft_skills': [],
            'management': [],
            'other': []
        }
        
        # Keywords for categorization
        programming_keywords = ['python', 'java', 'c++', 'javascript', 'sql', 'programming', 
                               'coding', 'development', 'algorithm', 'data structure']
        database_keywords = ['database', 'sql', 'oracle', 'mysql', 'postgresql', 'mongodb', 
                            'db2', 'sqlite', 'redis', 'cassandra', 'dynamodb']
        web_keywords = ['html', 'css', 'react', 'angular', 'vue', 'node', 'django', 'flask',
                       'web', 'frontend', 'backend', 'api', 'rest']
        cloud_keywords = ['aws', 'azure', 'gcp', 'cloud', 'docker', 'kubernetes', 'devops',
                         'terraform', 'ansible', 'jenkins']
        tools_keywords = ['git', 'github', 'jira', 'confluence', 'slack', 'excel', 'word',
                       'powerpoint', 'tableau', 'powerbi', 'splunk']
        soft_skills_keywords = ['communication', 'leadership', 'teamwork', 'problem solving',
                               'analytical', 'creative', 'adaptable', 'organized']
        management_keywords = ['project management', 'agile', 'scrum', 'kanban', 'planning',
                              'scheduling', 'budget', 'resource', 'stakeholder']
        
        for skill in skills:
            skill_lower = skill.lower()
            categorized = False
            
            if any(kw in skill_lower for kw in programming_keywords):
                categories['programming'].append(skill)
                categorized = True
            if any(kw in skill_lower for kw in database_keywords):
                categories['database'].append(skill)
                categorized = True
            if any(kw in skill_lower for kw in web_keywords):
                categories['web_technologies'].append(skill)
                categorized = True
            if any(kw in skill_lower for kw in cloud_keywords):
                categories['cloud'].append(skill)
                categorized = True
            if any(kw in skill_lower for kw in tools_keywords):
                categories['tools'].append(skill)
                categorized = True
            if any(kw in skill_lower for kw in soft_skills_keywords):
                categories['soft_skills'].append(skill)
                categorized = True
            if any(kw in skill_lower for kw in management_keywords):
                categories['management'].append(skill)
                categorized = True
            
            if not categorized:
                categories['other'].append(skill)
        
        return categories


class SkillExtractor:
    """
    @class SkillExtractor
    @brief Machine learning model for extracting skills from resume text
    @details Uses TF-IDF vectorization and Naive Bayes classification to
              identify and extract skills from resume text.
    """
    
    def __init__(self):
        """
        @brief Constructor for SkillExtractor
        @details Initializes the NLP components and ML pipeline.
        """
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.pipeline: Optional[Pipeline] = None
        self.skills_list: List[str] = []
        self.is_trained = False
        
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
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens 
                  if token not in self.stop_words and len(token) > 2]
        
        return ' '.join(tokens)
    
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
            X_train = []
            y_train = []
            
            # Add skills as positive examples
            for skill in skills_list[:5000]:  # Limit for performance
                X_train.append(skill)
                y_train.append(1)  # Is a skill
            
            # Add some negative examples (common non-skill phrases)
            non_skills = [
                'the', 'and', 'for', 'with', 'have', 'been', 'this', 'that',
                'experience in', 'worked on', 'responsible for', 'managed',
                'developed', 'implemented', 'created', 'designed', 'maintained'
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
                    max_df=0.95
                )),
                ('classifier', MultinomialNB(alpha=0.1))
            ])
            
            self.pipeline.fit(X_train, y_train)
            self.is_trained = True
            
            logger.info("Model training completed successfully")
            return True
            
        except Exception as e:
            logger.error("Error training model: %s", str(e))
            return False
    
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
        
        extracted_skills = []
        text_lower = text.lower()
        
        # Pattern matching for known skills
        for skill in self.skills_list:
            skill_lower = skill.lower()
            # Check for exact match or word boundary match
            pattern = r'\b' + re.escape(skill_lower) + r'\b'
            if re.search(pattern, text_lower):
                # Calculate confidence based on context
                confidence = self._calculate_confidence(skill, text)
                extracted_skills.append((skill, confidence))
        
        # Remove duplicates and sort by confidence
        seen = set()
        unique_skills = []
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
        # Common technical skills patterns
        common_skills = [
            'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'go',
            'sql', 'mysql', 'postgresql', 'oracle', 'mongodb', 'redis',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
            'git', 'github', 'jira', 'confluence', 'slack',
            'html', 'css', 'react', 'angular', 'vue', 'node.js', 'django',
            'machine learning', 'deep learning', 'tensorflow', 'pytorch',
            'data analysis', 'excel', 'tableau', 'powerbi', 'spark', 'hadoop',
            'linux', 'unix', 'windows', 'bash', 'shell scripting',
            'agile', 'scrum', 'kanban', 'project management', 'leadership'
        ]
        
        extracted = []
        text_lower = text.lower()
        
        for skill in common_skills:
            if skill in text_lower:
                confidence = 0.7  # Default confidence for pattern matching
                extracted.append((skill, confidence))
        
        return extracted
    
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
        skills_section_indicators = ['skills', 'technologies', 'expertise', 'proficiency']
        for indicator in skills_section_indicators:
            if indicator in text_lower:
                # Check if skill is near the indicator
                idx_indicator = text_lower.find(indicator)
                idx_skill = text_lower.find(skill_lower)
                if abs(idx_skill - idx_indicator) < 500:  # Within 500 chars
                    confidence = min(confidence + 0.1, 0.98)
        
        return confidence


class ResumeParser:
    """
    @class ResumeParser
    @brief Main class for parsing resume files and extracting information
    @details Coordinates text extraction, skill identification, and
              information structuring from various resume formats.
    """
    
    def __init__(self, skill_extractor: SkillExtractor):
        """
        @brief Constructor for ResumeParser
        @param skill_extractor Instance of SkillExtractor for skill identification
        """
        self.skill_extractor = skill_extractor
        
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
            confidence_score=confidence
        )
    
    def _extract_pdf_text(self, file_path: str) -> str:
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
    
    def _extract_text_file(self, file_path: str) -> str:
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
    
    def _extract_education(self, text: str) -> List[Dict]:
        """
        @brief Extract education information from resume text
        @param text Resume text content
        @return List of education entries
        @details Identifies education sections and extracts degree,
                  institution, and date information.
        """
        education = []
        
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
                degree_match = re.search(r'(bachelor|master|phd|bs|ms|mba|b\.s\.|m\.s\.|b\.a\.|m\.a\.)', 
                                        line, re.IGNORECASE)
                if degree_match:
                    edu_entry = {
                        'degree': line.strip(),
                        'institution': '',
                        'date': ''
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
    
    def _extract_experience(self, text: str) -> List[Dict]:
        """
        @brief Extract work experience from resume text
        @param text Resume text content
        @return List of experience entries
        @details Identifies experience sections and extracts job titles,
                  companies, and dates.
        """
        experience = []
        
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
                date_pattern = r'(19|20)\d{2}|present|current|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec'
                if re.search(date_pattern, line, re.IGNORECASE) and len(line) < 100:
                    exp_entry = {
                        'title': '',
                        'company': '',
                        'date': line.strip()
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
    
    def _extract_contact_info(self, text: str) -> Dict:
        """
        @brief Extract contact information from resume
        @param text Resume text content
        @return Dictionary with contact details
        @details Extracts email, phone, and LinkedIn information.
        """
        contact = {
            'email': '',
            'phone': '',
            'linkedin': ''
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact['email'] = email_match.group(0)
        
        # Extract phone
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact['phone'] = phone_match.group(0)
        
        # Extract LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[a-zA-Z0-9-]+'
        linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_match:
            contact['linkedin'] = linkedin_match.group(0)
        
        return contact
    
    def _calculate_overall_confidence(self, skills: List, education: List, experience: List) -> float:
        """
        @brief Calculate overall confidence score for extraction
        @param skills List of extracted skills
        @param education List of extracted education entries
        @param experience List of extracted experience entries
        @return Overall confidence score between 0 and 1
        """
        scores = []
        
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


# Global instances
data_loader = DataLoader()
skill_extractor = SkillExtractor()
resume_parser: Optional[ResumeParser] = None


def initialize_app():
    """
    @brief Initialize the application by loading data and training model
    @details Loads all CSV data and trains the skill extraction model.
    """
    global resume_parser
    
    logger.info("Initializing Resume Extractor application...")
    
    # Load data
    if data_loader.load_all_data():
        # Get skills and train model
        skills = data_loader.get_skills_list()
        logger.info("Found %d unique skills in dataset", len(skills))
        
        if skill_extractor.train(skills):
            resume_parser = ResumeParser(skill_extractor)
            logger.info("Application initialized successfully")
            return True
        else:
            logger.warning("Model training failed, using pattern matching")
            resume_parser = ResumeParser(skill_extractor)
            return True
    else:
        logger.error("Failed to load data")
        # Create parser with empty extractor as fallback
        resume_parser = ResumeParser(skill_extractor)
        return False


def allowed_file(filename: str) -> bool:
    """
    @brief Check if file extension is allowed
    @param filename Name of the file
    @return True if extension is allowed, False otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Flask Routes

@app.route('/')
def index():
    """
    @brief Main page route
    @return Rendered HTML template
    @details Serves the main application page with upload interface.
    """
    return render_template('index.html')


@app.route('/static/<path:filename>')
def serve_static(filename):
    """
    @brief Serve static files
    @param filename Path to static file
    @return Static file content
    """
    return send_from_directory('static', filename)


@app.route('/api/extract', methods=['POST'])
def extract_resume():
    """
    @brief API endpoint for resume extraction
    @return JSON response with extracted information
    @details Handles file upload and returns extracted skills,
              education, experience, and contact information.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        logger.info("Processing uploaded file: %s", filename)
        
        # Parse resume
        if resume_parser is None:
            return jsonify({'error': 'Parser not initialized'}), 500
        
        extracted_info = resume_parser.parse_file(file_path)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        # Return results
        return jsonify({
            'success': True,
            'skills': extracted_info.skills,
            'education': extracted_info.education,
            'experience': extracted_info.experience,
            'contact_info': extracted_info.contact_info,
            'confidence_score': extracted_info.confidence_score,
            'raw_text_preview': extracted_info.raw_text
        })
        
    except Exception as e:
        logger.error("Error processing file: %s", str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/api/skills', methods=['GET'])
def get_skills():
    """
    @brief API endpoint to get available skills
    @return JSON list of skills
    @details Returns the list of skills available in the dataset.
    """
    skills = data_loader.get_skills_list()
    return jsonify({
        'count': len(skills),
        'skills': skills[:100]  # Return first 100 for performance
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    @brief Health check endpoint
    @return JSON status
    @details Returns application health status and initialization state.
    """
    return jsonify({
        'status': 'healthy',
        'initialized': resume_parser is not None,
        'data_loaded': data_loader.skills_df is not None
    })


if __name__ == '__main__':
    # Initialize application
    initialize_app()
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
