from docx import Document
import PyPDF2

def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        return "\n".join([page.extract_text() or "" for page in reader.pages])

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])
