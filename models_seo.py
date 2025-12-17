"""
Enhanced database models with SEO fields
"""
from datetime import datetime
from sqlalchemy import Text, String, Integer, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship

# db will be imported from app when models are used

class PostSEO(db.Model):
    """SEO metadata for blog posts"""
    __tablename__ = 'post_seo'
    
    id = db.Column(Integer, primary_key=True)
    post_id = db.Column(Integer, db.ForeignKey('post.id'), unique=True, nullable=False)
    
    # Primary SEO fields
    primary_keyword = db.Column(String(200))
    secondary_keywords = db.Column(Text)  # Comma-separated
    meta_title = db.Column(String(70))  # Max 60 chars recommended
    meta_description = db.Column(String(160))  # Max 155 chars recommended
    
    # Open Graph fields
    og_title = db.Column(String(100))
    og_description = db.Column(Text)
    og_image = db.Column(String(500))
    
    # Twitter Card fields
    twitter_title = db.Column(String(100))
    twitter_description = db.Column(Text)
    twitter_image = db.Column(String(500))
    
    # Additional SEO
    canonical_url = db.Column(String(500))
    schema_type = db.Column(String(50), default='Article')  # Article, BlogPosting, etc.
    reading_time = db.Column(Integer)  # in minutes
    word_count = db.Column(Integer)
    
    # SEO metrics
    seo_score = db.Column(Integer, default=0)  # 0-100
    keyword_density = db.Column(Float)  # Percentage
    
    # Timestamps
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    post = relationship('Post', backref='seo', uselist=False)
    
    def __repr__(self):
        return f'<PostSEO {self.post_id}>'


class PostImage(db.Model):
    """Images with ALT text for posts"""
    __tablename__ = 'post_images'
    
    id = db.Column(Integer, primary_key=True)
    post_id = db.Column(Integer, db.ForeignKey('post.id'), nullable=False)
    image_url = db.Column(String(500), nullable=False)
    alt_text = db.Column(String(200), nullable=False)
    caption = db.Column(Text)
    is_featured = db.Column(Boolean, default=False)
    order = db.Column(Integer, default=0)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    post = relationship('Post', backref='images')
    
    def __repr__(self):
        return f'<PostImage {self.id}>'


class PostDraft(db.Model):
    """Draft versions of posts"""
    __tablename__ = 'post_drafts'
    
    id = db.Column(Integer, primary_key=True)
    post_id = db.Column(Integer, db.ForeignKey('post.id'), nullable=True)  # Null if new post
    title = db.Column(String(500))
    slug = db.Column(String(500))
    content = db.Column(Text)
    excerpt = db.Column(Text)
    author = db.Column(String(200))
    status = db.Column(String(20), default='draft')  # draft, review, published
    
    # SEO draft data (stored as JSON)
    seo_data = db.Column(Text)  # JSON string
    
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    post = relationship('Post', backref='drafts')
    
    def __repr__(self):
        return f'<PostDraft {self.id}>'

