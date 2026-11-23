from fpdf import FPDF
import os

# Create a directory for the PDF files
pdf_dir = "docs"
os.makedirs(pdf_dir, exist_ok=True)

# Sample dummy medical records
records = {
    "Patient_JohnDoe_Record.pdf": """
    Patient Name: John Doe
    Age: 52
    Date of Visit: 2025-10-01
    Diagnosis: Type 2 Diabetes Mellitus, Hypertension
    Medications: Metformin 500 mg BID, Lisinopril 10 mg daily
    Notes: Patient reports occasional dizziness upon standing. Blood pressure averaging 148/92 mmHg over last two visits. Recommended lifestyle modifications: diet low in sodium, increase physical activity to 30 minutes per day.
    """,
    "Patient_JaneSmith_Record.pdf": """
    Patient Name: Jane Smith
    Age: 38
    Date of Visit: 2025-09-15
    Diagnosis: Asthma (moderate persistent)
    Medications: Fluticasone/Salmeterol inhaler twice daily, as needed albuterol inhaler
    Notes: Patient had two exacerbations in past year requiring oral steroids. Advised asthma action plan, trigger avoidance, spirometry to be scheduled.
    """,
    "Patient_AliceBrown_Record.pdf": """
    Patient Name: Alice Brown
    Age: 29
    Date of Visit: 2025-08-12
    Diagnosis: Iron Deficiency Anemia
    Medications: Ferrous sulfate 325 mg once daily
    Notes: Complains of fatigue and weakness. Hemoglobin: 10.2 g/dL. Advised dietary changes to include iron-rich foods, follow-up labs in 2 months.
    """,
    "Patient_MichaelGreen_Record.pdf": """
    Patient Name: Michael Green
    Age: 47
    Date of Visit: 2025-07-20
    Diagnosis: Hyperlipidemia
    Medications: Atorvastatin 20 mg daily
    Notes: LDL cholesterol 165 mg/dL. Recommends statin therapy, exercise, diet modification. Follow-up lipid panel in 3 months.
    """,
    "Patient_LindaWhite_Record.pdf": """
    Patient Name: Linda White
    Age: 60
    Date of Visit: 2025-06-30
    Diagnosis: Osteoarthritis (Knees)
    Medications: Acetaminophen 1000 mg TID
    Notes: Reports chronic knee pain worsened by walking. No signs of inflammation. Referred to physical therapy and advised joint strengthening exercises.
    """,
    "Patient_AliceMckinzy_Record.pdf": """
    Patient Name: Alice Mckinzy
    Age: 40
    Date of Visit: 2025-06-12
    Diagnosis: Hyperlipidemia
    Medications: Atorvastatin 20 mg daily
    Notes: LDL cholesterol 190 mg/dL. Recommends statin therapy, exercise, diet modification. Follow-up lipid panel in 3 months.
    """
}

# Generate PDFs from the records
for filename, content in records.items():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in content.strip().split('\n'):
        pdf.multi_cell(0, 10, line.strip())
    pdf.output(os.path.join(pdf_dir, filename))

print(f"Dummy PDFs created in '{pdf_dir}' folder.")
