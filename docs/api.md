# API Reference

Complete documentation of the Resume Extractor REST API.

---

## Base URL

```
http://localhost:5005
```

**Note:** Default port is `5005`. Configure in `app.py` if needed.

---

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serve the web UI |
| POST | `/api/extract` | Upload and extract resume data |
| GET | `/api/skills` | List available skills from dataset |
| GET | `/api/health` | Application health check |

---

## Endpoints

### 1. Web UI

**Endpoint:** `GET /`

Serves the main application interface (HTML).

**Response:**
- `200 OK` — Returns `index.html`
- Content-Type: `text/html`

---

### 2. Extract Resume

**Endpoint:** `POST /api/extract`

Upload a resume file and receive extracted information.

**Request:**

```http
POST /api/extract HTTP/1.1
Content-Type: multipart/form-data

file: <binary file data>
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File | Yes | Resume file (PDF, TXT, DOC, DOCX) |

**Supported Formats:**
- `.pdf` — Portable Document Format
- `.txt` — Plain text
- `.doc` — Microsoft Word (legacy)
- `.docx` — Microsoft Word (modern)

**Success Response (200 OK):**

```json
{
  "success": true,
  "skills": ["Python", "Machine Learning", "SQL", "Flask"],
  "education": [
    {
      "degree": "Bachelor of Science in Computer Science",
      "institution": "Stanford University",
      "date": "2018-2022"
    }
  ],
  "experience": [
    {
      "title": "Software Engineer",
      "company": "Tech Corp",
      "date": "2022-Present"
    }
  ],
  "contact_info": {
    "email": "john.doe@example.com",
    "phone": "+1-555-123-4567",
    "linkedin": "linkedin.com/in/johndoe"
  },
  "confidence_score": 0.85,
  "raw_text_preview": "John Doe\nSoftware Engineer..."
}
```

**Error Responses:**

| Status | Error | Description |
|--------|-------|-------------|
| 400 | `{"error": "No file provided"}` | Missing file in request |
| 400 | `{"error": "No file selected"}` | Empty filename |
| 400 | `{"error": "File type not allowed"}` | Invalid file extension |
| 500 | `{"error": "Parser not initialized"}` | Server startup incomplete |
| 500 | `{"error": "<exception message>"}` | Internal processing error |

**Example (cURL):**

```bash
curl -X POST http://localhost:5000/api/extract \
  -F "file=@samples/Stockholm-Resume-Template-Simple.pdf"
```

**Example (Python requests):**

```python
import requests

with open('resume.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/api/extract',
        files={'file': f}
    )
    data = response.json()
    print(data['skills'])
```

---

### 3. List Skills

**Endpoint:** `GET /api/skills`

Returns available skills from the training dataset.

**Response (200 OK):**

```json
{
  "count": 227483,
  "skills": [
    "Python",
    "Java",
    "Machine Learning",
    "..."
  ]
}
```

**Notes:**
- Returns first 100 skills for performance
- `count` field shows total available skills
- Skills are extracted from `06_skills.csv`

**Example (cURL):**

```bash
curl http://localhost:5000/api/skills
```

---

### 4. Health Check

**Endpoint:** `GET /api/health`

Check application status and initialization state.

**Response (200 OK):**

```json
{
  "status": "healthy",
  "initialized": true,
  "data_loaded": true
}
```

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Always `"healthy"` if responding |
| `initialized` | boolean | Whether `ResumeParser` is ready |
| `data_loaded` | boolean | Whether CSV data was loaded successfully |

**States:**

| `initialized` | `data_loaded` | Meaning |
|---------------|---------------|---------|
| true | true | Fully operational |
| true | false | Running with pattern matching fallback |
| false | false | Startup incomplete or failed |

**Example (cURL):**

```bash
curl http://localhost:5000/api/health
```

---

## Response Schema Details

### ExtractedInfo Object

The core data structure returned by `/api/extract`:

```json
{
  "skills": [string],           // List of extracted skill names
  "education": [{                // Education entries
    "degree": string,            // Degree/certification name
    "institution": string,       // School/organization
    "date": string               // Time period (optional)
  }],
  "experience": [{               // Work experience entries
    "title": string,             // Job title
    "company": string,           // Employer name
    "date": string               // Time period (optional)
  }],
  "contact_info": {              // Contact details
    "email": string,             // Email address
    "phone": string,             // Phone number
    "linkedin": string           // LinkedIn profile URL
  },
  "confidence_score": number,     // 0.0 - 1.0 extraction confidence
  "raw_text_preview": string     // First 1000 chars of extracted text
}
```

### Confidence Score Interpretation

| Range | Quality | Description |
|-------|---------|-------------|
| 0.80 - 1.00 | Excellent | Strong extraction with multiple data points |
| 0.60 - 0.79 | Good | Decent extraction, some sections may be incomplete |
| 0.40 - 0.59 | Fair | Limited extraction, sparse data |
| 0.00 - 0.39 | Poor | Minimal extraction, mostly fallback values |

---

## Error Handling

All errors return JSON with an `error` field:

```json
{
  "error": "Descriptive error message"
}
```

**Common Error Causes:**

| Error | Likely Cause | Solution |
|-------|--------------|----------|
| "No file provided" | Missing `file` field in multipart request | Include file in form-data |
| "File type not allowed" | Extension not in `ALLOWED_EXTENSIONS` | Use PDF, TXT, DOC, or DOCX |
| "Parser not initialized" | Data loading failed on startup | Check data files exist |
| PDF reading errors | Corrupted or scanned PDF | Use text-based PDFs |

---

## Rate Limits & Constraints

| Constraint | Value |
|------------|-------|
| Max file size | 16 MB |
| Supported formats | PDF, TXT, DOC, DOCX |
| Skills returned | Up to 50 per resume |
| Education entries | Up to 5 per resume |
| Experience entries | Up to 5 per resume |

---

## Integration Examples

### JavaScript/Fetch

```javascript
async function extractResume(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('/api/extract', {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  return await response.json();
}

// Usage
const fileInput = document.getElementById('resume');
extractResume(fileInput.files[0])
  .then(data => console.log(data.skills));
```

### Python

```python
import requests

def extract_resume(file_path):
    with open(file_path, 'rb') as f:
        response = requests.post(
            'http://localhost:5000/api/extract',
            files={'file': f}
        )
    response.raise_for_status()
    return response.json()

# Usage
data = extract_resume('resume.pdf')
print(f"Found {len(data['skills'])} skills")
print(f"Confidence: {data['confidence_score']:.0%}")
```

### PowerShell

```powershell
$filePath = "C:\resumes\sample.pdf"
$form = @{ file = Get-Item $filePath }
Invoke-RestMethod -Uri "http://localhost:5000/api/extract" -Method Post -Form $form
```
