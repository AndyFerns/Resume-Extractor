# Resume Extractor

A machine-learning-powered web application that extracts **skills**, **education**, **experience**, and **contact information** from resume files (PDF / TXT). Built with Flask, scikit-learn, and NLTK.

---

## Overview

Resume Extractor is a Python-based web application designed to automate the extraction of structured information from unstructured resume documents. It leverages machine learning (TF-IDF + Naive Bayes) and natural language processing to identify and categorize resume content.

---

## Quick Navigation

- **[Architecture](architecture.md)** — System design and component overview
- **[API Reference](api.md)** — REST API documentation
- **[User Guide](user-guide.md)** — How to use the application
- **[Tech Stack](tech-stack.md)** — Detailed tools and software documentation
- **[Development](development.md)** — Setup, configuration, and contribution guidelines

---

## Key Features

| Feature | Description |
|---------|-------------|
| **ML-based skill extraction** | TF-IDF + Naive Bayes trained on 226k+ skills from a Kaggle dataset |
| **Pattern-matching fallback** | Works even without training data |
| **PDF & text parsing** | PyPDF2 for PDFs, plain-text fallback |
| **Contact detection** | Regex-based email, phone, and LinkedIn extraction |
| **REST API** | JSON endpoints for programmatic access |
| **Responsive web UI** | Drag-and-drop upload with live results |

---

## Quick Start

```bash
# Clone & enter the project
git clone <repo-url>
cd Resume-Extractor

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The server starts at **http://localhost:5005**. Open it in your browser to use the upload UI.

---

## Project Structure

```
Resume-Extractor/
├── app.py                        # Entry point (Flask app factory)
├── requirements.txt              # Python dependencies
├── README.md                     # Project readme
├── docs/                         # Documentation suite
│
├── resume_extractor/             # Core package (all business logic)
│   ├── __init__.py               # Package exports
│   ├── config.py                 # Constants, logging, NLTK setup
│   ├── models.py                 # ExtractedInfo dataclass
│   ├── data_loader.py            # CSV dataset loading & skill categorization
│   ├── skill_extractor.py        # ML pipeline for skill extraction
│   ├── resume_parser.py          # File parsing & section extraction
│   └── routes.py                 # Flask Blueprint with all API routes
│
├── data/2/                       # Training dataset (CSV files)
│   ├── 01_people.csv
│   ├── 02_abilities.csv
│   ├── 03_education.csv
│   ├── 04_experience.csv
│   ├── 05_person_skills.csv
│   └── 06_skills.csv
│
├── templates/
│   └── index.html                # Main web UI
│
├── static/
│   ├── css/style.css             # Stylesheet
│   └── js/app.js                 # Client-side JavaScript
│
├── samples/                      # Sample resumes for testing
│   ├── Stockholm-Resume-Template-Simple.pdf
│   └── test_resume.txt
│
└── uploads/                      # Temporary upload directory (auto-created)
```

---

## License

This project is for educational / academic use.
