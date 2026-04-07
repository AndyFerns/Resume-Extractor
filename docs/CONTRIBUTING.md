# Contributing to Resume Extractor

Thank you for your interest in contributing to Resume Extractor! This document provides guidelines and instructions for external contributors.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [How to Contribute](#how-to-contribute)
4. [Development Setup](#development-setup)
5. [Submitting Changes](#submitting-changes)
6. [Coding Standards](#coding-standards)
7. [Testing Guidelines](#testing-guidelines)
8. [Documentation](#documentation)
9. [Areas for Contribution](#areas-for-contribution)

---

## Code of Conduct

This project adheres to a professional and inclusive environment:

- **Be respectful** — Treat all contributors with courtesy
- **Be constructive** — Provide helpful feedback and suggestions
- **Be patient** — Maintainers review PRs as time permits
- **Be clear** — Communicate intentions and reasoning explicitly

Harassment, discrimination, and toxic behavior will not be tolerated.

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- 4GB RAM minimum (for ML model training)
- Virtual environment tool (venv recommended)

### First-Time Setup

1. **Fork the repository** on GitHub

2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Resume-Extractor.git
   cd Resume-Extractor
   ```

3. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/Resume-Extractor.git
   ```

4. **Create virtual environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # macOS/Linux
   ```

5. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

6. **Verify setup:**
   ```bash
   python app.py
   # Test with: curl http://localhost:5005/api/health
   ```

---

## How to Contribute

### Contribution Workflow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Find or   │───▶│   Create    │───▶│   Make      │───▶│   Submit    │
│   Open an   │    │   Branch    │    │   Changes   │    │   Pull      │
│   Issue     │    │             │    │             │    │   Request   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Step-by-Step Process

1. **Check existing issues** — Look for `good first issue` or `help wanted` labels

2. **Create an issue** (for significant changes) — Discuss before coding

3. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

4. **Make your changes** — Follow coding standards below

5. **Test your changes** — Verify functionality manually

6. **Commit with clear messages:**
   ```bash
   git commit -m "feat: Add support for DOCX parsing

   - Implement python-docx integration
   - Add unit tests for DOCX extraction
   - Update documentation

   Fixes #123"
   ```

7. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Open a Pull Request** — Fill out the PR template

9. **Address review feedback** — Be responsive to comments

---

## Development Setup

### Project Structure

```
Resume-Extractor/
├── app.py                    # Flask entry point
├── requirements.txt          # Dependencies
├── resume_extractor/         # Core package
│   ├── __init__.py
│   ├── config.py            # Configuration
│   ├── models.py            # Data classes
│   ├── data_loader.py       # CSV operations
│   ├── skill_extractor.py   # ML pipeline
│   ├── resume_parser.py     # File parsing
│   └── routes.py            # API endpoints
├── templates/               # HTML templates
├── static/                  # CSS/JS assets
├── data/2/                  # Training datasets
└── docs/                    # Documentation
```

### Running Tests

**Basic health check:**
```bash
python -c "from app import create_app; app = create_app(); print('OK')"
```

**API endpoint test:**
```bash
curl http://localhost:5005/api/health
curl http://localhost:5005/api/skills
```

**Manual extraction test:**
```bash
curl -X POST http://localhost:5005/api/extract \
  -F "file=@samples/test_resume.txt"
```

### Debugging

Enable debug logging:
```python
# In resume_extractor/config.py
logging.basicConfig(level=logging.DEBUG, ...)
```

---

## Submitting Changes

### Pull Request Guidelines

**Before submitting:**

- [ ] Branch is up-to-date with `main`
- [ ] Code follows project style guidelines
- [ ] Changes are tested manually
- [ ] Documentation updated (if applicable)
- [ ] Commit messages are clear and descriptive

**PR Description should include:**

1. **What** — Summary of changes
2. **Why** — Motivation and context
3. **How** — Implementation approach
4. **Testing** — How you verified the changes
5. **Related Issues** — Link to relevant issues

**Example:**

```markdown
## Description
Add support for extracting certifications from resumes.

## Motivation
Users requested certification extraction in #45. Currently, only degrees are captured.

## Changes
- Add `_extract_certifications()` method to ResumeParser
- Update ExtractedInfo dataclass with certifications field
- Add certification keywords to config
- Update API response to include certifications

## Testing
- Tested with 5 sample resumes containing certifications
- Verified API response includes new field
- Checked backward compatibility (empty list when none found)

## Related
Fixes #45
```

### Review Process

1. **Automated checks** — Must pass (if CI configured)
2. **Code review** — At least one maintainer approval required
3. **Manual testing** — Maintainers may verify functionality
4. **Merge** — Squash and merge once approved

---

## Coding Standards

### Python Style Guide

**Follow PEP 8 with these specifics:**

- **Line length:** 100 characters max
- **Indentation:** 4 spaces
- **Quotes:** Single quotes for strings, except docstrings
- **Imports:** Group by stdlib, third-party, local; alphabetize within groups

**Example:**
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@file example.py
@brief Brief description
@details Detailed description
@author Your Name
@date 2024
@version 1.0.0
"""

import os
import re
from typing import List, Dict

import pandas as pd
from flask import jsonify

from resume_extractor.config import logger


def process_data(data: List[str]) -> Dict[str, int]:
    """
    @brief Process input data
    @param data List of strings to process
    @return Dictionary with counts
    """
    result = {}
    for item in data:
        result[item] = len(item)
    return result
```

### Type Hints

**Required for:**
- Function parameters
- Return types
- Class attributes

**Example:**
```python
def extract_skills(text: str, threshold: float = 0.5) -> List[Tuple[str, float]]:
    ...
```

### Docstrings

**Use this format:**
```python
"""
@file filename.py
@brief One-line description
@details Detailed explanation (optional)
@param param_name Parameter description
@return Description of return value
@author Your Name
@date YYYY
@version X.Y.Z
"""
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Classes | PascalCase | `SkillExtractor` |
| Functions | snake_case | `extract_skills()` |
| Variables | snake_case | `skills_list` |
| Constants | UPPER_SNAKE_CASE | `MAX_CONTENT_LENGTH` |
| Private | _leading_underscore | `_internal_method()` |
| Modules | snake_case | `skill_extractor.py` |

---

## Testing Guidelines

### Manual Testing Checklist

**For parser changes:**
- [ ] Test with PDF files
- [ ] Test with TXT files
- [ ] Test with DOC/DOCX (if applicable)
- [ ] Test with edge cases (empty files, large files)
- [ ] Verify confidence scores are reasonable

**For API changes:**
- [ ] Test endpoint with valid input
- [ ] Test endpoint with invalid input
- [ ] Verify response format matches documentation
- [ ] Check error handling

**For ML changes:**
- [ ] Verify model trains successfully
- [ ] Test extraction accuracy on sample files
- [ ] Check training time is acceptable
- [ ] Verify fallback works when model unavailable

### Adding New Tests

**Test file structure:**
```python
# tests/test_parser.py
def test_pdf_extraction():
    parser = ResumeParser(mock_extractor)
    result = parser.parse_file('samples/test.pdf')
    assert result.skills is not None
    assert result.confidence_score > 0
```

---

## Documentation

### Updating Documentation

**When to update:**
- New features added
- API changes made
- Configuration options modified
- Architecture changes

**Files to update:**
- `README.md` — High-level overview
- `docs/*.md` — Detailed documentation
- Docstrings — Code-level documentation

### Documentation Style

- Use clear, concise language
- Include code examples
- Use tables for structured data
- Add diagrams where helpful (ASCII art acceptable)

---

## Areas for Contribution

### Good First Issues

| Area | Description | Skills Needed |
|------|-------------|---------------|
| Documentation | Fix typos, clarify instructions | Writing |
| UI Improvements | CSS enhancements, accessibility | HTML/CSS |
| Error Messages | Better user-facing error text | UX Writing |
| Sample Resumes | Add test files for edge cases | Testing |

### Feature Opportunities

| Feature | Complexity | Impact |
|---------|------------|--------|
| DOCX support | Medium | High |
| Additional languages | High | High |
| Batch processing API | Medium | Medium |
| Export to JSON/CSV | Low | Medium |
| Resume comparison | High | Medium |
| Confidence thresholds | Low | Low |

### Performance Improvements

- Model training optimization
- PDF text extraction speed
- Memory usage reduction
- Caching strategies

---

## Questions?

**Before asking:**
- Check existing documentation
- Search closed issues
- Review previous discussions

**How to reach out:**
- Open a GitHub Discussion for questions
- Comment on relevant issues
- Tag maintainers with `@username` if urgent

---

## Recognition

Contributors will be acknowledged in:
- Release notes for significant contributions
- CONTRIBUTORS.md file (if created)
- Commit history (always preserved)

Thank you for helping improve Resume Extractor!
