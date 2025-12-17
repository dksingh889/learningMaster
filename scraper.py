"""
Web scraper to fetch all blog posts from phphelpclub.blogspot.com
"""
import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
import time


class BloggerScraper:
    def __init__(self, blog_url):
        self.blog_url = blog_url
        self.posts = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_blog_feed_url(self):
        """Get the Blogger Atom feed URL"""
        # Extract blog name from URL
        # Supports both phphelpclub.blogspot.com and blogspot.com/phphelpclub formats
        parsed = urlparse(self.blog_url)
        domain = parsed.netloc
        
        if 'blogspot.com' in domain:
            blog_name = domain.split('.')[0]
        else:
            # Try to extract from path
            path_parts = [p for p in parsed.path.split('/') if p]
            blog_name = path_parts[0] if path_parts else 'phphelpclub'
        
        return f"https://{blog_name}.blogspot.com/feeds/posts/default?max-results=500"
    
    def scrape_from_feed(self):
        """Scrape posts from Blogger Atom feed"""
        feed_url = self.get_blog_feed_url()
        print(f"Fetching feed from: {feed_url}")
        
        try:
            response = self.session.get(feed_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'xml')
            entries = soup.find_all('entry')
            
            print(f"Found {len(entries)} posts in feed")
            
            for entry in entries:
                post = self.parse_entry(entry)
                if post:
                    self.posts.append(post)
                    print(f"Scraped: {post['title']}")
            
            return self.posts
        except Exception as e:
            print(f"Error fetching feed: {e}")
            return []
    
    def parse_entry(self, entry):
        """Parse a single entry from the Atom feed"""
        try:
            title = entry.find('title')
            title_text = title.text if title else "Untitled"
            
            content = entry.find('content')
            content_html = content.text if content else ""
            
            published = entry.find('published')
            published_date = published.text if published else datetime.now().isoformat()
            
            link = entry.find('link', {'rel': 'alternate'})
            post_url = link.get('href') if link else ""
            
            author = entry.find('author')
            author_name = author.find('name').text if author and author.find('name') else "Unknown"
            
            # Extract categories/tags
            categories = [cat.get('term') for cat in entry.find_all('category')]
            
            # Try to get post ID
            post_id = entry.find('id')
            post_id_text = post_id.text if post_id else ""
            
            return {
                'title': title_text,
                'content': content_html,
                'published_date': published_date,
                'url': post_url,
                'author': author_name,
                'categories': categories,
                'post_id': post_id_text,
                'slug': self.create_slug(title_text)
            }
        except Exception as e:
            print(f"Error parsing entry: {e}")
            return None
    
    def scrape_from_html(self):
        """Alternative method: scrape directly from HTML pages"""
        print(f"Scraping from HTML: {self.blog_url}")
        
        try:
            response = self.session.get(self.blog_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all blog post links
            post_links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if '/p/' in href or '/search/label/' in href:
                    full_url = urljoin(self.blog_url, href)
                    if full_url not in post_links:
                        post_links.append(full_url)
            
            print(f"Found {len(post_links)} post links")
            
            # Scrape each post
            for post_url in post_links:
                if '/p/' in post_url:  # Individual post
                    post = self.scrape_single_post(post_url)
                    if post:
                        self.posts.append(post)
                        print(f"Scraped: {post['title']}")
                        time.sleep(1)  # Be respectful with requests
            
            return self.posts
        except Exception as e:
            print(f"Error scraping HTML: {e}")
            return []
    
    def scrape_single_post(self, post_url):
        """Scrape a single blog post page"""
        try:
            response = self.session.get(post_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find title
            title_elem = soup.find('h1', class_='post-title') or soup.find('h1')
            title = title_elem.text.strip() if title_elem else "Untitled"
            
            # Find content
            content_elem = soup.find('div', class_='post-body') or soup.find('div', class_='post-content')
            if not content_elem:
                content_elem = soup.find('article') or soup.find('div', {'itemprop': 'articleBody'})
            
            content = str(content_elem) if content_elem else ""
            
            # Find published date
            date_elem = soup.find('time') or soup.find('span', class_='published')
            published_date = datetime.now().isoformat()
            if date_elem:
                date_text = date_elem.get('datetime') or date_elem.text
                try:
                    published_date = datetime.fromisoformat(date_text.replace('Z', '+00:00')).isoformat()
                except:
                    pass
            
            # Find author
            author_elem = soup.find('span', class_='author') or soup.find('a', class_='g-profile')
            author = author_elem.text.strip() if author_elem else "Unknown"
            
            # Find categories/tags
            categories = []
            tag_elems = soup.find_all('a', class_='label-link') or soup.find_all('a', rel='tag')
            for tag in tag_elems:
                categories.append(tag.text.strip())
            
            return {
                'title': title,
                'content': content,
                'published_date': published_date,
                'url': post_url,
                'author': author,
                'categories': categories,
                'post_id': post_url.split('/')[-1],
                'slug': self.create_slug(title)
            }
        except Exception as e:
            print(f"Error scraping post {post_url}: {e}")
            return None
    
    def create_slug(self, title):
        """Create URL-friendly slug from title"""
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug[:100]
    
    def save_to_json(self, filename='blog_posts.json'):
        """Save scraped posts to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.posts, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(self.posts)} posts to {filename}")
    
    def scrape_all(self):
        """Main method to scrape all posts"""
        print("Starting blog scrape...")
        
        # Try feed first (more reliable)
        posts = self.scrape_from_feed()
        
        # If feed doesn't work or returns few posts, try HTML scraping
        if len(posts) < 5:
            print("Feed returned few posts, trying HTML scraping...")
            posts = self.scrape_from_html()
        
        self.save_to_json()
        return self.posts


if __name__ == '__main__':
    scraper = BloggerScraper('https://phphelpclub.blogspot.com/')
    posts = scraper.scrape_all()
    print(f"\nTotal posts scraped: {len(posts)}")

