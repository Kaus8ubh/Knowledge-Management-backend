from typing import List, Dict, Any
import google.generativeai as genai
from config import Config

api_key = Config.GEMINI_API_KEY 
genai.configure(api_key=api_key)

def generate_topic_name(cards: List[Dict[str, Any]]) -> str:
    """
    Usage: Generate a topic name for a cluster of cards
    Parameter: cards: List of knowledge cards
    Returns: Topic name as a string
    """
    all_tags = []
    for card in cards:
        tags = card.get("tags", [])
        if isinstance(tags, list) and tags:
            all_tags.extend(tags)

    if all_tags:
        try:
            client = genai.GenerativeModel("gemini-2.0-flash")
            response = client.generate_content(f"""
                                       Generate a two to max three word Title based on given tags:
                                       {all_tags}
                                       Guidelines:
                                       1. give a title for the overall topic of the tags
                                       2. don't go beyond 3 words.
                                       """)

            if response and hasattr(response, 'candidates') and len(response.candidates) > 0:
                title = response.candidates[0].content.parts[0].text.strip()
            else:
                title = "No valid title generated"
    
        except Exception as e:
            title = f"Error generating title: {str(e)}"

        return title

