# Multi-Source Candidate Data Transformer

This repository contains the submission for the **Eightfold Engineering Intern (Jul-Dec 2026) Assignment** by **Dhileepan T** (`dhileepantv@gmail.com`).

🎥 **[Insert Demo Video Link Here]**

## 🎯 Assignment Checklist & Implementation

This pipeline is engineered to ingest messy candidate data from multiple sources (both structured and unstructured) and resolve it into a single clean, canonical profile per candidate.

- ✅ **Run end-to-end & emit valid JSON**: Exposes a thin CLI that dynamically processes inputs and outputs schema-valid JSON based on `config.json`.
- ✅ **Cover at least 2 source types**: Successfully processes:
  - **Structured**: Recruiter CSV Export (`recruiter_export.csv`)
  - **Unstructured**: Resume PDF (`resume_dhileepan.pdf`, `resume_jane.pdf`)
  - **Structured API**: GitHub Profile via URL extraction.
- ✅ **Normalize correctly**: Built-in normalizers handle converting Phone numbers to E.164 format, dates to YYYY-MM, and a custom normalizer that tokenizes and deduplicates skills into canonical forms (e.g. `react`, `react.js`, `reactjs` -> `React.js`).
- ✅ **Merge across sources into one record**: Implements a robust **Deterministic Match Engine** prioritizing strong identifiers (Email, E.164 Phone, GitHub URL) to group and merge records.
- ✅ **Provenance and confidence**: Every output field is traced via a `provenance` log detailing the original `source`, extraction `method`, and assigned `confidence` level.
- ✅ **Degrade gracefully**: Handles missing files (e.g., throwing a non-fatal warning if an input file is missing or a garbage URL is passed) and continues processing valid sources. 
- ✅ **Automated Tests**: Comprehensive Pytest suite covering normalization, deterministic merging logic, and edge cases.

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- `pip`

### Setup

```bash
# Create and activate a virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\Activate.ps1
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install pydantic phonenumbers python-dateutil pypdf pytest
```

## 🛠 Exact Run Steps

### 1. Run the Data Pipeline
A thin CLI is provided. Pass the input files (CSV, PDF, or API URLs), the projection config, and an output file. 

*Note: The CLI degrades gracefully; if you pass a missing/garbage file (like `missing.pdf`), it logs a warning but still successfully processes the rest.*

```bash
python src/cli.py --inputs inputs/recruiter_export.csv inputs/resume_dhileepan.pdf inputs/resume_jane.pdf missing.pdf https://github.com/dhileepant --config config.json --output final_output.json
```

**What happens here:**
1. The pipeline parses the CSV, PDFs, and makes a live fetch to the GitHub API.
2. The Deterministic Merge Engine observes that the GitHub API and the `resume_dhileepan.pdf` share the exact same GitHub URL (extracted from hidden PDF hyperlinks!).
3. The CSV shares the same Email. 
4. All three sources are dynamically merged into **one** canonical profile for Dhileepan T, with fields prioritized by confidence scores. The output is printed to the CLI and saved to `final_output.json`.

### 2. Run the Test Suite
The unit tests validate the core architectural components (Normalizers and the Deterministic Match Engine), including an edge case testing that two profiles with matching names but no matching strong identifiers are correctly kept separate (preventing false-positive merges).

```bash
pytest tests/
```

## 🧠 Design Decisions, Assumptions & Descoping

1. **Deterministic Merging (Zero False-Positives)**: The assignment dictates that "incorrect but confident outputs are worse than incomplete ones". Therefore, I descoped probabilistic threshold scoring (e.g. matching based on Name + Company). Two profiles are *only* merged if they share an exact match on a strong identifier (Email, Phone, GitHub URL).
2. **Confidence-Based Projection**: Conflict resolution between merged records prioritizes high-fidelity sources over heuristic extraction. For example, a name extracted directly from a GitHub API is given a higher base confidence (0.95) than a name extracted via NLP/Regex from an unstructured PDF (0.80).
3. **Regex over LLMs for PDFs**: Instead of using an LLM (which requires paid API keys to test) or a heavy NLP suite, I built the PDF unstructured extraction using modular Regex heuristics. This ensures the evaluator can run this repository completely out-of-the-box locally.
4. **Configuration Mapping**: The `config.json` leverages a simplified JSONPath-style syntax (`from: "emails[0]"`) to dynamically map the internal Pydantic CanonicalProfile into whatever final shape the consumer needs.

## 📦 Deliverables Included

- **Step 1 (Technical Design)**: Available upon request or via application portal.
- **Step 2 (Implementation)**: This repository.
- **Output Data**: `final_output.json`
- **Demo Video**: [Link at top of document]
