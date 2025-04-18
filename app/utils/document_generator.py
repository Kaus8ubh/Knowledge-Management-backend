from datetime import datetime
from fpdf import FPDF
from docx import Document
from docx.shared import Pt
from bs4 import BeautifulSoup  
import io

class DocumentGenerator:

    def _convert_html_to_text(self, html_content):
        """Convert HTML content into formatted text for FPDF and python-docx."""
        # Use BeautifulSoup to parse and clean HTML content
        soup = BeautifulSoup(html_content, "html.parser")
        return soup

    def generate_card_pdf(self,card_data):
        """generate pdf document from card data"""
        pdf = FPDF()
        pdf.add_page()

        # title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, card_data.get("title", "Knowledge Card"), ln=True)

       # creation date
        if "created_at" in card_data:
            created_at = card_data["created_at"]
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at)
                except ValueError:
                    try:
                        created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        created_at = None  # fallback if parsing fails

            if created_at:
                pdf.set_font("Arial", "I", 10)
                pdf.cell(0, 8, f"Created: {created_at.strftime('%Y-%m-%d')}", ln=True)

        # notes
        if "note" in card_data:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Note:", ln=True)
            pdf.set_font("Arial", "", 12)
            note_html = card_data["note"]
            note_content = self._convert_html_to_text(note_html)
            pdf.multi_cell(0, 10, note_content.text)    

        # summary
        if "summary" in card_data:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Summary:", ln=True)
            pdf.set_font("Arial", "", 12)
            summary_html = card_data["summary"]
            summary_content = self._convert_html_to_text(summary_html)
            pdf.multi_cell(0, 10, summary_content.text)

        # source URL
        if "source_url" in card_data:
            pdf.set_font("Arial", "I", 10)
            pdf.cell(0, 10, f"Source: {card_data['source_url']}", ln=True)

        # Return the PDF as bytes
        # Write PDF content to BytesIO buffer
        pdf_bytes = pdf.output(dest='S').encode('latin1')
        return pdf_bytes
    
    def generate_card_docx(self, card_data):
        """Generate a Word document from card data"""
        doc = Document()
        
        # title
        doc.add_heading(card_data.get("title", "Knowledge Card"), 0)
        
        # creation date if available
        if "created_at" in card_data:
            created_at = card_data["created_at"]
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at)
                except ValueError:
                    try:
                        created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        created_at = None  # fallback

            if created_at:
                p = doc.add_paragraph(f"Created: {created_at.strftime('%Y-%m-%d')}")
                p.runs[0].italic = True

        # user notes
        if "note" in card_data:
            doc.add_heading("Note:", level=1)
            note_html = card_data["note"]
            note_content = self._convert_html_to_text(note_html)
            doc.add_paragraph(note_content.text)   

        # summary
        if "summary" in card_data:
            doc.add_heading("Summary:", level=1)
            summary_html = card_data["summary"]
            summary_content = self._convert_html_to_text(summary_html)
            doc.add_paragraph(summary_content.text)
                    
        # source URL
        if "source_url" in card_data:
            p = doc.add_paragraph("Source: ")
            p.add_run(card_data["source_url"]).italic = True
        
        # Return the document as bytes
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()