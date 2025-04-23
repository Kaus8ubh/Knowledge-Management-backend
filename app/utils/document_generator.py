from datetime import datetime
from fpdf import FPDF
from docx import Document
from docx.shared import Pt
from bs4 import BeautifulSoup  
import io
from weasyprint import HTML

class DocumentGenerator:

    def _convert_html_to_text(self, html_content):
        """Convert HTML content into formatted text for FPDF and python-docx."""
        # Use BeautifulSoup to parse and clean HTML content
        soup = BeautifulSoup(html_content, "html.parser")
        return soup

    def generate_card_pdf(self,card_data):
        """Generate a PDF with proper formatting using HTML and WeasyPrint."""

        # Format creation date
        created_at_str = ""
        if "created_at" in card_data:
            created_at = card_data["created_at"]
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at)
                except ValueError:
                    try:
                        created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        created_at = None
            if created_at:
                created_at_str = f"<h3><em>Created: {created_at.strftime('%Y-%m-%d')}</em></h3>"

        # HTML template
        html_content = f"""
        <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        padding: 20px;
                    }}
                    h1 {{
                        font-size: 28px;
                        font-weight: bold;
                    }}
                    h2 {{
                        font-size: 18px;
                        margin-top: 20px;
                    }}
                    p {{
                        font-size: 14px;
                        line-height: 1.6;
                    }}
                    .source {{
                        color: blue;
                    }}
                </style>
            </head>
            <body>
                <h1>{card_data.get("title", "Knowledge Card")}</h1>
                {created_at_str}
                <h3 class="source"><em>Source: {card_data.get("source_url", "N/A")}</em></h3>
                <hr>
                <h2>Note:</h2>
                {card_data.get("note", "<p>No notes.</p>")}
                <hr>
                <h2>Summary:</h2>
                {card_data.get("summary", "<p>No summary.</p>")}
            </body>
        </html>
        """

        # Generate and return PDF as bytes
        pdf_bytes = HTML(string=html_content).write_pdf()
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