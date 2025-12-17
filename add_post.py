"""
Script to add a new blog post via command line
Usage: python add_post.py
"""
import sys
from datetime import datetime
from app import app, db, Post, Category
from utils import process_blog_content
import re


def create_slug(text):
    """Create URL-friendly slug"""
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug[:100]


def add_post_interactive():
    """Interactive function to add a new post"""
    with app.app_context():
        print("\n" + "="*60)
        print("Add New Blog Post")
        print("="*60 + "\n")
        
        # Get title
        title = input("Enter post title: ").strip()
        if not title:
            print("Error: Title is required!")
            return
        
        # Check if slug already exists
        slug = create_slug(title)
        existing = Post.query.filter_by(slug=slug).first()
        if existing:
            print(f"Warning: A post with slug '{slug}' already exists!")
            use_existing = input("Do you want to use a different slug? (y/n): ").strip().lower()
            if use_existing == 'y':
                slug = input("Enter custom slug: ").strip()
            else:
                print("Cancelled.")
                return
        
        # Get content
        print("\nEnter post content (HTML supported).")
        print("Type 'END' on a new line when finished:")
        content_lines = []
        while True:
            line = input()
            if line.strip() == 'END':
                break
            content_lines.append(line)
        
        content = '\n'.join(content_lines)
        if not content:
            print("Error: Content is required!")
            return
        
        # Process content
        processed_content = process_blog_content(content)
        
        # Get author
        author = input("\nEnter author name (default: Admin): ").strip() or 'Admin'
        
        # Get categories
        print("\nEnter categories (comma-separated, e.g., Python, Web Development):")
        categories_input = input().strip()
        categories = []
        if categories_input:
            category_names = [cat.strip() for cat in categories_input.split(',')]
            for cat_name in category_names:
                if cat_name:
                    cat_slug = create_slug(cat_name)
                    category = Category.query.filter_by(slug=cat_slug).first()
                    if not category:
                        category = Category(name=cat_name, slug=cat_slug)
                        db.session.add(category)
                        db.session.flush()
                    categories.append(category)
        
        # Get published date
        date_input = input("\nEnter published date (YYYY-MM-DD) or press Enter for today: ").strip()
        if date_input:
            try:
                published_date = datetime.strptime(date_input, '%Y-%m-%d')
            except ValueError:
                print("Invalid date format. Using today's date.")
                published_date = datetime.now()
        else:
            published_date = datetime.now()
        
        # Create post
        post = Post(
            title=title,
            slug=slug,
            content=processed_content,
            published_date=published_date,
            author=author
        )
        
        # Add categories
        post.categories = categories
        
        # Save to database
        try:
            db.session.add(post)
            db.session.commit()
            print(f"\n✅ Successfully added post: {title}")
            print(f"   Slug: {slug}")
            print(f"   URL: /post/{slug}")
        except Exception as e:
            print(f"\n❌ Error adding post: {e}")
            db.session.rollback()


def add_post_from_file(title, content_file, author='Admin', categories=None, published_date=None):
    """Add a post from a file"""
    with app.app_context():
        # Read content from file
        try:
            with open(content_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: File '{content_file}' not found!")
            return False
        
        slug = create_slug(title)
        
        # Check if slug exists
        existing = Post.query.filter_by(slug=slug).first()
        if existing:
            print(f"Error: Post with slug '{slug}' already exists!")
            return False
        
        # Process content
        processed_content = process_blog_content(content)
        
        # Handle categories
        category_objects = []
        if categories:
            for cat_name in categories:
                cat_slug = create_slug(cat_name)
                category = Category.query.filter_by(slug=cat_slug).first()
                if not category:
                    category = Category(name=cat_name, slug=cat_slug)
                    db.session.add(category)
                    db.session.flush()
                category_objects.append(category)
        
        # Create post
        post = Post(
            title=title,
            slug=slug,
            content=processed_content,
            published_date=published_date or datetime.now(),
            author=author
        )
        
        post.categories = category_objects
        
        try:
            db.session.add(post)
            db.session.commit()
            print(f"✅ Successfully added post: {title}")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            return False


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Command line mode
        if sys.argv[1] == '--file' and len(sys.argv) >= 4:
            title = sys.argv[2]
            content_file = sys.argv[3]
            author = sys.argv[4] if len(sys.argv) > 4 else 'Admin'
            add_post_from_file(title, content_file, author)
        else:
            print("Usage:")
            print("  Interactive: python add_post.py")
            print("  From file:   python add_post.py --file 'Title' content.html 'Author'")
    else:
        # Interactive mode
        add_post_interactive()

