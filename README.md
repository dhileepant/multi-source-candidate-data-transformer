# Multi-Source Candidate Data Transformer

This is the submission for the Eightfold Engineering Intern (Jul-Dec 2026) Assignment by Dhileepan T (dhileepantv@gmail.com).

## Problem Statement

The goal is to build a robust pipeline that ingests candidate data from multiple messy sources (both structured and unstructured) and produces a single clean, canonical profile per candidate. The output must be configurable at runtime.

## Sources Handled

- **Structured**: Recruiter CSV Export (`.csv`)
- **Unstructured**: Resume PDF (`.pdf`)

## Getting Started

### Prerequisites
- Python 3.9+
- `pip`

### Setup

```bash
# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install pydantic phonenumbers python-dateutil pypdf
```

### Running the Pipeline

A thin CLI is provided to run the pipeline. You must pass the input files and a configuration JSON file.

```bash
# Example Run
python src/cli.py --inputs inputs/recruiter_export.csv inputs/resume_dhileepan.pdf inputs/resume_jane.pdf --config config.json
```

To save the output to a file instead of printing to stdout:
```bash
python src/cli.py --inputs inputs/recruiter_export.csv inputs/resume_dhileepan.pdf --config config.json --output final_profiles.json
```

### Running Tests

```bash
pip install pytest
pytest tests/
```

## Design Decisions & Assumptions

1. **Deterministic & Explainable**: The pipeline tracks `provenance` for every extracted field (source and method). Conflict resolution prioritizes structured CSV data over heuristic PDF extraction, with higher confidence assigned to structured fields.
2. **Robustness**: Missing files or un-parseable values (like an invalid phone number) are gracefully handled. The pipeline will not crash; it either falls back to the original string or skips the invalid field based on strictness logic.
3. **Descoping**: Instead of hitting real LinkedIn/GitHub APIs or using a large LLM which requires API keys to run, I simulated the unstructured extraction pipeline using RegEx heuristics on the PDF text to ensure this repository is runnable out-of-the-box for evaluation.
4. **Configuration**: The `config.json` uses a simplified JSONPath-like syntax (`from: "emails[0]"`) to project the internal Pydantic canonical model into the final output JSON.

## Deliverables Included

- **Step 1 - Technical Design**: `DHILEEPAN_T_dhileepantv@gmail.com_Eightfold.pdf`
- **Step 2 - Implementation**: This repository (Code, Tests, Mock Inputs).
