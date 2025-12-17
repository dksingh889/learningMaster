"""
SEO utility functions for blog posts
"""
import re
from html import unescape
from collections import Counter
from bs4 import BeautifulSoup


def calculate_word_count(html_content):
    """Calculate word count from HTML content"""
    if not html_content:
        return 0
    # Remove HTML tags
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()
    # Remove extra whitespace
    words = text.split()
    return len(words)


def calculate_reading_time(html_content, words_per_minute=200):
    """Calculate reading time in minutes"""
    word_count = calculate_word_count(html_content)
    return max(1, round(word_count / words_per_minute))


def extract_headings(html_content):
    """Extract H2 and H3 headings from content"""
    if not html_content:
        return []
    soup = BeautifulSoup(html_content, 'html.parser')
    headings = []
    for tag in soup.find_all(['h2', 'h3']):
        headings.append({
            'level': tag.name,
            'text': tag.get_text().strip()
        })
    return headings


def calculate_keyword_density(content, keyword):
    """Calculate keyword density percentage"""
    if not content or not keyword:
        return 0.0
    
    # Remove HTML tags
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text().lower()
    keyword_lower = keyword.lower()
    
    # Count keyword occurrences
    word_count = len(text.split())
    keyword_count = text.count(keyword_lower)
    
    if word_count == 0:
        return 0.0
    
    density = (keyword_count / word_count) * 100
    return round(density, 2)


def generate_meta_description(content, max_length=155, keyword=None):
    """Generate SEO-optimized meta description from content"""
    if not content:
        return ""
    
    # Remove HTML tags
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text().strip()
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # If keyword provided, try to include it near the beginning
    if keyword and keyword.lower() in text.lower():
        # Find keyword position
        keyword_pos = text.lower().find(keyword.lower())
        if keyword_pos < 100:  # If keyword is in first 100 chars
            # Start from keyword position
            start = max(0, keyword_pos - 20)
            text = text[start:]
    
    # Truncate to max length
    if len(text) <= max_length:
        return text
    
    # Truncate at word boundary, ensure it ends with punctuation or add ellipsis
    truncated = text[:max_length].rsplit(' ', 1)[0]
    if not truncated.endswith(('.', '!', '?')):
        truncated += '...'
    return truncated


def generate_meta_title(title, keyword=None, max_length=60):
    """Generate SEO-optimized meta title from post title"""
    if not title:
        return ""
    
    # If keyword provided and not in title, add it
    if keyword and keyword.lower() not in title.lower():
        # Try to add keyword in a natural way
        if len(title) + len(keyword) + 5 <= max_length:
            title = f"{title} - {keyword} Guide"
        elif len(title) + len(keyword) + 3 <= max_length:
            title = f"{title} - {keyword}"
    
    # Truncate if too long
    if len(title) > max_length:
        title = title[:max_length].rsplit(' ', 1)[0]
    
    return title


def extract_primary_keyword(title, content=None):
    """Extract primary keyword from title or content"""
    if not title:
        return ""
    
    # Remove common words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'what', 'which', 'who', 'whom', 'whose', 'where', 'when', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now'}
    
    # Extract words from title
    words = re.findall(r'\b[a-zA-Z]{3,}\b', title.lower())
    keywords = [w for w in words if w not in stop_words]
    
    # Return most significant word (longest or first)
    if keywords:
        # Prefer longer words
        keywords.sort(key=len, reverse=True)
        return keywords[0].title()
    
    # Fallback: use first significant word from title
    words = title.split()
    for word in words:
        clean_word = re.sub(r'[^\w]', '', word)
        if len(clean_word) >= 3 and clean_word.lower() not in stop_words:
            return clean_word
    
    return ""


def generate_secondary_keywords(primary_keyword, content=None, count=5):
    """Generate secondary keywords based on primary keyword and content"""
    if not primary_keyword:
        return ""
    
    # Common secondary keyword patterns
    patterns = [
        f"{primary_keyword} tutorial",
        f"{primary_keyword} guide",
        f"{primary_keyword} tips",
        f"learn {primary_keyword}",
        f"{primary_keyword} best practices",
        f"{primary_keyword} examples",
        f"how to {primary_keyword}",
        f"{primary_keyword} for beginners"
    ]
    
    # If content provided, try to extract more relevant keywords
    if content:
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text().lower()
        
        # Find words that appear frequently with primary keyword
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text)
        word_freq = Counter(words)
        
        # Get top words that aren't the primary keyword
        top_words = [w for w, _ in word_freq.most_common(10) 
                    if w != primary_keyword.lower() and len(w) >= 4]
        
        if top_words:
            # Create combinations
            for word in top_words[:3]:
                patterns.append(f"{primary_keyword} {word}")
                patterns.append(f"{word} {primary_keyword}")
    
    # Return comma-separated list
    return ', '.join(patterns[:count])


def generate_og_tags(title, description, keyword=None):
    """Generate Open Graph tags from title and description"""
    og_title = title[:100] if len(title) <= 100 else title[:97] + '...'
    
    if description:
        og_description = description[:300] if len(description) <= 300 else description[:297] + '...'
    else:
        og_description = title[:300] if len(title) <= 300 else title[:297] + '...'
    
    return {
        'og_title': og_title,
        'og_description': og_description
    }


def generate_twitter_tags(title, description, keyword=None):
    """Generate Twitter Card tags from title and description"""
    twitter_title = title[:70] if len(title) <= 70 else title[:67] + '...'
    
    if description:
        twitter_description = description[:200] if len(description) <= 200 else description[:197] + '...'
    else:
        twitter_description = title[:200] if len(title) <= 200 else title[:197] + '...'
    
    return {
        'twitter_title': twitter_title,
        'twitter_description': twitter_description
    }


def suggest_headings(content, keyword):
    """Suggest headings based on content and keyword"""
    if not content or not keyword:
        return []
    
    suggestions = []
    
    # Extract existing headings
    existing_headings = extract_headings(content)
    
    # Common heading patterns with keyword
    patterns = [
        f"What is {keyword}?",
        f"How to {keyword}",
        f"{keyword} Guide",
        f"{keyword} Tutorial",
        f"{keyword} Best Practices",
        f"{keyword} Examples",
        f"Benefits of {keyword}",
        f"{keyword} Tips",
    ]
    
    # Filter out patterns that already exist
    existing_texts = [h['text'].lower() for h in existing_headings]
    for pattern in patterns:
        if pattern.lower() not in existing_texts:
            suggestions.append({
                'text': pattern,
                'level': 'h2',
                'reason': 'Common SEO pattern'
            })
    
    return suggestions[:5]  # Return top 5 suggestions


def suggest_faqs(content, keyword):
    """Suggest FAQ questions based on content and keyword"""
    if not content or not keyword:
        return []
    
    faqs = []
    
    # Common FAQ patterns
    patterns = [
        f"What is {keyword}?",
        f"How does {keyword} work?",
        f"Why use {keyword}?",
        f"When should I use {keyword}?",
        f"Is {keyword} worth it?",
        f"What are the benefits of {keyword}?",
        f"How to get started with {keyword}?",
    ]
    
    for pattern in patterns:
        faqs.append({
            'question': pattern,
            'answer': f"Answer about {keyword} based on your content..."
        })
    
    return faqs[:5]  # Return top 5 FAQs


def calculate_seo_score(post, seo_data):
    """Calculate overall SEO score (0-100)"""
    score = 0
    max_score = 100
    
    # Title (10 points)
    if post.title and len(post.title) >= 30 and len(post.title) <= 60:
        score += 10
    elif post.title:
        score += 5
    
    # Meta description (10 points)
    if seo_data.get('meta_description'):
        desc = seo_data['meta_description']
        if len(desc) >= 120 and len(desc) <= 155:
            score += 10
        elif desc:
            score += 5
    
    # Primary keyword (15 points)
    if seo_data.get('primary_keyword'):
        score += 15
    
    # Content length (15 points)
    word_count = post.word_count
    if word_count >= 1000:
        score += 15
    elif word_count >= 500:
        score += 10
    elif word_count >= 300:
        score += 5
    
    # Headings (10 points)
    headings = extract_headings(post.content)
    if len(headings) >= 3:
        score += 10
    elif len(headings) >= 1:
        score += 5
    
    # Images with ALT text (10 points)
    if post.featured_image:
        score += 5
    # Additional images would add more points
    
    # Keyword density (10 points)
    if seo_data.get('keyword_density'):
        density = seo_data['keyword_density']
        if 1.0 <= density <= 2.5:  # Optimal range
            score += 10
        elif 0.5 <= density <= 3.0:
            score += 5
    
    # URL slug (5 points)
    if post.slug and len(post.slug) <= 60:
        score += 5
    
    # Excerpt (5 points)
    if post.excerpt:
        score += 5
    
    # OG tags (10 points)
    if seo_data.get('og_title') and seo_data.get('og_description'):
        score += 10
    elif seo_data.get('og_title') or seo_data.get('og_description'):
        score += 5
    
    return min(score, max_score)


def validate_seo_fields(seo_data):
    """Validate SEO fields and return errors"""
    errors = []
    warnings = []
    
    # Required fields
    if not seo_data.get('primary_keyword'):
        errors.append("Primary keyword is required")
    
    if not seo_data.get('meta_title'):
        errors.append("Meta title is required")
    elif len(seo_data['meta_title']) > 60:
        warnings.append("Meta title should be 60 characters or less (currently {})".format(len(seo_data['meta_title'])))
    
    if not seo_data.get('meta_description'):
        errors.append("Meta description is required")
    elif len(seo_data['meta_description']) > 155:
        warnings.append("Meta description should be 155 characters or less (currently {})".format(len(seo_data['meta_description'])))
    
    # Recommended fields
    if not seo_data.get('og_title'):
        warnings.append("OG title is recommended for social sharing")
    
    if not seo_data.get('og_description'):
        warnings.append("OG description is recommended for social sharing")
    
    if not seo_data.get('og_image'):
        warnings.append("OG image is recommended for social sharing")
    
    return errors, warnings


def generate_internal_link_suggestions(post_title, all_posts):
    """Suggest internal links based on post title and existing posts"""
    suggestions = []
    title_words = set(post_title.lower().split())
    
    for post in all_posts:
        if post.id == getattr(post, 'id', None):  # Skip current post
            continue
        
        post_words = set(post.title.lower().split())
        # Calculate similarity
        common_words = title_words.intersection(post_words)
        if len(common_words) >= 2:  # At least 2 common words
            suggestions.append({
                'post': post,
                'relevance': len(common_words),
                'reason': f"Shares {len(common_words)} keywords"
            })
    
    # Sort by relevance
    suggestions.sort(key=lambda x: x['relevance'], reverse=True)
    return suggestions[:5]  # Return top 5 suggestions

