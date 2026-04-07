# Development Guide

Setup instructions, configuration options, and development workflows for the Resume Extractor project.

---

## Table of Contents

1. [Setup](#setup)
2. [Configuration](#configuration)
3. [Development Workflow](#development-workflow)
4. [Testing](#testing)
5. [Project Structure](#project-structure)
6. [Contributing](#contributing)

---

## Setup

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10+ | 3.12 recommended |
| pip | Latest | Usually bundled with Python |
| Git | Latest | For cloning |
| 4GB RAM | Minimum | For ML model training |
| 500MB Disk | Free space | For dependencies + data |

### Installation Steps

1. **Clone the repository:**

```bash
git clone <repository-url>
cd Resume-Extractor
```

2. **Create virtual environment:**

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Verify data files exist:**

```bash
ls data/2/
# Should show: 01_people.csv, 02_abilities.csv, etc.
```

5. **Run the application:**

```bash
python app.py
```

6. **Test the health endpoint:**

```bash
curl http://localhost:5005/api/health
```

Expected output:
```json
{"status": "healthy", "initialized": true, "data_loaded": true}
```

---

## Configuration

### Application Constants

Edit `resume_extractor/config.py` to modify behavior:

```python
# File upload settings
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
UPLOAD_FOLDER = 'uploads'

# Data location
DATA_PATH = 'data/2'
```

### Server Configuration

Edit `app.py` to change server settings:

```python
app.run(
    debug=True,      # Enable debug mode (development only)
    host='0.0.0.0',  # Bind to all interfaces
    port=5005,       # Change port number
    use_reloader=False  # Set True for auto-reload (slower startup)
)
```

### Logging Configuration

Adjust in `resume_extractor/config.py`:

```python
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for verbose output
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## Development Workflow

### Running with Auto-Reload

For frontend development (faster iteration):

```python
# In app.py, change:
app.run(debug=True, host='0.0.0.0', port=5005, use_reloader=True)
```

**Warning:** Auto-reloader causes double data loading (~50s each restart).

### Frontend Development

The frontend uses vanilla JS/CSS with no build step:

1. Edit `templates/index.html` — Structure and content
2. Edit `static/css/style.css` — Styling and themes
3. Edit `static/js/app.js` — Client-side logic
4. Refresh browser to see changes

### Adding New Skill Categories

Edit `resume_extractor/data_loader.py`:

```python
_CATEGORY_KEYWORDS = {
    'programming': ['python', 'java', ...],
    'database': ['sql', 'mysql', ...],
    # Add new category here
    'new_category': ['keyword1', 'keyword2', ...],
}
```

### Modifying the ML Model

Edit `resume_extractor/skill_extractor.py`:

```python
self.pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(
        ngram_range=(1, 3),
        max_features=10000,  # Adjust feature count
        min_df=1,
        max_df=0.95,
    )),
    ('classifier', MultinomialNB(alpha=0.1)),
    # Swap classifier here for experimentation
])
```

Alternative classifiers to try:
- `sklearn.linear_model.LogisticRegression`
- `sklearn.ensemble.RandomForestClassifier`
- `sklearn.svm.LinearSVC`

---

## Testing

### Manual Testing

**Test file upload:**

```bash
curl -X POST http://localhost:5005/api/extract \
  -F "file=@samples/Stockholm-Resume-Template-Simple.pdf"
```

**Test health endpoint:**

```bash
curl http://localhost:5005/api/health
```

**Test skills endpoint:**

```bash
curl http://localhost:5005/api/skills
```

### Smoke Test Script

```bash
#!/bin/bash
# quick_test.sh

echo "Testing health endpoint..."
curl -s http://localhost:5005/api/health | grep -q '"status": "healthy"' && echo "✓ Health OK" || echo "✗ Health failed"

echo "Testing skills endpoint..."
curl -s http://localhost:5005/api/skills | grep -q '"count":' && echo "✓ Skills OK" || echo "✗ Skills failed"

echo "Testing extract endpoint..."
curl -s -X POST http://localhost:5005/api/extract -F "file=@samples/test_resume.txt" | grep -q '"success": true' && echo "✓ Extract OK" || echo "✗ Extract failed"
```

### Python Verification

```python
# verify_setup.py
from app import create_app
from resume_extractor.routes import initialize_app

app = create_app()
print("App created successfully")

with app.test_client() as client:
    response = client.get('/api/health')
    print(f"Health check: {response.status_code}")
    print(f"Response: {response.json}")
```

---

## Project Structure

### Module Responsibilities

```
resume_extractor/
├── __init__.py          # Package initialization
├── config.py            # Constants, logging, NLTK setup
│   └── Responsibilities:
│       - Centralized configuration
│       - NLTK data downloads
│       - Directory initialization
│
├── models.py            # Data structures
│   └── Responsibilities:
│       - ExtractedInfo dataclass
│       - Type definitions
│
├── data_loader.py       # CSV data operations
│   └── Responsibilities:
│       - Load 6 CSV files
│       - Skill categorization
│       - LRU-cached skill list
│
├── skill_extractor.py   # ML pipeline
│   └── Responsibilities:
│       - TF-IDF vectorization
│       - Naive Bayes classification
│       - Pattern matching fallback
│       - Text preprocessing with NLTK
│
├── resume_parser.py     # File parsing & extraction
│   └── Responsibilities:
│       - PDF text extraction (PyPDF2)
│       - Section detection (education/experience)
│       - Contact info extraction (regex)
│       - Confidence scoring
│
└── routes.py            # HTTP API
    └── Responsibilities:
        - Flask Blueprint definition
        - Route handlers (4 endpoints)
        - Application initialization
        - File upload handling
```

### Data Flow

```
Request → routes.py → resume_parser.py → skill_extractor.py
                                               ↓
Response ← routes.py ← resume_parser.py ← data_loader.py
```

---

## Contributing

See `CONTRIBUTING.md` for detailed contribution guidelines.

### Quick Contribution Checklist

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes with clear commit messages
4. Test manually with sample files
5. Update documentation if needed
6. Submit pull request

### Code Style

- Follow PEP 8 for Python code
- Use type hints for function signatures
- Add docstrings with `@brief`, `@param`, `@return` tags
- Keep functions focused and under 50 lines when possible

### Commit Message Format

```
type: Brief description (50 chars max)

Longer explanation if needed (wrap at 72 chars).

- Bullet points for changes
- Reference issues: Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

---

## Troubleshooting Development Issues

### NLTK Data Download Fails

**Symptom:** LookupError for punkt/stopwords/wordnet

**Solution:**
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
```

### Module Import Errors

**Symptom:** `ModuleNotFoundError: No module named 'resume_extractor'`

**Solution:** Ensure virtual environment is activated and you're in project root.

### Port Already in Use

**Symptom:** `OSError: [Errno 98] Address already in use`

**Solution:**
```bash
# Find and kill process
lsof -i :5005  # macOS/Linux
netstat -ano | findstr :5005  # Windows

# Or use different port
python app.py  # edit port in app.py
```

### Memory Issues During Training

**Symptom:** Process killed or MemoryError

**Solution:** Reduce training data limit in `skill_extractor.py`:

```python
for skill in skills_list[:1000]:  # Reduce from 5000
```
