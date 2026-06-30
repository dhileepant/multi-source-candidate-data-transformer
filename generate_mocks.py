import csv
import os
from fpdf import FPDF

# Create input directory
os.makedirs("inputs", exist_ok=True)

# 1. Generate CSV (Recruiter export)
csv_data = [
    {"name": "Dhileepan T", "email": "dhileepantv@gmail.com", "phone": "123-456-7890", "current_company": "Tech Corp", "title": "Software Engineer Intern"},
    {"name": "Jane Doe", "email": "jane.doe@example.com", "phone": "(555) 123-4567", "current_company": "InnoSoft", "title": "Backend Dev"},
]

with open("inputs/recruiter_export.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "email", "phone", "current_company", "title"])
    writer.writeheader()
    writer.writerows(csv_data)

# 2. Generate PDF (Resume)
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

# Resume 1
pdf.cell(200, 10, txt="Dhileepan T", ln=True, align="C")
pdf.cell(200, 10, txt="Email: dhileepantv@gmail.com | Phone: +1 123-456-7890", ln=True, align="C")
pdf.cell(200, 10, txt="", ln=True)
pdf.cell(200, 10, txt="Skills: Python, React, Data Pipelines, SQL", ln=True)
pdf.cell(200, 10, txt="", ln=True)
pdf.cell(200, 10, txt="Experience", ln=True)
pdf.cell(200, 10, txt="Software Engineer Intern at Tech Corp (Jan 2023 - Present)", ln=True)
pdf.cell(200, 10, txt="Education", ln=True)
pdf.cell(200, 10, txt="B.Tech Computer Science, Anna University (2025)", ln=True)

pdf.output("inputs/resume_dhileepan.pdf")

# Resume 2
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="Jane Doe", ln=True, align="C")
pdf.cell(200, 10, txt="Email: jane.doe@example.com | Phone: 555-123-4567", ln=True, align="C")
pdf.cell(200, 10, txt="", ln=True)
pdf.cell(200, 10, txt="Skills: Java, Spring Boot, MySQL", ln=True)
pdf.cell(200, 10, txt="", ln=True)
pdf.cell(200, 10, txt="Experience", ln=True)
pdf.cell(200, 10, txt="Backend Dev at InnoSoft (March 2022 - Aug 2023)", ln=True)
pdf.cell(200, 10, txt="Education", ln=True)
pdf.cell(200, 10, txt="BS CS, XYZ University (2024)", ln=True)

pdf.output("inputs/resume_jane.pdf")

print("Generated mock inputs.")
