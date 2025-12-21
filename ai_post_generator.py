#!/usr/bin/env python3
"""
AI Post Generator
Generates SEO-optimized blog posts using AI with keyword research.
"""

import os
import requests
from typing import Dict, Optional, List
import json
import re


def research_keywords_with_openai(topic: str, api_key: Optional[str] = None) -> Optional[Dict]:
    """
    Research and suggest SEO keywords for a topic using OpenAI.
    
    Returns:
        Dictionary with primary_keyword, secondary_keywords, and keyword_insights
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
        
        keyword_prompt = f"""Research and suggest SEO keywords for the topic: "{topic}"

Perform keyword research and provide:
1. Primary keyword (most relevant, high search volume)
2. 5-7 secondary keywords (related, long-tail, semantic variations)
3. Keyword insights (search intent, competition level, content angle)

Format your response as JSON with these keys:
- primary_keyword: string
- secondary_keywords: array of strings (5-7 keywords)
- keyword_insights: string (brief analysis of search intent and content angle)

Focus on keywords that are:
- Relevant to the topic
- Have good search volume
- Match user search intent
- Are suitable for long-form content (900-1000 words)"""
        
        data = {
            "model": "gpt-4o",  # Use best model for research
            "messages": [
                {"role": "system", "content": "You are an expert SEO keyword researcher. Always respond with valid JSON only."},
                {"role": "user", "content": keyword_prompt}
            ],
            "temperature": 0.3,  # Lower temperature for more focused research
            "max_tokens": 1000
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content_text = result['choices'][0]['message']['content']
            
            # Extract JSON
            if '```json' in content_text:
                content_text = content_text.split('```json')[1].split('```')[0]
            elif '```' in content_text:
                content_text = content_text.split('```')[1].split('```')[0]
            
            keyword_data = json.loads(content_text.strip())
            return keyword_data
        else:
            print(f"Keyword research error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error in keyword research: {str(e)}")
        return None


def research_keywords_with_anthropic(topic: str, api_key: Optional[str] = None) -> Optional[Dict]:
    """
    Research and suggest SEO keywords for a topic using Anthropic Claude.
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
        
        keyword_prompt = f"""Research and suggest SEO keywords for the topic: "{topic}"

Perform keyword research and provide:
1. Primary keyword (most relevant, high search volume)
2. 5-7 secondary keywords (related, long-tail, semantic variations)
3. Keyword insights (search intent, competition level, content angle)

Format your response as JSON with these keys:
- primary_keyword: string
- secondary_keywords: array of strings (5-7 keywords)
- keyword_insights: string (brief analysis of search intent and content angle)

Focus on keywords that are:
- Relevant to the topic
- Have good search volume
- Match user search intent
- Are suitable for long-form content (900-1000 words)"""
        
        data = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1000,
            "temperature": 0.3,
            "messages": [
                {"role": "user", "content": keyword_prompt}
            ]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content_text = result['content'][0]['text']
            
            if '```json' in content_text:
                content_text = content_text.split('```json')[1].split('```')[0]
            elif '```' in content_text:
                content_text = content_text.split('```')[1].split('```')[0]
            
            keyword_data = json.loads(content_text.strip())
            return keyword_data
        else:
            print(f"Keyword research error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error in keyword research: {str(e)}")
        return None


def generate_ai_content_with_openai(topic: str, keyword_data: Optional[Dict] = None, api_key: Optional[str] = None, custom_prompt: Optional[str] = None) -> Optional[Dict]:
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
        
        # Prepare keyword information for prompt
        primary_keyword = keyword_data.get('primary_keyword', topic) if keyword_data else topic
        secondary_keywords = keyword_data.get('secondary_keywords', []) if keyword_data else []
        keyword_insights = keyword_data.get('keyword_insights', '') if keyword_data else ''
        
        secondary_keywords_str = ', '.join(secondary_keywords) if isinstance(secondary_keywords, list) else (secondary_keywords if isinstance(secondary_keywords, str) else '')
        
        # Create comprehensive prompt for SEO-optimized, human-like content
        prompt = f"""Create a comprehensive, SEO-optimized blog post about "{topic}" that reads like it was written by an experienced human expert, not AI.

KEYWORD RESEARCH DATA:
- Primary Keyword: {primary_keyword}
- Secondary Keywords: {secondary_keywords_str}
- Keyword Insights: {keyword_insights}

WRITING STYLE (CRITICAL - TO SOUND HUMAN):
1. Vary sentence structure: Mix short punchy sentences with longer, more complex ones. Avoid repetitive patterns.
2. Use natural transitions: Use varied transition words (however, meanwhile, furthermore, on the other hand, in contrast, etc.) - don't always start paragraphs the same way.
3. Add personality: Include occasional personal opinions, real-world examples, and conversational asides. Use "I've found that..." or "In my experience..." occasionally.
4. Natural language patterns: Use contractions (don't, can't, it's) naturally. Include occasional colloquialisms and varied vocabulary.
5. Avoid AI patterns: Don't use phrases like "In conclusion", "It's important to note", "Furthermore" at the start of every paragraph. Vary your approach.
6. Real examples: Include specific, concrete examples rather than generic ones. Use real scenarios and practical applications.
7. Imperfect perfection: Occasionally use slightly informal language, varied punctuation, and natural flow - not overly polished.

SEO requirements (STRICT - MUST FOLLOW):
1. Title: 50-60 characters, MUST include the primary keyword "{primary_keyword}" near the start. Make it compelling and click-worthy.
2. Meta Description: 150-160 characters, MUST include the primary keyword once naturally. Make it engaging and action-oriented.
3. Content: EXACTLY 900-1000 words (count carefully - this is critical). Include:
   - An engaging, hook-driven introduction (100-150 words) that naturally states the primary keyword and draws readers in.
   - At least 5-6 H2 headings with varied phrasing; add H3s where useful for structure.
   - Practical, real-world examples, step-by-step guides, checklists, or case studies with specific details.
   - A clear, actionable conclusion (100-150 words) with a natural call to action that doesn't sound robotic.
   - A dedicated FAQ section (at least 4-5 FAQs) with questions in H3 and concise, helpful answers.
4. Keyword usage: 
   - Use primary keyword "{primary_keyword}" naturally 8-12 times throughout (1-1.5% density) - vary placement (beginning, middle, end of sentences).
   - Weave in secondary keywords: {secondary_keywords_str} naturally throughout the content in varied contexts.
   - Avoid keyword stuffing - make it read naturally. Use synonyms and related terms.
   - Include LSI (Latent Semantic Indexing) keywords naturally.
5. Readability: 
   - Vary paragraph length (some 2-3 sentences, some 4-5 sentences).
   - Use bulleted/numbered lists where helpful, but not excessively.
   - Break up text with subheadings, examples, and visual breaks.
6. Internal linking suggestions: Add a short unordered list at the end with 3 anchor texts and target slug ideas (no full URLs).
7. Excerpt: 150-200 characters summarizing the post, include primary keyword naturally.
8. Categories: Suggest 2-3 relevant categories.

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

CODE BLOCK FORMATTING (CRITICAL):
- All code examples MUST use this exact format: <pre><code class="language-python">your code here</code></pre>
- For Python code, use: class="language-python"
- For JavaScript code, use: class="language-javascript"
- For Bash/Shell code, use: class="language-bash"
- For other languages, use the appropriate language class (e.g., language-html, language-css, language-sql)
- NEVER use plain <pre> or <code> tags without the language class
- NEVER use markdown code blocks (```) in the HTML content

CRITICAL: The content MUST be exactly 900-1000 words. Count the words in your content before responding. Make the content informative, well-researched, and SEO-optimized."""
        
        data = {
            "model": "gpt-4o",  # Use best model for quality content
            "messages": [
                {"role": "system", "content": "You are an experienced human blogger and SEO expert with years of writing experience. You write naturally, conversationally, and with personality - never sounding like AI. Your content is highly optimized for SEO but reads like a knowledgeable expert sharing insights. Always respond with valid JSON only. You MUST ensure content is exactly 900-1000 words and sounds completely human-written."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.85,  # Higher temperature for more natural, varied writing
            "max_tokens": 8000  # Increased for longer content
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


def generate_ai_content_with_anthropic(topic: str, keyword_data: Optional[Dict] = None, api_key: Optional[str] = None, custom_prompt: Optional[str] = None) -> Optional[Dict]:
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
        
        # Prepare keyword information for prompt
        primary_keyword = keyword_data.get('primary_keyword', topic) if keyword_data else topic
        secondary_keywords = keyword_data.get('secondary_keywords', []) if keyword_data else []
        keyword_insights = keyword_data.get('keyword_insights', '') if keyword_data else ''
        
        secondary_keywords_str = ', '.join(secondary_keywords) if isinstance(secondary_keywords, list) else (secondary_keywords if isinstance(secondary_keywords, str) else '')
        
        prompt = f"""Create a comprehensive, SEO-optimized blog post about "{topic}" that reads like it was written by an experienced human expert, not AI.

KEYWORD RESEARCH DATA:
- Primary Keyword: {primary_keyword}
- Secondary Keywords: {secondary_keywords_str}
- Keyword Insights: {keyword_insights}

WRITING STYLE (CRITICAL - TO SOUND HUMAN):
1. Vary sentence structure: Mix short punchy sentences with longer, more complex ones. Avoid repetitive patterns.
2. Use natural transitions: Use varied transition words (however, meanwhile, furthermore, on the other hand, in contrast, etc.) - don't always start paragraphs the same way.
3. Add personality: Include occasional personal opinions, real-world examples, and conversational asides. Use "I've found that..." or "In my experience..." occasionally.
4. Natural language patterns: Use contractions (don't, can't, it's) naturally. Include occasional colloquialisms and varied vocabulary.
5. Avoid AI patterns: Don't use phrases like "In conclusion", "It's important to note", "Furthermore" at the start of every paragraph. Vary your approach.
6. Real examples: Include specific, concrete examples rather than generic ones. Use real scenarios and practical applications.
7. Imperfect perfection: Occasionally use slightly informal language, varied punctuation, and natural flow - not overly polished.

SEO requirements (STRICT - MUST FOLLOW):
1. Title: 50-60 characters, MUST include the primary keyword "{primary_keyword}" near the start. Make it compelling and click-worthy.
2. Meta Description: 150-160 characters, MUST include the primary keyword once naturally. Make it engaging and action-oriented.
3. Content: EXACTLY 900-1000 words (count carefully - this is critical). Include:
   - An engaging, hook-driven introduction (100-150 words) that naturally states the primary keyword and draws readers in.
   - At least 5-6 H2 headings with varied phrasing; add H3s where useful for structure.
   - Practical, real-world examples, step-by-step guides, checklists, or case studies with specific details.
   - A clear, actionable conclusion (100-150 words) with a natural call to action that doesn't sound robotic.
   - A dedicated FAQ section (at least 4-5 FAQs) with questions in H3 and concise, helpful answers.
4. Keyword usage: 
   - Use primary keyword "{primary_keyword}" naturally 8-12 times throughout (1-1.5% density) - vary placement (beginning, middle, end of sentences).
   - Weave in secondary keywords: {secondary_keywords_str} naturally throughout the content in varied contexts.
   - Avoid keyword stuffing - make it read naturally. Use synonyms and related terms.
   - Include LSI (Latent Semantic Indexing) keywords naturally.
5. Readability: 
   - Vary paragraph length (some 2-3 sentences, some 4-5 sentences).
   - Use bulleted/numbered lists where helpful, but not excessively.
   - Break up text with subheadings, examples, and visual breaks.
6. Internal linking suggestions: Add a short unordered list at the end with 3 anchor texts and target slug ideas (no full URLs).
7. Excerpt: 150-200 characters summarizing the post, include primary keyword naturally.
8. Categories: Suggest 2-3 relevant categories.

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

CODE BLOCK FORMATTING (CRITICAL):
- All code examples MUST use this exact format: <pre><code class="language-python">your code here</code></pre>
- For Python code, use: class="language-python"
- For JavaScript code, use: class="language-javascript"
- For Bash/Shell code, use: class="language-bash"
- For other languages, use the appropriate language class (e.g., language-html, language-css, language-sql)
- NEVER use plain <pre> or <code> tags without the language class
- NEVER use markdown code blocks (```) in the HTML content

CRITICAL: The content MUST be exactly 900-1000 words. Count the words in your content before responding. Make the content informative, well-researched, and SEO-optimized."""

        # Add user's custom prompt/instructions if provided
        if custom_prompt and custom_prompt.strip():
            prompt += f"""

ADDITIONAL USER INSTRUCTIONS:
{custom_prompt.strip()}

Please incorporate these additional instructions while following all the requirements above."""
        
        data = {
            "model": "claude-3-5-sonnet-20241022",  # Best Claude model
            "max_tokens": 8000,  # Increased for longer content
            "temperature": 0.85,  # Higher temperature for more natural, varied writing
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


def generate_seo_post(topic: str, api_key: Optional[str] = None, provider: str = 'openai', custom_prompt: Optional[str] = None) -> Optional[Dict]:
    """
    Generate SEO-optimized blog post content with keyword research.
    
    Args:
        topic: The topic to generate content about
        api_key: API key (optional, uses env var if not provided)
        provider: 'openai' or 'anthropic'
        custom_prompt: Optional custom instructions from user to be included in the prompt
        
    Returns:
        Dictionary with all post fields including SEO data
    """
    print(f"🔍 Starting keyword research for topic: '{topic}'...")
    
    # Step 1: Research keywords
    keyword_data = None
    if provider == 'openai':
        keyword_data = research_keywords_with_openai(topic, api_key)
    elif provider == 'anthropic':
        keyword_data = research_keywords_with_anthropic(topic, api_key)
    
    if keyword_data:
        primary = keyword_data.get('primary_keyword', topic)
        secondary = keyword_data.get('secondary_keywords', [])
        print(f"✅ Keyword research complete!")
        print(f"   Primary: {primary}")
        print(f"   Secondary: {', '.join(secondary) if isinstance(secondary, list) else secondary}")
    else:
        print("⚠️  Keyword research failed, proceeding with topic-based keywords")
        keyword_data = {
            'primary_keyword': topic,
            'secondary_keywords': [],
            'keyword_insights': ''
        }
    
    # Step 2: Generate content with researched keywords
    print(f"🤖 Generating AI content (900-1000 words) for topic: '{topic}'...")
    if custom_prompt:
        print(f"📝 Including custom user instructions in prompt...")
    
    if provider == 'openai':
        result = generate_ai_content_with_openai(topic, keyword_data, api_key, custom_prompt)
    elif provider == 'anthropic':
        result = generate_ai_content_with_anthropic(topic, keyword_data, api_key, custom_prompt)
    else:
        print(f"Unknown provider: {provider}")
        return None
    
    if result:
        # Verify word count
        content = result.get('content', '')
        # Remove HTML tags for word count
        text_content = re.sub(r'<[^>]+>', '', content)
        word_count = len(text_content.split())
        
        print(f"✅ AI content generated successfully!")
        print(f"   Word count: {word_count} words")
        
        if word_count < 900:
            print(f"⚠️  Warning: Content is {word_count} words, below target of 900-1000 words")
        elif word_count > 1000:
            print(f"⚠️  Warning: Content is {word_count} words, above target of 900-1000 words")
        
        # Ensure keyword data is included in result
        if keyword_data and 'primary_keyword' in keyword_data:
            result['primary_keyword'] = keyword_data['primary_keyword']
            if 'secondary_keywords' in keyword_data:
                sec_keywords = keyword_data['secondary_keywords']
                if isinstance(sec_keywords, list):
                    result['secondary_keywords'] = ', '.join(sec_keywords)
                else:
                    result['secondary_keywords'] = sec_keywords
        
        return result
    else:
        print("❌ Failed to generate AI content")
        return None

