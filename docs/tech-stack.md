# Tech Stack

Complete inventory of tools, libraries, and software incorporated in the Resume Extractor project.

---

## Core Framework

### Python 3.12+

**Purpose:** Primary programming language

**Version Requirements:**
- Minimum: Python 3.10
- Recommended: Python 3.12

**Key Language Features Used:**
- Type hints with `typing` module
- Dataclasses for data models
- f-strings for formatting
- `functools.lru_cache` for memoization
- Context managers for resource handling

---

## Web Framework

### Flask 3.1.2

**Purpose:** Web application framework and HTTP request handling

**Key Components Used:**

| Component | Usage |
|-----------|-------|
| `Flask` | Application instance creation |
| `Blueprint` | API route organization (`api_bp`) |
| `render_template` | HTML template rendering |
| `request` | File upload handling |
| `jsonify` | JSON API responses |

**Configuration:**
- Static folder: `static/`
- Template folder: `templates/`
- Max content length: 16 MB
- Port: 5005

**Documentation:** https://flask.palletsprojects.com/

---

### Werkzeug 3.1.5

**Purpose:** WSGI utility library (Flask dependency)

**Features Used:**
- `secure_filename()` — Sanitizes uploaded filenames
- Request/Response handling
- Development server

---

## Machine Learning

### scikit-learn 1.8.0

**Purpose:** Machine learning pipeline for skill extraction

**Components Used:**

| Class | Module | Purpose |
|-------|--------|---------|
| `TfidfVectorizer` | `feature_extraction.text` | Text vectorization |
| `MultinomialNB` | `naive_bayes` | Naive Bayes classifier |
| `Pipeline` | `pipeline` | Model composition |

**Model Configuration:**
```python
Pipeline([
    ('tfidf', TfidfVectorizer(
        ngram_range=(1, 3),
        max_features=10000,
        min_df=1,
        max_df=0.95,
    )),
    ('classifier', MultinomialNB(alpha=0.1)),
])
```

**Documentation:** https://scikit-learn.org/

---

### joblib 1.5.3

**Purpose:** Serialization and parallelization support (scikit-learn dependency)

---

### scipy 1.17.0

**Purpose:** Scientific computing foundation (scikit-learn dependency)

---

### threadpoolctl 3.6.0

**Purpose:** Thread pool control for BLAS libraries (scikit-learn dependency)

---

## Natural Language Processing

### NLTK 3.9.2

**Purpose:** Natural language processing and text preprocessing

**Resources Used:**

| Resource | Type | Purpose |
|----------|------|---------|
| `punkt` | Tokenizer | Sentence/word tokenization |
| `punkt_tab` | Tokenizer | Required by newer NLTK versions |
| `stopwords` | Corpus | Stopword filtering |
| `wordnet` | Lexical DB | Word lemmatization |

**APIs Used:**
```python
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
```

**Preprocessing Pipeline:**
1. Lowercase conversion
2. Regex cleaning (special chars)
3. Word tokenization
4. Stopword removal
5. Lemmatization

**Documentation:** https://www.nltk.org/

---

### regex 2026.1.15

**Purpose:** Advanced regular expression operations (NLTK dependency)

---

## Data Processing

### pandas 3.0.0

**Purpose:** CSV dataset loading and manipulation

**Usage:**
- Loading training data from CSV files
- DataFrame operations for skill categorization
- Data cleaning and normalization

**Key Methods:**
- `pd.read_csv()` — Load CSV files
- `DataFrame.dropna()` — Remove null values
- `Series.unique()` — Get unique values

**Documentation:** https://pandas.pydata.org/

---

### numpy 2.4.2

**Purpose:** Numerical computing foundation (pandas/scikit-learn dependency)

---

### python-dateutil 2.9.0.post0

**Purpose:** Date parsing utilities (pandas dependency)

---

### pytz 2025.2

**Purpose:** Timezone handling (pandas dependency)

---

### tzdata 2025.3

**Purpose:** Timezone database (pandas dependency)

---

## PDF Processing

### PyPDF2 3.0.1

**Purpose:** PDF text extraction

**Usage:**
```python
from PyPDF2 import PdfReader

pdf_reader = PdfReader(file)
for page in pdf_reader.pages:
    text += page.extract_text() + "\n"
```

**Limitations:**
- Text-based PDFs only (not scanned images)
- Layout information may be lost
- Complex formatting may affect extraction

**Documentation:** https://pypdf2.readthedocs.io/

---

## Utilities

### requests 2.32.5

**Purpose:** HTTP client library for Kaggle integration

**Used by:** kaggle, kagglehub packages

---

### tqdm 4.67.3

**Purpose:** Progress bars for CLI operations

**Used by:** kagglehub for download progress

---

### urllib3 2.6.3

**Purpose:** HTTP client with connection pooling (requests dependency)

---

### packaging 26.0

**Purpose:** Version parsing and comparison

---

### six 1.17.0

**Purpose:** Python 2/3 compatibility (legacy dependency)

---

## Kaggle Integration

### kaggle 2.0.0

**Purpose:** Kaggle API client

**Purpose in Project:** Dataset download capabilities

---

### kagglehub 1.0.0

**Purpose:** Simplified Kaggle dataset/model access

**Purpose in Project:** Alternative dataset acquisition

---

### kagglesdk 0.1.15

**Purpose:** Kaggle SDK foundation

---

## HTML/XML Processing

### beautifulsoup4 4.13.4

**Purpose:** HTML/XML parsing (dependency of other packages)

---

### soupsieve 2.6

**Purpose:** CSS selector support for BeautifulSoup

---

### html5lib 1.1

**Purpose:** HTML5 parser (BeautifulSoup backend)

---

### webencodings 0.5.1

**Purpose:** Character encoding detection

---

## Text Processing

### text-unidecode 1.3

**Purpose:** Unicode text transliteration

**Used by:** python-slugify

---

### python-slugify 8.0.4

**Purpose:** URL-friendly slug generation

**Used by:** kaggle package

---

## Configuration & Data

### PyYAML 6.0.3

**Purpose:** YAML parsing

**Used by:** kaggle configuration

---

### protobuf 6.33.5

**Purpose:** Protocol Buffers serialization

**Used by:** kagglesdk

---

## Network & I/O

### certifi 2025.1.31

**Purpose:** SSL/TLS certificate bundle

**Purpose:** Secure HTTPS connections

---

### charset-normalizer 3.4.2

**Purpose:** Character encoding detection

**Used by:** requests

---

### idna 3.11

**Purpose:** Internationalized domain name handling

**Used by:** requests

---

## Security

### itsdangerous 2.2.0

**Purpose:** Data signing and verification

**Used by:** Flask for session security

---

### MarkupSafe 3.0.3

**Purpose:** Safe string markup handling

**Used by:** Jinja2 templating

---

## Templating

### Jinja2 3.1.6

**Purpose:** HTML template engine

**Used by:** Flask for rendering `templates/index.html`

---

## Build Tools

### setuptools 75.8.0

**Purpose:** Package building and distribution

---

### blinker 1.9.0

**Purpose:** Fast Python signals/events (Flask dependency)

---

### colorama 0.4.6

**Purpose:** Cross-platform colored terminal output

---

## Frontend (No Build Step)

The project uses vanilla web technologies without a build process:

### HTML5

- Location: `templates/index.html`
- Semantic elements and ARIA attributes
- Inline theme script for dark mode

### CSS3

- Location: `static/css/style.css`
- CSS custom properties (variables) for theming
- Flexbox and Grid layouts
- Media queries for responsiveness
- Dark mode via `data-theme` attribute

### JavaScript (ES6+)

- Location: `static/js/app.js`
- ES6 class syntax (`ResumeExtractorApp`)
- Async/await for API calls
- Fetch API for HTTP requests
- localStorage for preferences

---

## External Resources

### Google Fonts

**Loaded:**
- Inter (400, 500, 600, 700) — UI text
- JetBrains Mono (400, 500) — Code/text previews

**URL:** `https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap`

---

## Dataset

### Kaggle Resume Dataset

**Source:** `data/2/` directory

**Files:**

| File | Records | Content |
|------|---------|---------|
| `01_people.csv` | ~55,000 | Person profiles |
| `02_abilities.csv` | Variable | Ability descriptions |
| `03_education.csv` | Variable | Education records |
| `04_experience.csv` | Variable | Work experience |
| `05_person_skills.csv` | Variable | Person-skill mappings |
| `06_skills.csv` | ~227,000 | Skill definitions |

**Total Skills:** 226,000+ unique skills for ML training

---

## Development Tools

### Virtual Environment

**Recommended:** `venv` (built-in)

**Location:** `.venv/`

**Activation:**
- Windows: `.venv\Scripts\activate`
- Unix: `source .venv/bin/activate`

---

### Git

**Version Control:** `.git/`

**Ignore File:** `.gitignore`
- Python artifacts (`__pycache__`, `.pyc`)
- Virtual environment
- Uploads directory
- IDE files

---

## Platform Support

### Operating Systems

| OS | Support Level | Notes |
|----|---------------|-------|
| Windows 10/11 | Full | Primary development platform |
| macOS | Full | Requires path adjustments |
| Linux | Full | Tested on Ubuntu 22.04+ |

### Shell Scripts

- `run.sh` — Unix launcher
- `run.bat` — Windows launcher

---

## Dependency Summary

**Total Packages:** ~35 direct + transitive dependencies

**Core Categories:**
1. **Web Framework** — Flask ecosystem (5 packages)
2. **Machine Learning** — scikit-learn ecosystem (4 packages)
3. **NLP** — NLTK + supporting libs (3 packages)
4. **Data Processing** — pandas ecosystem (5 packages)
5. **PDF Processing** — PyPDF2 (1 package)
6. **Utilities** — Various helpers (17+ packages)

**Installation:**
```bash
pip install -r requirements.txt
```

---

## Version Pinning

All dependencies are pinned in `requirements.txt` for reproducibility:

```text
Flask==3.1.2
nltk==3.9.2
pandas==3.0.0
PyPDF2==3.0.1
scikit-learn==1.8.0
...
```

**Update Strategy:**
1. Test updates in development environment
2. Verify ML model still trains correctly
3. Run manual extraction tests
4. Update `requirements.txt` with new pins
