#!/usr/bin/env python3
"""
AI Post Generator
Generates SEO-optimized blog posts using AI for specific topics.
"""

import os
import requests
from typing import Dict, Optional
import json


def generate_ai_content_with_openai(topic: str, api_key: Optional[str] = None) -> Optional[Dict]:
    """
    Generate AI content using OpenAI API.
    
    Args:
        topic: The topic to generate content about
        api_key: OpenAI API key (if None, tries to get from env)
        
    Returns:
        Dictionary with generated content or None if failed
    """
    if api_key is None:
        api_key = os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        return None
    
    try:
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Create comprehensive prompt for SEO-optimized content
        prompt = f"""Create a comprehensive, SEO-optimized blog post about "{topic}".

SEO requirements (strict):
1. Title: 50-60 characters, include the primary keyword near the start.
2. Meta Description: 150-160 characters, include the primary keyword once.
3. Primary Keyword: Extract the main keyword from the topic.
4. Secondary Keywords: 3-5 related keywords; weave them naturally.
5. Content: Minimum 1200 words; include:
   - An engaging introduction that states the primary keyword.
   - At least 6 H2s; add H3s where useful.
   - Practical examples, steps, or checklists.
   - A clear conclusion with a call to action.
   - A dedicated FAQ section (at least 4 FAQs) with questions in H3 and concise answers.
6. Keyword usage: Keep primary keyword density around 1-2%; avoid stuffing.
7. Readability: Short paragraphs, bulleted lists where helpful.
8. Internal linking suggestions: Add a short unordered list at the end with 3 anchor texts and target slug ideas (no full URLs).
9. Excerpt: 150-200 characters summarizing the post.
10. Categories: Suggest 2-3 relevant categories.

Format your response as JSON with these keys:
- title
- meta_title
- meta_description
- primary_keyword
- secondary_keywords (comma-separated string)
- content (HTML formatted with <h2>, <h3>, <p>, <ul>, <li> tags; include the FAQ section and internal link suggestions list at the end)
- excerpt
- categories (comma-separated string)
- og_title
- og_description

Make the content informative, well-researched, and SEO-optimized."""
        
        data = {
            "model": "gpt-4o-mini",  # Use cost-effective model
            "messages": [
                {"role": "system", "content": "You are an expert SEO content writer. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            content_text = result['choices'][0]['message']['content']
            
            # Try to extract JSON from response
            try:
                # Remove markdown code blocks if present
                if '```json' in content_text:
                    content_text = content_text.split('```json')[1].split('```')[0]
                elif '```' in content_text:
                    content_text = content_text.split('```')[1].split('```')[0]
                
                generated_data = json.loads(content_text.strip())
                return generated_data
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract structured data
                return parse_text_response(content_text, topic)
        else:
            print(f"OpenAI API Error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error with OpenAI: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def generate_ai_content_with_anthropic(topic: str, api_key: Optional[str] = None) -> Optional[Dict]:
    """
    Generate AI content using Anthropic Claude API.
    
    Args:
        topic: The topic to generate content about
        api_key: Anthropic API key
        
    Returns:
        Dictionary with generated content or None if failed
    """
    if api_key is None:
        api_key = os.environ.get('ANTHROPIC_API_KEY')
    
    if not api_key:
        return None
    
    try:
        url = "https://api.anthropic.com/v1/messages"
        
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        prompt = f"""Create a comprehensive, SEO-optimized blog post about "{topic}".

SEO requirements (strict):
1. Title: 50-60 characters, include the primary keyword near the start.
2. Meta Description: 150-160 characters, include the primary keyword once.
3. Primary Keyword: Extract the main keyword from the topic.
4. Secondary Keywords: 3-5 related keywords; weave them naturally.
5. Content: Minimum 1200 words; include:
   - An engaging introduction that states the primary keyword.
   - At least 6 H2s; add H3s where useful.
   - Practical examples, steps, or checklists.
   - A clear conclusion with a call to action.
   - A dedicated FAQ section (at least 4 FAQs) with questions in H3 and concise answers.
6. Keyword usage: Keep primary keyword density around 1-2%; avoid stuffing.
7. Readability: Short paragraphs, bulleted lists where helpful.
8. Internal linking suggestions: Add a short unordered list at the end with 3 anchor texts and target slug ideas (no full URLs).
9. Excerpt: 150-200 characters summarizing the post.
10. Categories: Suggest 2-3 relevant categories.

Format your response as JSON with these keys:
- title
- meta_title
- meta_description
- primary_keyword
- secondary_keywords (comma-separated string)
- content (HTML formatted with <h2>, <h3>, <p>, <ul>, <li> tags; include the FAQ section and internal link suggestions list at the end)
- excerpt
- categories (comma-separated string)
- og_title
- og_description

Make the content informative, well-researched, and SEO-optimized."""
        
        data = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4000,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            content_text = result['content'][0]['text']
            
            try:
                if '```json' in content_text:
                    content_text = content_text.split('```json')[1].split('```')[0]
                elif '```' in content_text:
                    content_text = content_text.split('```')[1].split('```')[0]
                
                generated_data = json.loads(content_text.strip())
                return generated_data
            except json.JSONDecodeError:
                return parse_text_response(content_text, topic)
        else:
            print(f"Anthropic API Error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error with Anthropic: {str(e)}")
        return None


def parse_text_response(text: str, topic: str) -> Dict:
    """
    Parse text response and extract structured data.
    Fallback if JSON parsing fails.
    """
    import re
    
    # Extract title
    title_match = re.search(r'Title[:\s]+(.+?)(?:\n|$)', text, re.IGNORECASE)
    title = title_match.group(1).strip() if title_match else f"Complete Guide to {topic}"
    
    # Extract meta description
    meta_match = re.search(r'Meta Description[:\s]+(.+?)(?:\n|$)', text, re.IGNORECASE)
    meta_desc = meta_match.group(1).strip() if meta_match else f"Learn everything about {topic} with this comprehensive guide."
    
    # Extract keyword
    keyword_match = re.search(r'Primary Keyword[:\s]+(.+?)(?:\n|$)', text, re.IGNORECASE)
    keyword = keyword_match.group(1).strip() if keyword_match else topic.lower()
    
    # Extract content
    content_match = re.search(r'Content[:\s]+(.+)', text, re.IGNORECASE | re.DOTALL)
    content = content_match.group(1).strip() if content_match else f"<h2>Introduction to {topic}</h2><p>This is a comprehensive guide about {topic}.</p>"
    
    return {
        'title': title,
        'meta_title': title[:60],
        'meta_description': meta_desc[:160],
        'primary_keyword': keyword,
        'secondary_keywords': f"{keyword}, guide, tutorial, learn",
        'content': content,
        'excerpt': meta_desc[:200],
        'categories': 'Technology, Programming',
        'og_title': title,
        'og_description': meta_desc
    }


def generate_seo_post(topic: str, api_key: Optional[str] = None, provider: str = 'openai') -> Optional[Dict]:
    """
    Generate SEO-optimized blog post content for a specific topic.
    
    Args:
        topic: The topic to generate content about
        api_key: API key (optional, uses env var if not provided)
        provider: 'openai' or 'anthropic'
        
    Returns:
        Dictionary with all post fields including SEO data
    """
    print(f"🤖 Generating AI content for topic: '{topic}'...")
    
    if provider == 'openai':
        result = generate_ai_content_with_openai(topic, api_key)
    elif provider == 'anthropic':
        result = generate_ai_content_with_anthropic(topic, api_key)
    else:
        print(f"Unknown provider: {provider}")
        return None
    
    if result:
        print("✅ AI content generated successfully!")
        return result
    else:
        print("❌ Failed to generate AI content")
        return None

