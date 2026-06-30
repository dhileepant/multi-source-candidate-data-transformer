# Multi-Source Candidate Data Transformer

A production-style data transformation pipeline that ingests candidate information from multiple heterogeneous sources, performs deterministic entity resolution, normalizes and validates data, and produces a unified canonical candidate profile with complete provenance tracking and configurable output projections.

🚀 **Live Demo:** [multi-source-candidate-data-transformer-production.up.railway.app](https://multi-source-candidate-data-transformer-production.up.railway.app/)
*(The application is currently hosted on Railway and fully interactive)*

🎥 **Demo Video:** https://github.com/user-attachments/assets/e3ecc5ec-c39c-4cdd-8ddc-d03da11562f7

---

## Features

- **Multi-source ingestion**
  - Structured Sources
    - Recruiter CSV Export
    - GitHub Profile (REST API)
  - Unstructured Sources
    - Resume PDF

- **Deterministic Entity Resolution**
  - Merges candidate profiles using strong identifiers:
    - Email
    - Phone Number (E.164)
    - GitHub URL
  - Prevents false-positive merges by avoiding probabilistic matching.

- **Normalization**
  - Phone numbers → E.164
  - Dates → YYYY-MM
  - Skills → Canonical names
  - Duplicate removal

- **Conflict Resolution**
  - Selects the highest-confidence value across multiple sources.
  - Preserves complete provenance for every field.

- **Configurable Projection Layer**
  - Dynamic output schema using `config.json`
  - Field mapping
  - Field renaming
  - Optional fields
  - Runtime projections

- **Validation**
  - Schema validation via Pydantic
  - Missing source handling
  - Graceful degradation
  - Invalid input detection

- **Testing**
  - Automated Pytest suite
  - Normalization tests
  - Entity resolution tests
  - Edge-case coverage

---

# Architecture

```
                Recruiter CSV
                     │
                     │
                Resume PDF
                     │
                     │
               GitHub REST API
                     │
                     ▼
               Source Parsers
                     │
                     ▼
               Normalizers
                     │
                     ▼
        Deterministic Entity Resolution
                     │
                     ▼
            Conflict Resolution
                     │
                     ▼
            Canonical Candidate
                     │
                     ▼
             Projection Layer
                     │
                     ▼
             Schema Validator
                     │
                     ▼
               Output JSON
```

---

# Project Structure

```
multi-source-candidate-data-transformer/
│
├── src/
│   ├── __init__.py
│   ├── cli.py             # Entry point for the application
│   ├── extractors.py      # PDF, CSV, and GitHub API parsing logic
│   ├── merger.py          # Deterministic matching and conflict resolution
│   ├── normalizers.py     # Data cleaning (phones, dates, canonical skills)
│   ├── projector.py       # JSON output projection logic
│   └── schema.py          # Pydantic models for validation
│
├── tests/
│   ├── __init__.py
│   └── test_pipeline.py   # Unit tests for the pipeline
│
├── inputs/
│   ├── recruiter_export.csv
│   ├── resume_dhileepan.pdf
│   └── resume_jane.pdf
│
├── config.json            # Configuration schema
├── final_output.json      # Final merged & projected output
├── generate_mocks.py      # Utility script for generating mock CSVs
├── generate_pdf.py        # Utility script for generating mock PDFs
└── README.md
```

---

# Technology Stack

- Python 3.9+
- Pydantic
- PyPDF
- phonenumbers
- python-dateutil
- GitHub REST API
- Pytest

---

# Offline Setup & Installation

You can run this project locally using either **Docker** (recommended) or a standard Python virtual environment.

### Option 1: Docker (Recommended)
This is the easiest way to run the application without worrying about local dependencies.

1. Build the Docker image:
   ```bash
   docker build -t candidate-transformer .
   ```
2. Run the container:
   ```bash
   docker run -p 5000:5000 candidate-transformer
   ```
3. Open `http://localhost:5000` in your browser.

### Option 2: Python Virtual Environment

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the environment:
   - **Windows:** `.\venv\Scripts\Activate.ps1`
   - **Linux / macOS:** `source venv/bin/activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python app.py
   ```
5. Open `http://localhost:5000` in your browser.

---

# Running the Pipeline

### Option 1: Web Dashboard (Interactive)
The easiest way to run the pipeline is through the web dashboard, which provides a beautiful UI to upload files and visualize the entity resolution process in real-time.

```bash
python app.py
```
*(Then open http://127.0.0.1:5000 in your browser)*

### Option 2: Command Line Interface (CLI)
You can also run the pipeline directly via the CLI for batch processing.

**For the Official Eightfold Canonical Schema (Default):**
```bash
python src/cli.py \
--inputs inputs/recruiter_export.csv \
--config default_config.json \
--output final_output.json
```

**For a Custom Simplified Projection:**
```bash
python src/cli.py \
--inputs inputs/recruiter_export.csv \
--config custom_config.json \
--output custom_output.json
```

The pipeline will:

1. Parse all input sources.
2. Normalize phones, dates and skills.
3. Resolve duplicate candidate profiles using deterministic identifiers.
4. Merge records into canonical profiles.
5. Validate the output schema via Pydantic.
6. Produce JSON according to the requested projection.

---

# Running Tests

```bash
pytest tests/
```

The test suite validates:

- Phone normalization
- Skill canonicalization
- Date normalization
- Entity resolution
- Conflict resolution
- Missing input handling
- Duplicate detection

---

# Example Output

```json
{
  "candidate_id": "dhileepantv@gmail.com",
  "full_name": "DHILEEPAN T",
  "primary_email": "dhileepantv@gmail.com",
  "phone": "+919597349871",
  "skills": [
    "C",
    "TypeScript",
    "Git",
    "Spring Boot",
    "C++",
    "React.js",
    "GitHub",
    "Bootstrap",
    "Python",
    "Next.js",
    "JavaScript",
    "MongoDB"
  ],
  "headline": "Aspiring full-stack developer focused on MERN Stack, problem solving (DSA) , and real-world projects. Exploring AI, web development, and coding challenges.",
  "github_url": "https://github.com/dhileepant",
  "overall_confidence": 0.91
}
```

---

# Design Decisions

### Deterministic Entity Resolution

The assignment explicitly states:

> **"Wrong-but-confident is worse than honestly-empty."**

To align with this philosophy, candidate profiles are merged **only** when strong identifiers match exactly:

- Email
- Phone Number
- GitHub URL

This avoids false-positive merges while ensuring explainable, deterministic behavior.

---

### Provenance Tracking

Every field records:

- Source
- Extraction method
- Confidence

allowing complete traceability for all generated data.

---

### Modular Extraction

Each source has an independent parser (located in `src/extractors.py`), making it easy to support additional sources without modifying downstream components.

---

### Configurable Output

The repository supports dynamic runtime projections to shape the output exactly as needed, without changing any backend logic.
- **`default_config.json`**: Outputs the official canonical schema mandated by the Eightfold assignment (including complex objects for location, links, and provenance).
- **`custom_config.json`**: Outputs a simplified, flattened schema (e.g., pulling `primary_email` directly from `emails[0]`, collapsing skills into an array of strings).

---

# Assumptions

- Recruiter CSV contains reliable structured data.
- Resume PDFs contain selectable text (not scanned images).
- GitHub profile information is publicly accessible.
- Email, phone number and GitHub URL are treated as strong identifiers for entity resolution.

---

# Limitations

- OCR for scanned resumes is not currently supported.
- LinkedIn integration is intentionally excluded due to the lack of a public API.
- Skill extraction uses heuristic parsing rather than semantic NLP/LLMs to ensure this codebase is runnable out-of-the-box locally without external API keys.

---

# Future Improvements

- ATS JSON parser
- LinkedIn parser
- OCR support for scanned resumes
- LLM-based semantic skill extraction
- Batch processing
- Async source ingestion
- Additional configurable normalization strategies

---

# Deliverables

- ✅ Technical Design (Provided separately)
- ✅ Source Code
- ✅ README
- ✅ Sample Outputs (`final_output.json`)
- ✅ Test Suite
- ✅ Demo Video
