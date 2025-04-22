from .jwt_handler import create_access_token, decode_access_token
from .custom_exceptions import DatabaseError, NotFoundError
from .sraper import Scraper
from .ai_gemini import TextProcessingWithGemini
from .embedder import Embedder
from .thumbnails import get_thumbnail
from .cosine_distance_matrix import cosine_distance_matrix
from .topic_name_generator import generate_topic_name
from .clustering_module import clustering_module
from .youtube_url_checker import is_youtube_url
from .get_yt_transcript import get_video_id, get_yt_transcript_text
from .document_generator import DocumentGenerator
from .knowledge_card_helper import to_knowledge_card
from .mardown_converter import convert_summary_to_html
from .extract_text_from_file import extract_text_from_pdf, extract_text_from_docx

scraper = Scraper()
embedder_for_title = Embedder()
gemini_text_processor = TextProcessingWithGemini()
pdf_docx_generator = DocumentGenerator()

__all__ = ["create_access_token", "decode_access_token", "DatabaseError", "NotFoundError", "scraper","embedder_for_title","gemini_text_processor","get_thumbnail",
           "cosine_distance_matrix", "generate_topic_name", "clustering_module", "is_youtube_url", "get_yt_transcript_text", "get_video_id", "pdf_docx_generator",
           "to_knowledge_card", "convert_summary_to_html", "extract_text_from_pdf", "extract_text_from_docx"]