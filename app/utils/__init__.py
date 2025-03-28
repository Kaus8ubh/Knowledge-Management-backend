from .jwt_handler import create_access_token, decode_access_token
from .custom_exceptions import DatabaseError, NotFoundError
from .sraper import Scraper
from .ai_gemini import TextProcessingWithGemini
from .embedder import Embedder
from .thumbnails import get_thumbnail

scraper = Scraper()
embedder_for_title = Embedder()
gemini_text_processor = TextProcessingWithGemini()

__all__ = ["create_access_token", "decode_access_token", "DatabaseError", "NotFoundError", "scraper","embedder_for_title","gemini_text_processor","get_thumbnail"]