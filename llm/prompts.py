RESUME_PROMPT = """
Extract structured information from the following resume text and return valid JSON.
Include the candidate's name, contact details, skills, work experience, and education.
"""

INVOICE_PROMPT = """
Extract structured information from the following invoice text and return valid JSON.
Include invoice number, date, vendor/customer details, line items, subtotal, tax, and total.
"""

MEDICAL_REPORT_PROMPT = """
Extract structured information from the following medical report text and return valid JSON.
Include patient name, date, physician, diagnosis, symptoms, findings, and medications.
"""

MEETING_NOTES_PROMPT = """
Extract structured information from the following meeting notes text and return valid JSON.
Include meeting title, date, attendees, agenda, discussion points, decisions, and action items.
"""

RESEARCH_PAPER_PROMPT = """
Extract structured information from the following research paper text and return valid JSON.
Include title, authors, abstract, keywords, sections, methodology, conclusion, and references.
"""

DOCUMENT_PROMPTS = {
    "Resume": RESUME_PROMPT,
    "Invoice": INVOICE_PROMPT,
    "Medical Report": MEDICAL_REPORT_PROMPT,
    "Meeting Notes": MEETING_NOTES_PROMPT,
    "Research Paper": RESEARCH_PAPER_PROMPT,
}

GENERIC_EXTRACTION_PROMPT = """
Extract structured information from the following text and return it as valid JSON.
"""

SUMMARIZATION_PROMPT = """
Summarize the following text concisely.
"""
