from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import parse_qs, urlparse

def get_video_id(youtube_url):
    parsed_url = urlparse(youtube_url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    elif parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        return parse_qs(parsed_url.query).get('v', [None])[0]
    return None

def get_yt_transcript_text(url: str) -> str:
    video_id = get_video_id(url)
    if not video_id:
        return "Invalid YouTube URL"
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([t['text'] for t in transcript])
    except Exception as e:
        return f"Transcript not available: {e}"
