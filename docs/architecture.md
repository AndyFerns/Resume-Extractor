# Architecture

This document describes the system architecture, component design, and data flow of the Resume Extractor application.

---

## System Overview

Resume Extractor follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Browser    │  │    cURL      │  │   Scripts    │         │
│  │    (UI)      │  │   (API)      │  │   (API)      │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└─────────┼─────────────────┼─────────────────┼─────────────────┘
          │                 │                 │
          └─────────────────┴─────────────────┘
                            │
                    HTTP/JSON API
                            │
┌─────────────────────────────▼───────────────────────────────────┐
│                     PRESENTATION LAYER                          │
│                  Flask Application (app.py)                     │
│                    Blueprint: api_bp                            │
└─────────────────────────────┬─────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                      SERVICE LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ResumeParser  │  │SkillExtractor│  │ DataLoader   │         │
│  │              │──│              │──│              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### 1. Entry Point (`app.py`)

The application uses the **Factory Pattern** for creating Flask instances:

```python
def create_app() -> Flask:
    """Application factory — creates and configures Flask app."""
    application = Flask(__name__, ...)
    application.register_blueprint(api_bp)
    return application
```

**Responsibilities:**
- Flask app creation and configuration
- Blueprint registration
- Server startup
- Model initialization on boot

---

### 2. API Layer (`resume_extractor/routes.py`)

All HTTP endpoints are defined in a Flask Blueprint:

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Serves main web UI |
| `/api/extract` | POST | Upload and process resume |
| `/api/skills` | GET | List available skills |
| `/api/health` | GET | Health check endpoint |

**Key Functions:**
- `initialize_app()` — Loads data and trains ML model on startup
- `allowed_file()` — Validates file extensions
- Route handlers process requests and return JSON responses

---

### 3. Parser Service (`resume_extractor/resume_parser.py`)

**Class:** `ResumeParser`

The central coordinator for extracting information from resume files:

```python
class ResumeParser:
    def parse_file(self, file_path: str) -> ExtractedInfo:
        # 1. Extract text from PDF/TXT
        # 2. Extract skills via SkillExtractor
        # 3. Extract education via regex heuristics
        # 4. Extract experience via regex heuristics
        # 5. Extract contact info via regex patterns
        # 6. Calculate confidence score
        return ExtractedInfo(...)
```

**Extraction Methods:**

| Method | Purpose | Technique |
|--------|---------|-----------|
| `_extract_pdf_text()` | PDF text extraction | PyPDF2 |
| `_extract_text_file()` | Plain text reading | Python I/O |
| `_extract_education()` | Education detection | Section keywords + degree patterns |
| `_extract_experience()` | Work history detection | Date patterns + section keywords |
| `_extract_contact_info()` | Contact details | Compiled regex patterns |

---

### 4. ML Service (`resume_extractor/skill_extractor.py`)

**Class:** `SkillExtractor`

Machine learning pipeline for skill identification:

**Pipeline Architecture:**

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Raw Text    │────▶│ Preprocess   │────▶│ TF-IDF       │
│              │     │ (NLTK)       │     │ Vectorizer   │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
┌──────────────┐     ┌──────────────┐     ┌───────▼───────┐
│  Extracted   │◄────│  Confidence  │◄────│  Multinomial  │
│  Skills      │     │  Scoring     │     │  Naive Bayes  │
└──────────────┘     └──────────────┘     └───────────────┘
```

**Text Preprocessing:**
- Lowercase conversion
- Special character removal
- Tokenization (NLTK `word_tokenize`)
- Stopword removal
- Lemmatization (WordNet)

**Training Data:**
- Positive examples: Known skills from dataset (up to 5,000)
- Negative examples: Common non-skill phrases (balanced)

**Fallback:** Pattern matching with predefined skill list when ML unavailable.

---

### 5. Data Layer (`resume_extractor/data_loader.py`)

**Class:** `DataLoader`

Handles CSV dataset operations:

**Data Files:**

| File | Contents | Records |
|------|----------|---------|
| `01_people.csv` | Person profiles | ~55,000 |
| `02_abilities.csv` | Ability descriptions | Variable |
| `03_education.csv` | Education history | Variable |
| `04_experience.csv` | Work experience | Variable |
| `05_person_skills.csv` | Person-skill mappings | Variable |
| `06_skills.csv` | Skill definitions | ~227,000 |

**Features:**
- Lazy loading with error handling
- LRU-cached skill list retrieval
- Skill categorization by domain

**Skill Categories:**
- `programming` — Python, Java, C++, etc.
- `database` — SQL, MongoDB, Redis, etc.
- `web_technologies` — HTML, CSS, React, Node.js, etc.
- `cloud` — AWS, Azure, Docker, Kubernetes, etc.
- `tools` — Git, Jira, Excel, Tableau, etc.
- `soft_skills` — Communication, leadership, etc.
- `management` — Agile, Scrum, project management, etc.

---

### 6. Models (`resume_extractor/models.py`)

**Dataclass:** `ExtractedInfo`

Standardized data structure for extraction results:

```python
@dataclass
class ExtractedInfo:
    skills: List[str]           # Extracted skill names
    education: List[Dict]       # [{degree, institution, date}, ...]
    experience: List[Dict]      # [{title, company, date}, ...]
    contact_info: Dict          # {email, phone, linkedin}
    raw_text: str               # Text preview
    confidence_score: float     # 0.0 - 1.0
```

---

### 7. Configuration (`resume_extractor/config.py`)

**Constants:**

| Constant | Value | Purpose |
|----------|-------|---------|
| `ALLOWED_EXTENSIONS` | `{'pdf', 'txt', 'doc', 'docx'}` | Valid upload types |
| `MAX_CONTENT_LENGTH` | 16 MB | Maximum file size |
| `UPLOAD_FOLDER` | `'uploads/'` | Temp storage path |
| `DATA_PATH` | `'data/2'` | Training data location |

**Initialization:**
- NLTK data downloads (punkt, stopwords, wordnet)
- Logging configuration
- Directory creation

---

## Data Flow

### Resume Processing Pipeline

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  File       │───▶│  Text       │───▶│  Section    │───▶│  Skill      │
│  Upload     │    │  Extraction │    │  Detection  │    │  Extraction │
└─────────────┘    └─────────────┘    └─────────────┘    └──────┬──────┘
                                                                │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌──────▼──────┐
│  JSON       │◄───│  Confidence │◄───│  Contact    │◄───│  Experience │
│  Response   │    │  Score      │    │  Info       │    │  Education  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Request Lifecycle

1. **Upload** — File validated and saved to `uploads/`
2. **Text Extraction** — PyPDF2 or plain text reader extracts content
3. **Skill Extraction** — ML model or pattern matching identifies skills
4. **Section Parsing** — Regex patterns find education/experience sections
5. **Contact Extraction** — Compiled regex finds email, phone, LinkedIn
6. **Scoring** — Confidence calculated based on extraction quality
7. **Cleanup** — Temporary file deleted
8. **Response** — JSON returned to client

---

## Frontend Architecture

### Client-Side Structure

```
templates/index.html       ──▶  Main page structure
static/css/style.css       ──▶  Styling (responsive + dark mode)
static/js/app.js           ──▶  Application logic (ResumeExtractorApp class)
```

**ResumeExtractorApp Features:**
- File upload (drag-drop + click)
- Progress indication
- Section navigation
- Dark/light theme toggle
- Processing history
- Toast notifications
- Accessibility support (ARIA, keyboard nav)

---

## Security Considerations

- **File validation:** Extension checking via `allowed_file()`
- **Path security:** `secure_filename()` from Werkzeug
- **Size limits:** `MAX_CONTENT_LENGTH` prevents DoS
- **Temp file cleanup:** Uploaded files deleted after processing
- **XSS prevention:** HTML escaping in JavaScript

---

## Performance Optimizations

| Optimization | Implementation |
|--------------|----------------|
| Model caching | Global `skill_extractor` instance |
| Skill list caching | `@lru_cache` on `_get_skills_list_cached()` |
| Regex pre-compilation | `_compile_skill_patterns()` at training time |
| Training data limit | 5,000 skills max for performance |
| Reloader disabled | `use_reloader=False` avoids double data load |
