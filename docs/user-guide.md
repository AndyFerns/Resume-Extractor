# User Guide

Complete guide for using the Resume Extractor web interface and API.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Web Interface](#web-interface)
3. [Using the API](#using-the-api)
4. [Understanding Results](#understanding-results)
5. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Starting the Application

1. Ensure Python 3.12+ is installed
2. Activate your virtual environment
3. Run the application:

```bash
python app.py
```

4. Open your browser to **http://localhost:5005**

### First-Time Setup

The application automatically:
- Downloads required NLTK data (punkt, stopwords, wordnet)
- Loads CSV training data (~50s on first run)
- Trains the ML model
- Creates required directories

**Note:** Initial startup may take 60-90 seconds due to data loading.

---

## Web Interface

### Overview

The web interface consists of three main sections:

1. **Upload** — Drag-and-drop file upload
2. **Results** — Extracted information display
3. **History** — Processing history log

### Navigation

Access sections via the sidebar (☰ menu) or through automatic navigation after upload.

### Uploading a Resume

#### Method 1: Drag and Drop

1. Navigate to **Upload Resume** section
2. Drag a PDF or TXT file onto the upload area
3. Wait for processing to complete
4. Results appear automatically

#### Method 2: Click to Browse

1. Click **Choose File** button
2. Select your resume file in the file picker
3. Click **Open**
4. Processing begins automatically

#### Supported File Types

| Format | Extension | Notes |
|--------|-----------|-------|
| PDF | `.pdf` | Best results with text-based PDFs |
| Text | `.txt` | Plain UTF-8 text |
| Word (Legacy) | `.doc` | Limited support |
| Word (Modern) | `.docx` | Basic support |

**Maximum file size:** 16 MB

### Viewing Results

After processing, the **Results** section displays:

#### Skills Card

- List of detected technical and soft skills
- Color-coded by category
- Count badge showing total found

#### Education Card

- Degree/certification information
- Institution names
- Dates (if detected)

#### Experience Card

- Job titles
- Company names
- Employment dates

#### Contact Information Card

- Email address
- Phone number
- LinkedIn profile

#### Confidence Badge

Color-coded extraction quality:

| Color | Score | Meaning |
|-------|-------|---------|
| 🟢 Green | 80-100% | Excellent extraction |
| 🟡 Yellow | 60-79% | Good extraction |
| 🔴 Red | <60% | Fair/Poor extraction |

#### Raw Text Preview

Expandable section showing the extracted text from your resume (first 1000 characters).

### Settings

Access via the sidebar **Settings** section:

| Setting | Default | Description |
|---------|---------|-------------|
| Auto-extract | On | Automatically process after upload |
| Show confidence | On | Display confidence scores with skills |

Settings are saved to browser localStorage.

### Dark Mode

Toggle between light and dark themes using the moon/sun icon in the header. Your preference is saved automatically.

### Processing History

View past uploads in the **History** section:

- Filename
- Processing date/time
- Success/failure status

History is cleared when you close the browser (not persisted server-side).

---

## Using the API

### Quick API Test

Verify the application is running:

```bash
curl http://localhost:5005/api/health
```

Expected response:
```json
{"status": "healthy", "initialized": true, "data_loaded": true}
```

### Extract via API

#### cURL Example

```bash
curl -X POST http://localhost:5005/api/extract \
  -F "file=@/path/to/your/resume.pdf"
```

#### Python Example

```python
import requests

url = "http://localhost:5005/api/extract"
files = {"file": open("resume.pdf", "rb")}

response = requests.post(url, files=files)
data = response.json()

print("Skills:", data["skills"])
print("Email:", data["contact_info"]["email"])
```

#### JavaScript Example

```javascript
const formData = new FormData();
formData.append("file", fileInput.files[0]);

fetch("http://localhost:5005/api/extract", {
  method: "POST",
  body: formData
})
.then(r => r.json())
.then(data => {
  console.log("Skills:", data.skills);
});
```

### Batch Processing

Process multiple files:

```python
import requests
import os

url = "http://localhost:5005/api/extract"
resumes_dir = "./resumes/"

for filename in os.listdir(resumes_dir):
    if filename.endswith(".pdf"):
        with open(os.path.join(resumes_dir, filename), "rb") as f:
            response = requests.post(url, files={"file": f})
            data = response.json()
            print(f"{filename}: {len(data['skills'])} skills found")
```

---

## Understanding Results

### Skills Extraction

**How it works:**
- ML model compares text against 227k+ known skills
- Pattern matching as fallback
- Confidence based on frequency and context

**Categories detected:**
- Programming languages (Python, Java, JavaScript, etc.)
- Databases (SQL, MongoDB, Redis, etc.)
- Web technologies (React, Angular, Node.js, etc.)
- Cloud platforms (AWS, Azure, GCP, etc.)
- Tools (Git, Docker, Jira, etc.)
- Soft skills (Communication, Leadership, etc.)

**Improving skill detection:**
- Use standard industry terminology
- List skills in a dedicated "Skills" section
- Avoid abbreviations without context

### Education Extraction

**Detected patterns:**
- Degree keywords: Bachelor, Master, PhD, BS, MS, MBA, etc.
- Institution keywords: University, College, Institute
- Date patterns near education entries

**Tips for better extraction:**
- Use standard degree naming
- Keep institution name on same or next line
- Include graduation years

### Experience Extraction

**Detected patterns:**
- Date ranges (2020-2023, Jan 2020 - Present, etc.)
- Job titles before dates
- Company names after dates

**Tips for better extraction:**
- Use consistent date formatting
- Place job title before dates
- Put company name on separate line

### Contact Extraction

**Detected formats:**

| Type | Pattern Example |
|------|-----------------|
| Email | `name@domain.com` |
| Phone | `+1-555-123-4567`, `(555) 123-4567` |
| LinkedIn | `linkedin.com/in/username` |

---

## Troubleshooting

### Common Issues

#### "Application not fully initialized"

**Cause:** Data loading incomplete or failed.

**Solution:**
1. Check that `data/2/` directory contains CSV files
2. Restart the application
3. Check console logs for errors

#### "No skills detected"

**Cause:** Resume format or content doesn't match training data.

**Solution:**
- Ensure resume uses standard skill terminology
- Try different file format (PDF vs TXT)
- Check that model trained successfully (see `/api/health`)

#### PDF extraction errors

**Cause:** Scanned/image-based PDFs cannot be parsed.

**Solution:**
- Use text-based PDFs (exported from Word/Google Docs)
- Convert scanned PDFs using OCR software first
- Try TXT format as alternative

#### File upload fails

**Cause:** File size or type restrictions.

**Solution:**
- Check file is under 16 MB
- Verify extension is `.pdf`, `.txt`, `.doc`, or `.docx`
- Try renaming file to remove special characters

### Performance Issues

#### Slow initial startup

**Expected:** First run downloads NLTK data and loads 55k+ records.

**Mitigation:** Subsequent starts use cached data (faster).

#### Large file processing timeout

**Solution:** Split very large resumes or reduce file size.

### Getting Help

1. Check application logs in console output
2. Test with sample files in `samples/` directory
3. Verify `/api/health` shows `initialized: true`
4. Review error messages in API responses

---

## Best Practices

### For Best Extraction Results

1. **Use text-based PDFs** — Avoid scanned documents
2. **Standard formatting** — Use clear section headers
3. **Consistent structure** — Similar formatting throughout
4. **English language** — Optimized for English text
5. **Common terminology** — Use industry-standard skill names

### Security Considerations

1. **Temporary files** — Uploaded files are deleted after processing
2. **No persistence** — Resume data is not stored server-side
3. **Local processing** — All extraction happens on your machine

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Tab | Navigate through interactive elements |
| Enter/Space | Activate buttons, toggle switches |
| Escape | Close sidebar |
