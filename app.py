#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@file app.py
@brief Resume Extractor Flask Application — Entry Point
@details Thin entry point that creates the Flask application, registers the
         API blueprint from the ``resume_extractor`` package, initializes
         the data / ML pipeline, and starts the development server.

         All business logic now lives inside the ``resume_extractor/``
         package — see the individual module docstrings for details:
           - config.py           — app configuration & constants
           - models.py           — data classes (ExtractedInfo)
           - data_loader.py      — CSV dataset loading & skill categorization
           - skill_extractor.py  — ML-based skill extraction
           - resume_parser.py    — file parsing & section extraction
           - routes.py           — Flask route handlers (Blueprint)
@author Resume Extractor Team
@date 2024
@version 2.0.0
"""

from flask import Flask

from resume_extractor.config import MAX_CONTENT_LENGTH, UPLOAD_FOLDER
from resume_extractor.routes import api_bp, initialize_app


def create_app() -> Flask:
    """
    @brief Application factory
    @return Configured Flask application instance
    @details Creates the Flask app, applies configuration, and registers
             the API blueprint.
    """
    application = Flask(
        __name__,
        static_folder='static',
        template_folder='templates',
    )

    # Apply configuration constants
    application.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # Register the API blueprint (all routes live here)
    application.register_blueprint(api_bp)

    return application


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    # Build the Flask application
    app = create_app()

    # Load data & train the ML model
    initialize_app()

    # Start the development server
    # NOTE: use_reloader=False avoids double-initialization of the heavy
    #       data-loading / model-training step on every code change.
    #       Re-enable it during lightweight frontend-only development.
    app.run(debug=True, host='0.0.0.0', port=5005, use_reloader=False)
