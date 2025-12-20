"""
Utility functions for blog content processing
"""
import re
from urllib.parse import urlparse, parse_qs

def process_blog_content(content):
    """
    Process blog content - can add formatting, link processing, etc.
    Currently returns content as-is but can be extended.
    """
    if not content:
        return ""
    
    # Basic processing - can be extended
    return content


def extract_youtube_video_id(url):
    """
    Extract YouTube video ID from various YouTube URL formats.
    
    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID
    
    Returns video ID or None if invalid URL.
    """
    if not url:
        return None
    
    # Remove whitespace
    url = url.strip()
    
    # Pattern for standard YouTube URLs
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def get_youtube_embed_url(url):
    """
    Convert YouTube URL to embed URL.
    
    Returns embed URL or None if invalid.
    """
    video_id = extract_youtube_video_id(url)
    if video_id:
        return f"https://www.youtube.com/embed/{video_id}"
    return None


def insert_youtube_video_in_content(content, youtube_url):
    """
    Insert YouTube video embed after the second H2 heading (and its content), 
    or after the second H3 if no second H2 exists.
    
    The video is placed after the header's content but before the next header starts.
    
    Args:
        content: HTML content string
        youtube_url: YouTube video URL
    
    Returns:
        HTML content with video embed inserted
    """
    if not youtube_url or not content:
        return content
    
    video_id = extract_youtube_video_id(youtube_url)
    if not video_id:
        return content
    
    # Create the video embed HTML
    video_html = f'''
<div class="youtube-video-container" style="margin: 3rem 0; max-width: 100%;">
    <div class="youtube-video-wrapper" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <iframe 
            src="https://www.youtube.com/embed/{video_id}" 
            frameborder="0" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
            allowfullscreen
            style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
        </iframe>
    </div>
</div>'''
    
    # Strategy 1: Find second H2 heading
    h2_pattern = r'</h2>'
    h2_matches = list(re.finditer(h2_pattern, content, re.IGNORECASE))
    
    if len(h2_matches) >= 2:
        # We have at least 2 H2 headings
        second_h2_end = h2_matches[1].end()
        
        # Find the next header (H1-H6) after the second H2
        next_header_pattern = r'<(h[1-6])(?:\s[^>]*)?>'
        next_header_match = re.search(next_header_pattern, content[second_h2_end:], re.IGNORECASE)
        
        if next_header_match:
            # Insert before the next header
            insert_position = second_h2_end + next_header_match.start()
            # Skip any whitespace before the header
            while insert_position > second_h2_end and content[insert_position - 1] in ' \n\r\t':
                insert_position -= 1
            return content[:insert_position] + video_html + content[insert_position:]
        else:
            # No next header found, insert at the end of content after second H2
            return content[:second_h2_end] + video_html + content[second_h2_end:]
    
    # Strategy 2: If no second H2, try second H3 heading
    h3_pattern = r'</h3>'
    h3_matches = list(re.finditer(h3_pattern, content, re.IGNORECASE))
    
    if len(h3_matches) >= 2:
        # We have at least 2 H3 headings
        second_h3_end = h3_matches[1].end()
        
        # Find the next header (H1-H6) after the second H3
        next_header_pattern = r'<(h[1-6])(?:\s[^>]*)?>'
        next_header_match = re.search(next_header_pattern, content[second_h3_end:], re.IGNORECASE)
        
        if next_header_match:
            # Insert before the next header
            insert_position = second_h3_end + next_header_match.start()
            # Skip any whitespace before the header
            while insert_position > second_h3_end and content[insert_position - 1] in ' \n\r\t':
                insert_position -= 1
            return content[:insert_position] + video_html + content[insert_position:]
        else:
            # No next header found, insert at the end of content after second H3
            return content[:second_h3_end] + video_html + content[second_h3_end:]
    
    # Fallback: If no second H2 or H3, insert at the end
    return content + video_html
