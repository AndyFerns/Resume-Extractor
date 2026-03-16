# Resume Extractor

A machine-learning-powered web application that extracts **skills**, **education**, **experience**, and **contact information** from resume files (PDF / TXT). Built with Flask, scikit-learn, and NLTK.

---

## Features

- **ML-based skill extraction** — TF-IDF + Naive Bayes trained on 226k+ skills from a Kaggle dataset
- **Pattern-matching fallback** — works even without training data
- **PDF & text parsing** — PyPDF2 for PDFs, plain-text fallback
- **Contact detection** — regex-based email, phone, and LinkedIn extraction
- **REST API** — JSON endpoints for programmatic access
- **Responsive web UI** — drag-and-drop upload with live results

---

## Quick Start

### 1. Clone & enter the project

```bash
git clone <repo-url>
cd Resume-Extractor
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

The server starts at **http://localhost:5000**. Open it in your browser to use the upload UI.

---

## Project Structure

```
Resume-Extractor/
├── app.py                        # Entry point (Flask app factory)
├── requirements.txt              # Python dependencies
├── README.md                     # This file
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

## API Endpoints

| Method | Endpoint        | Description                                |
|--------|-----------------|--------------------------------------------|
| GET    | `/`             | Serve the web UI                           |
| POST   | `/api/extract`  | Upload a resume and get extracted data     |
| GET    | `/api/skills`   | List available skills from the dataset     |
| GET    | `/api/health`   | Application health check                  |

### Example: Extract a resume via cURL

```bash
curl -X POST http://localhost:5000/api/extract \
  -F "file=@samples/Stockholm-Resume-Template-Simple.pdf"
```

### Example: Health check

```bash
curl http://localhost:5000/api/health
```

---

## Configuration

All constants live in `resume_extractor/config.py`:

| Constant              | Default      | Description                        |
|-----------------------|--------------|------------------------------------|
| `ALLOWED_EXTENSIONS`  | pdf, txt, doc, docx | Accepted upload file types  |
| `MAX_CONTENT_LENGTH`  | 16 MB        | Maximum upload size                |
| `UPLOAD_FOLDER`       | `uploads/`   | Temporary file storage             |
| `DATA_PATH`           | `data/2/`    | Path to training CSV files         |

---

## Customization Guide

### Adding new skills to the dataset

1. Edit `data/2/06_skills.csv` to add new skill entries
2. Restart the server — the model retrains automatically on startup

### Changing the ML model

Edit `resume_extractor/skill_extractor.py`:
- Modify the `Pipeline` in the `train()` method to swap classifiers
- Adjust `TfidfVectorizer` parameters (ngram range, max features, etc.)

### Adding new extraction categories

1. Add a new extraction method in `resume_extractor/resume_parser.py`
2. Add the field to the `ExtractedInfo` dataclass in `resume_extractor/models.py`
3. Update the route handler in `resume_extractor/routes.py` to include the new field

### Modifying the web UI

- **HTML**: `templates/index.html`
- **CSS**: `static/css/style.css`
- **JavaScript**: `static/js/app.js`

---

## Development

### Running with auto-reload (frontend changes only)

For lightweight frontend work, you can re-enable the Flask reloader in `app.py`:

```python
app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=True)
```

> **Note**: The reloader causes a double data-load (~50s each) on every restart because the training dataset is large.

### Running tests

```bash
# Quick smoke test — verify the app starts and routes are registered
.venv/Scripts/python -c "from app import create_app; app = create_app(); print([str(r) for r in app.url_map.iter_rules()])"
```

---

## Tech Stack

- **Backend**: Python 3.12, Flask 3.1
- **ML**: scikit-learn (TF-IDF + Naive Bayes)
- **NLP**: NLTK (tokenization, lemmatization, stopwords)
- **PDF parsing**: PyPDF2
- **Frontend**: Vanilla HTML/CSS/JS
- **Dataset**: Kaggle resume dataset (~55k people, ~227k skills)

---

## License

This project is for educational / academic use.
