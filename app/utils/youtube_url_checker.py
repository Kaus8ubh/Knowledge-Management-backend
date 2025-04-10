from urllib.parse import urlparse

def is_youtube_url(url: str) -> bool:
    parsed_url = urlparse(url)
    return parsed_url.hostname in ['www.youtube.com', 'youtube.com', 'youtu.be']
