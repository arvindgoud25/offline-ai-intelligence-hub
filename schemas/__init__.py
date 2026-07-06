RESUME_SCHEMA = {
    "title": "Resume",
    "description": "Extracted information from a resume or CV",
    "fields": {
        "full_name": {"type": "string", "description": "Candidate's full name"},
        "email": {"type": "string", "description": "Email address"},
        "phone": {"type": "string", "description": "Phone number"},
        "summary": {
            "type": "string",
            "description": "Professional summary or objective",
        },
        "skills": {"type": "array", "items": "string", "description": "List of skills"},
        "experience": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "job_title": {"type": "string"},
                    "company": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                    "description": {"type": "string"},
                },
            },
            "description": "Work experience entries",
        },
        "education": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "degree": {"type": "string"},
                    "institution": {"type": "string"},
                    "year": {"type": "string"},
                },
            },
            "description": "Education history",
        },
    },
}

INVOICE_SCHEMA = {
    "title": "Invoice",
    "description": "Extracted information from an invoice",
    "fields": {
        "invoice_number": {"type": "string", "description": "Invoice identifier"},
        "date": {"type": "string", "description": "Invoice date"},
        "due_date": {"type": "string", "description": "Payment due date"},
        "vendor_name": {"type": "string", "description": "Seller / vendor name"},
        "customer_name": {"type": "string", "description": "Buyer / customer name"},
        "line_items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "quantity": {"type": "number"},
                    "unit_price": {"type": "number"},
                    "total": {"type": "number"},
                },
            },
            "description": "Items or services listed on the invoice",
        },
        "subtotal": {"type": "number", "description": "Amount before tax"},
        "tax": {"type": "number", "description": "Tax amount"},
        "total": {"type": "number", "description": "Total amount due"},
    },
}

MEDICAL_REPORT_SCHEMA = {
    "title": "Medical Report",
    "description": "Extracted information from a medical report",
    "fields": {
        "patient_name": {"type": "string", "description": "Patient's full name"},
        "date_of_birth": {"type": "string", "description": "Patient's date of birth"},
        "report_date": {"type": "string", "description": "Date of the report"},
        "physician": {"type": "string", "description": "Attending physician name"},
        "diagnosis": {"type": "string", "description": "Primary diagnosis"},
        "symptoms": {
            "type": "array",
            "items": "string",
            "description": "Reported symptoms",
        },
        "findings": {"type": "string", "description": "Clinical findings"},
        "medications": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "dosage": {"type": "string"},
                    "frequency": {"type": "string"},
                },
            },
            "description": "Prescribed medications",
        },
        "notes": {
            "type": "string",
            "description": "Additional notes or recommendations",
        },
    },
}

MEETING_NOTES_SCHEMA = {
    "title": "Meeting Notes",
    "description": "Extracted information from meeting notes or minutes",
    "fields": {
        "title": {"type": "string", "description": "Meeting title or subject"},
        "date": {"type": "string", "description": "Meeting date"},
        "attendees": {
            "type": "array",
            "items": "string",
            "description": "List of attendees",
        },
        "agenda": {
            "type": "array",
            "items": "string",
            "description": "Agenda items discussed",
        },
        "discussion_points": {
            "type": "array",
            "items": "string",
            "description": "Key discussion points",
        },
        "decisions": {
            "type": "array",
            "items": "string",
            "description": "Decisions made",
        },
        "action_items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "task": {"type": "string"},
                    "assignee": {"type": "string"},
                    "deadline": {"type": "string"},
                },
            },
            "description": "Action items with assignees",
        },
    },
}

RESEARCH_PAPER_SCHEMA = {
    "title": "Research Paper",
    "description": "Extracted information from a research paper",
    "fields": {
        "title": {"type": "string", "description": "Paper title"},
        "authors": {
            "type": "array",
            "items": "string",
            "description": "List of authors",
        },
        "abstract": {"type": "string", "description": "Paper abstract"},
        "keywords": {"type": "array", "items": "string", "description": "Keywords"},
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "heading": {"type": "string"},
                    "content": {"type": "string"},
                },
            },
            "description": "Sections with headings and content",
        },
        "methodology": {"type": "string", "description": "Research methodology"},
        "conclusion": {"type": "string", "description": "Conclusion or findings"},
        "references": {
            "type": "array",
            "items": "string",
            "description": "List of references",
        },
    },
}

DOCUMENT_SCHEMAS = {
    "Resume": RESUME_SCHEMA,
    "Invoice": INVOICE_SCHEMA,
    "Medical Report": MEDICAL_REPORT_SCHEMA,
    "Meeting Notes": MEETING_NOTES_SCHEMA,
    "Research Paper": RESEARCH_PAPER_SCHEMA,
}
