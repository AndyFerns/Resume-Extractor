#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@file routes.py
@brief Flask route handlers for the Resume Extractor API
@details Defines a Flask Blueprint containing all HTTP endpoints:
         - GET  /            — Serve the main application page
         - POST /api/extract — Upload and extract a resume
         - GET  /api/skills  — List available skills from the dataset
         - GET  /api/health  — Application health check

         Also contains application-level initialization (data loading &
         model training) and the helper for validating file extensions.
@author Resume Extractor Team
@date 2024
@version 2.0.0
"""

import os
import logging
from datetime import datetime
from typing import Optional

from flask import Blueprint, render_template, request, jsonify
from werkzeug.utils import secure_filename

from resume_extractor.config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from resume_extractor.data_loader import DataLoader
from resume_extractor.skill_extractor import SkillExtractor
from resume_extractor.resume_parser import ResumeParser

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Blueprint Definition
# ---------------------------------------------------------------------------
# All routes are registered on this Blueprint; the main app.py registers it
# with the Flask application instance.
api_bp = Blueprint('api', __name__)

# ---------------------------------------------------------------------------
# Global Service Instances
# ---------------------------------------------------------------------------
data_loader = DataLoader()
skill_extractor = SkillExtractor()
resume_parser: Optional[ResumeParser] = None


# ---------------------------------------------------------------------------
# Application Initialization
# ---------------------------------------------------------------------------

def initialize_app() -> bool:
    """
    @brief Initialize the application by loading data and training model
    @return True if the application initialized (at least partially), False on
            complete failure.
    @details Loads all CSV data and trains the skill extraction model.
             Falls back gracefully to pattern matching if training fails.
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def allowed_file(filename: str) -> bool:
    """
    @brief Check if file extension is allowed
    @param filename Name of the file
    @return True if extension is allowed, False otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------------------------------------------------------
# Route Handlers
# ---------------------------------------------------------------------------

@api_bp.route('/')
def index():
    """
    @brief Main page route
    @return Rendered HTML template
    @details Serves the main application page with upload interface.
    """
    return render_template('index.html')


@api_bp.route('/api/extract', methods=['POST'])
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
        file_path = os.path.join(UPLOAD_FOLDER, filename)
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
            'raw_text_preview': extracted_info.raw_text,
        })

    except Exception as e:
        logger.error("Error processing file: %s", str(e))
        return jsonify({'error': str(e)}), 500


@api_bp.route('/api/skills', methods=['GET'])
def get_skills():
    """
    @brief API endpoint to get available skills
    @return JSON list of skills
    @details Returns the list of skills available in the dataset.
    """
    skills = data_loader.get_skills_list()
    return jsonify({
        'count': len(skills),
        'skills': skills[:100],  # Return first 100 for performance
    })


@api_bp.route('/api/health', methods=['GET'])
def health_check():
    """
    @brief Health check endpoint
    @return JSON status
    @details Returns application health status and initialization state.
    """
    return jsonify({
        'status': 'healthy',
        'initialized': resume_parser is not None,
        'data_loaded': data_loader.skills_df is not None,
    })
