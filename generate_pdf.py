from fpdf import FPDF
import datetime

class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 15)
        self.cell(0, 10, 'Step 1 - Technical Design: Multi-Source Candidate Data Transformer', new_x="LMARGIN", new_y="NEXT", align='C')
        self.set_font('Helvetica', 'I', 10)
        self.cell(0, 10, 'Dhileepan T - dhileepantv@gmail.com', new_x="LMARGIN", new_y="NEXT", align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

pdf = PDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.set_font("Helvetica", size=11)

content = """
1. Pipeline / Step Breakdown
- Detect & Load: Read input files (CSV, JSON, PDF) and identify the source type.
- Extract:
  - Structured: Map fields from CSV/JSON to the canonical schema.
  - Unstructured: Use NLP/Regex to parse free-text (resume PDFs) into structured fields.
- Normalize: Standardize individual fields (e.g., dates to YYYY-MM, phones to E.164, countries to ISO-3166).
- Merge & Confidence: Group records by candidate using email/name. Resolve conflicts using source-priority and calculate an overall confidence score.
- Project-to-Output: Apply the runtime JSON configuration to reshape the record into the desired output.
- Validate: Ensure the final projected output conforms to the requested schema.

2. Canonical Output Schema & Normalized Formats
- Dates: YYYY-MM using dateutil.
- Phones: E.164 (e.g., +14155551234) using phonenumbers.
- Country: ISO-3166 alpha-2.
- Skills: Lowercased, stripped, mapped to a canonical list.
- Representation: Pydantic models for strict typing.

3. Merge / Conflict-Resolution Policy & Confidence
- Match Keys: Primary key is email. Fallback is full_name.
- Conflict Resolution: Source priority: 1) ATS/Structured Data (Highest), 2) Direct APIs, 3) Resume Parsing, 4) Recruiter Notes (Lowest).
- Confidence Scoring: ATS (0.95), API (0.90), Resume (0.80), Notes (0.60).
- Provenance: Tracks {"field": "...", "source": "...", "method": "..."} for every populated field.

4. Runtime Custom-Output Config (Projection)
- Iterates over config.fields. Uses custom traversal to fetch values from the internal canonical record using the "from" path (e.g., emails[0]).
- Applies field-level normalize rules.
- Handles missing values based on "on_missing" (null, omit, error).
- Includes or excludes provenance and overall_confidence based on flags.

5. Edge Cases & Handling
- Garbage/Missing Source File: Pipeline logs an error for the specific file but continues processing other files (Robustness).
- Un-normalizable Phone: Kept as-is with lower confidence or set to null based on strictness. Never crashes.
- Missing Match Key: Treat as a new candidate to avoid incorrect merges.
- Time-pressure Descoping: Mocked NLP extraction with RegEx heuristics to avoid external LLM dependencies for the assignment.
"""

for line in content.split('\n'):
    if line.startswith(('1.', '2.', '3.', '4.', '5.')):
        pdf.set_font("Helvetica", 'B', 12)
        pdf.write(txt=line + "\n")
        pdf.set_font("Helvetica", size=11)
    else:
        pdf.write(txt=line + "\n")

pdf.output("DHILEEPAN_T_dhileepantv@gmail.com_Eightfold.pdf")
print("Generated PDF.")
