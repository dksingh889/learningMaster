"""
Import scraped blog posts into the database
"""
import json
from datetime import datetime
from app import app, db, Post, Category
from utils import process_blog_content
import re


def create_slug(text):
    """Create URL-friendly slug"""
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug[:100]


def parse_date(date_string):
    """Parse date string to datetime object"""
    try:
        # Try ISO format
        if 'T' in date_string:
            date_string = date_string.replace('Z', '+00:00')
            return datetime.fromisoformat(date_string)
        # Try other formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%d/%Y'
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except:
                continue
    except:
        pass
    return datetime.now()


def import_posts(json_file='blog_posts.json'):
    """Import posts from JSON file"""
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Load posts from JSON
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                posts_data = json.load(f)
        except FileNotFoundError:
            print(f"Error: {json_file} not found. Please run scraper.py first.")
            return
        
        print(f"Importing {len(posts_data)} posts...")
        
        imported = 0
        skipped = 0
        
        for post_data in posts_data:
            try:
                # Check if post already exists
                existing_post = Post.query.filter_by(slug=post_data.get('slug', '')).first()
                if existing_post:
                    print(f"Skipping duplicate: {post_data.get('title', 'Untitled')}")
                    skipped += 1
                    continue
                
                # Create or get categories
                categories = []
                for cat_name in post_data.get('categories', []):
                    if cat_name:
                        cat_slug = create_slug(cat_name)
                        category = Category.query.filter_by(slug=cat_slug).first()
                        if not category:
                            category = Category(name=cat_name, slug=cat_slug)
                            db.session.add(category)
                            db.session.flush()
                        categories.append(category)
                
                # Process content before saving
                raw_content = post_data.get('content', '')
                processed_content = process_blog_content(raw_content)
                
                # Create post
                post = Post(
                    title=post_data.get('title', 'Untitled'),
                    slug=post_data.get('slug', create_slug(post_data.get('title', 'untitled'))),
                    content=processed_content,
                    published_date=parse_date(post_data.get('published_date', datetime.now().isoformat())),
                    author=post_data.get('author', 'Admin'),
                    url=post_data.get('url', ''),
                    post_id=post_data.get('post_id', '')
                )
                
                # Add categories
                post.categories = categories
                
                db.session.add(post)
                db.session.commit()
                
                imported += 1
                print(f"Imported: {post.title}")
                
            except Exception as e:
                print(f"Error importing post {post_data.get('title', 'Unknown')}: {e}")
                db.session.rollback()
                skipped += 1
        
        print(f"\nImport complete!")
        print(f"Imported: {imported}")
        print(f"Skipped: {skipped}")


if __name__ == '__main__':
    import_posts()

