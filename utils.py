"""
Utility functions for content processing
"""
import html
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def process_blog_content(content):
    """
    Process blog content to fix:
    - HTML entities
    - Image URLs
    - Links
    - Code formatting
    """
    if not content:
        return ""
    
    # Decode HTML entities
    content = html.unescape(content)
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    
    # Fix image URLs - ensure they're absolute and working
    for img in soup.find_all('img'):
        src = img.get('src', '')
        if src:
            # If it's a local upload, keep it as relative path
            if src.startswith('/static/uploads/') or src.startswith('static/uploads/'):
                # Ensure it starts with /static/uploads/
                if src.startswith('static/'):
                    img['src'] = '/' + src
                else:
                    img['src'] = src
            # If it's a Blogger CDN URL, keep it as is
            elif 'blogger.googleusercontent.com' in src:
                # Ensure full URL
                if not src.startswith('http'):
                    img['src'] = 'https:' + src if src.startswith('//') else src
            else:
                # Make relative URLs absolute
                if not src.startswith('http'):
                    img['src'] = urljoin('http://192.168.1.51:5000/', src)
            
            # Add responsive classes and styling
            img['class'] = img.get('class', []) + ['blog-image']
            img['loading'] = 'lazy'
            img['style'] = 'max-width: 100%; height: auto; border-radius: 8px; margin: 20px 0;'
    
    # Fix links - ensure they open in new tab and are absolute
    for link in soup.find_all('a'):
        href = link.get('href', '')
        if href:
            # Make relative URLs absolute
            if href.startswith('/') or (not href.startswith('http') and not href.startswith('#')):
                link['href'] = urljoin('http://192.168.1.51:5000/', href)
            
            # Add target and rel for external links
            if href.startswith('http') and 'http://192.168.1.51:5000/' not in href:
                link['target'] = '_blank'
                link['rel'] = 'noopener noreferrer'
    
    # Improve code blocks
    for pre in soup.find_all('pre'):
        pre['class'] = pre.get('class', []) + ['code-block', 'language-javascript']
        # Wrap code tags inside pre if not already present
        if not pre.find('code'):
            code_tag = soup.new_tag('code')
            code_tag.string = pre.get_text()
            pre.clear()
            pre.append(code_tag)
        
        # Detect language from content
        code_text = pre.get_text().lower()
        if 'php' in code_text or '<?php' in code_text:
            pre['class'] = [c for c in pre.get('class', []) if not c.startswith('language-')] + ['language-php']
        elif 'python' in code_text or 'import ' in code_text or 'def ' in code_text:
            pre['class'] = [c for c in pre.get('class', []) if not c.startswith('language-')] + ['language-python']
        elif 'javascript' in code_text or 'function' in code_text or 'var ' in code_text:
            pre['class'] = [c for c in pre.get('class', []) if not c.startswith('language-')] + ['language-javascript']
        elif 'html' in code_text or '<!DOCTYPE' in code_text or '<html' in code_text:
            pre['class'] = [c for c in pre.get('class', []) if not c.startswith('language-')] + ['language-html']
        elif 'css' in code_text or '{' in code_text and ':' in code_text:
            pre['class'] = [c for c in pre.get('class', []) if not c.startswith('language-')] + ['language-css']
    
    # Improve headings styling
    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        heading['class'] = heading.get('class', []) + ['content-heading']
    
    # Clean up empty divs and paragraphs
    for tag in soup.find_all(['div', 'p']):
        if not tag.get_text(strip=True) and not tag.find_all(['img', 'iframe', 'video']):
            tag.decompose()
    
    # Remove Blogger-specific attributes
    for tag in soup.find_all(True):
        # Remove Blogger-specific attributes
        for attr in ['dir', 'trbidi', 'imageanchor', 'data-original-height', 'data-original-width']:
            if attr in tag.attrs:
                del tag.attrs[attr]
    
    return str(soup)


def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return ""
    # Decode HTML entities
    text = html.unescape(text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

