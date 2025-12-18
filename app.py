"""
Flask blog application - Google AdSense Ready
"""
from flask import Flask, render_template, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json
from utils import process_blog_content
from urllib.parse import urljoin, quote_plus

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, skip

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

# Database configuration
# For MySQL: mysql+pymysql://username:password@host:port/database_name
# For SQLite (default): sqlite:///blog.db
DATABASE_URL = os.environ.get('DATABASE_URL', None)

if DATABASE_URL:
    # Use provided DATABASE_URL (MySQL, PostgreSQL, etc.)
    # Validate and fix the connection string if needed
    try:
        # Parse and properly encode the connection string
        if DATABASE_URL.startswith('mysql+pymysql://'):
            # Use urllib.parse.urlparse for proper parsing
            from urllib.parse import urlparse, urlunparse, quote
            
            parsed = urlparse(DATABASE_URL)
            
            # Check if parsing was successful
            if parsed.netloc and '@' in parsed.netloc:
                # Split username:password@host
                auth_and_host = parsed.netloc
                if '@' in auth_and_host:
                    auth_part, host_part = auth_and_host.rsplit('@', 1)  # Use rsplit to handle @ in password
                    if ':' in auth_part:
                        user, password = auth_part.split(':', 1)  # Split only on first :
                        # URL encode password to handle special characters
                        encoded_password = quote(password, safe='')
                        # Reconstruct the URL
                        new_netloc = f"{user}:{encoded_password}@{host_part}"
                        DATABASE_URL = urlunparse((
                            parsed.scheme,
                            new_netloc,
                            parsed.path,
                            parsed.params,
                            parsed.query,
                            parsed.fragment
                        ))
                        print(f"✅ Parsed MySQL connection string for user: {user}")
                    else:
                        print(f"⚠️  Warning: No password found in connection string")
                else:
                    print(f"⚠️  Warning: Invalid connection string format (missing @)")
            else:
                print(f"⚠️  Warning: Could not parse connection string properly")
    except Exception as e:
        print(f"❌ Error parsing DATABASE_URL: {e}")
        print(f"   DATABASE_URL value: {DATABASE_URL[:50]}..." if len(DATABASE_URL) > 50 else f"   DATABASE_URL value: {DATABASE_URL}")
        print("   Using DATABASE_URL as-is. Please check the format.")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    print(f"📊 Database configured: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[0]}@...")  # Hide password in logs
else:
    # Default to SQLite for development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
    print("📊 Using SQLite database (default)")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}

db = SQLAlchemy(app)

# Import SEO models after db is created
# They will be imported in admin_seo.py when needed


class Post(db.Model):
    """Blog post model with SEO support"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    slug = db.Column(db.String(500), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text)  # Short summary/excerpt
    featured_image = db.Column(db.String(500))  # Featured image URL
    published_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    author = db.Column(db.String(200), default='Admin')
    url = db.Column(db.String(500))
    post_id = db.Column(db.String(200))
    status = db.Column(db.String(20), default='published')  # draft, published, archived
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with categories
    categories = db.relationship('Category', secondary='post_categories', backref='posts', lazy='dynamic')
    
    def __repr__(self):
        return f'<Post {self.title}>'
    
    @property
    def word_count(self):
        """Calculate word count from content"""
        if self.content:
            # Remove HTML tags and count words
            import re
            text = re.sub(r'<[^>]+>', '', self.content)
            return len(text.split())
        return 0
    
    @property
    def reading_time(self):
        """Calculate reading time in minutes (average 200 words per minute)"""
        return max(1, round(self.word_count / 200))


class Category(db.Model):
    """Category/Tag model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Category {self.name}>'


# Association table for many-to-many relationship
post_categories = db.Table('post_categories',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)


@app.route('/')
def index():
    """Home page - list all posts"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    posts = Post.query.order_by(Post.published_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('index.html', posts=posts)


@app.route('/post/<slug>')
def post_detail(slug):
    """Individual post page"""
    post = Post.query.filter_by(slug=slug).first_or_404()
    
    # Get next and previous posts
    next_post = Post.query.filter(Post.published_date > post.published_date).order_by(Post.published_date.asc()).first()
    prev_post = Post.query.filter(Post.published_date < post.published_date).order_by(Post.published_date.desc()).first()
    
    return render_template('post.html', post=post, next_post=next_post, prev_post=prev_post)


@app.route('/category/<slug>')
def category_posts(slug):
    """Posts by category"""
    category = Category.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    posts = Post.query.join(post_categories).join(Category).filter(
        Category.slug == slug
    ).order_by(Post.published_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('category.html', category=category, posts=posts)


@app.route('/search')
def search():
    """Search posts"""
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    if query:
        posts = Post.query.filter(
            db.or_(
                Post.title.contains(query),
                Post.content.contains(query)
            )
        ).order_by(Post.published_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    else:
        posts = Post.query.order_by(Post.published_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    return render_template('search.html', posts=posts, query=query)


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with form"""
    if request.method == 'POST':
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        subject = request.form.get('subject', '')
        message = request.form.get('message', '')
        
        # Here you would typically send an email
        # For now, we'll just return a success message
        return render_template('contact.html', success=True, name=name)
    
    return render_template('contact.html', success=False)


@app.route('/privacy-policy')
def privacy_policy():
    """Privacy Policy page"""
    return render_template('privacy-policy.html')


@app.route('/terms-conditions')
def terms_conditions():
    """Terms and Conditions page"""
    return render_template('terms-conditions.html')


@app.route('/disclaimer')
def disclaimer():
    """Disclaimer page"""
    return render_template('disclaimer.html')


@app.route('/cookie-policy')
def cookie_policy():
    """Cookie Policy page"""
    return render_template('cookie-policy.html')


@app.route('/dmca')
def dmca():
    """DMCA page"""
    return render_template('dmca.html')


@app.route('/sitemap.xml')
def sitemap():
    """Generate sitemap.xml - Auto-updates when new posts are published"""
    base_url = request.url_root.rstrip('/')
    
    # Get only published posts
    posts = Post.query.filter_by(status='published').order_by(Post.published_date.desc()).all()
    categories = Category.query.all()
    
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>']
    sitemap.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    # Home page
    sitemap.append('<url>')
    sitemap.append(f'<loc>{base_url}/</loc>')
    sitemap.append('<lastmod>{}</lastmod>'.format(datetime.now().strftime('%Y-%m-%d')))
    sitemap.append('<changefreq>daily</changefreq>')
    sitemap.append('<priority>1.0</priority>')
    sitemap.append('</url>')
    
    # Static pages
    static_pages = ['/about', '/contact', '/privacy-policy', '/terms-conditions', 
                   '/disclaimer', '/cookie-policy', '/dmca']
    for page in static_pages:
        sitemap.append('<url>')
        sitemap.append(f'<loc>{base_url}{page}</loc>')
        sitemap.append('<lastmod>{}</lastmod>'.format(datetime.now().strftime('%Y-%m-%d')))
        sitemap.append('<changefreq>monthly</changefreq>')
        sitemap.append('<priority>0.8</priority>')
        sitemap.append('</url>')
    
    # Blog posts (only published)
    for post in posts:
        sitemap.append('<url>')
        sitemap.append(f'<loc>{base_url}/post/{post.slug}</loc>')
        sitemap.append('<lastmod>{}</lastmod>'.format(post.updated_at.strftime('%Y-%m-%d')))
        sitemap.append('<changefreq>weekly</changefreq>')
        sitemap.append('<priority>0.9</priority>')
        sitemap.append('</url>')
    
    # Categories
    for category in categories:
        sitemap.append('<url>')
        sitemap.append(f'<loc>{base_url}/category/{category.slug}</loc>')
        sitemap.append('<lastmod>{}</lastmod>'.format(datetime.now().strftime('%Y-%m-%d')))
        sitemap.append('<changefreq>weekly</changefreq>')
        sitemap.append('<priority>0.7</priority>')
        sitemap.append('</url>')
    
    sitemap.append('</urlset>')
    
    return Response('\n'.join(sitemap), mimetype='application/xml')


@app.route('/feed.xml')
@app.route('/rss.xml')
def rss_feed():
    """Generate RSS feed - Auto-updates when new posts are published"""
    base_url = request.url_root.rstrip('/')
    
    # Get only published posts (latest 20)
    posts = Post.query.filter_by(status='published').order_by(Post.published_date.desc()).limit(20).all()
    
    rss = ['<?xml version="1.0" encoding="UTF-8"?>']
    rss.append('<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/">')
    rss.append('<channel>')
    rss.append(f'<title>Learning Master - Programming & Web Development Blog</title>')
    rss.append(f'<link>{base_url}</link>')
    rss.append(f'<description>Learn Python, PHP, JavaScript, AWS, and modern web development with comprehensive tutorials, guides, and tips.</description>')
    rss.append(f'<language>en-us</language>')
    rss.append(f'<lastBuildDate>{datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")}</lastBuildDate>')
    rss.append(f'<atom:link href="{base_url}/feed.xml" rel="self" type="application/rss+xml"/>')
    
    for post in posts:
        # Get excerpt or generate from content
        excerpt = post.excerpt or (post.content[:200] + '...' if len(post.content) > 200 else post.content)
        # Remove HTML tags from excerpt
        from html import unescape
        import re
        excerpt = re.sub(r'<[^>]+>', '', excerpt)
        excerpt = unescape(excerpt)
        
        rss.append('<item>')
        rss.append(f'<title><![CDATA[{post.title}]]></title>')
        rss.append(f'<link>{base_url}/post/{post.slug}</link>')
        rss.append(f'<guid>{base_url}/post/{post.slug}</guid>')
        rss.append(f'<description><![CDATA[{excerpt}]]></description>')
        rss.append(f'<pubDate>{post.published_date.strftime("%a, %d %b %Y %H:%M:%S +0000")}</pubDate>')
        rss.append(f'<author>{post.author}</author>')
        if post.categories:
            for category in post.categories.all()[:3]:
                rss.append(f'<category><![CDATA[{category.name}]]></category>')
        rss.append('</item>')
    
    rss.append('</channel>')
    rss.append('</rss>')
    
    return Response('\n'.join(rss), mimetype='application/rss+xml')


@app.route('/robots.txt')
def robots():
    """Generate robots.txt"""
    base_url = request.url_root.rstrip('/')
    robots_content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/

Sitemap: {base_url}/sitemap.xml
"""
    return Response(robots_content, mimetype='text/plain')


@app.route('/api/contact', methods=['POST'])
def api_contact():
    """API endpoint for contact form"""
    try:
        data = request.get_json()
        name = data.get('name', '')
        email = data.get('email', '')
        subject = data.get('subject', '')
        message = data.get('message', '')
        
        # Here you would send an email
        # For now, just return success
        return jsonify({'success': True, 'message': 'Thank you for your message!'})
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred'}), 400


@app.route('/api/newsletter', methods=['POST'])
def api_newsletter():
    """API endpoint for newsletter subscription"""
    try:
        data = request.get_json()
        email = data.get('email', '')
        
        # Here you would save to database or send to email service
        # For now, just return success
        return jsonify({'success': True, 'message': 'Successfully subscribed!'})
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred'}), 400


@app.template_filter('process_content')
def process_content_filter(content):
    """Template filter to process blog content"""
    return process_blog_content(content)


@app.template_filter('regex_search')
def regex_search_filter(text, pattern):
    """Extract first match from text using regex"""
    import re
    match = re.search(pattern, text)
    return match.group(1) if match else None




@app.context_processor
def inject_categories():
    """Make categories, recent posts, static version, and current date available to all templates"""
    import time
    categories = Category.query.all()
    recent_posts = Post.query.order_by(Post.published_date.desc()).limit(5).all()
    return dict(
        categories=categories, 
        recent_posts=recent_posts,
        static_version=int(time.time()),
        current_date=datetime.now().strftime('%B %d, %Y')
    )


@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404


# Import and initialize authentication
from auth import init_auth_routes
init_auth_routes(app)

# Import admin routes (optional - uncomment to enable admin panel)
from admin import register_admin_routes
register_admin_routes(app, db, Post, Category)  # This adds /admin routes to the main app

# Import SEO-optimized admin routes
try:
    from admin_seo import register_seo_admin_routes
    register_seo_admin_routes(app, db, Post, Category)  # This adds /admin/seo routes
except ImportError as e:
    print(f"Warning: Could not load SEO admin routes: {e}")


if __name__ == '__main__':
    with app.app_context():
        # Create core tables
        db.create_all()
        
        # Import and create SEO tables (models are defined in register_seo_admin_routes)
        try:
            import admin_seo
            # Models should be available after register_seo_admin_routes was called above
            if admin_seo.PostSEO is not None:
                db.create_all()  # Create SEO tables if they don't exist
                print("✅ SEO tables ready")
            else:
                print("⚠️  SEO models not yet initialized")
        except Exception as e:
            print(f"⚠️  SEO tables: {e}")
            print("   SEO admin will work with basic functionality")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

