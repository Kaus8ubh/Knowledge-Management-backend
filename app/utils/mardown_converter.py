import markdown

def convert_summary_to_html(summary_text: str) -> str:
    """
    Converts structured plain/markdown-like summary text into HTML.
    Useful for rendering in rich text editors like React Quill.
    """
    html_markup = markdown.markdown(summary_text, extensions=['extra'])
    return html_markup
