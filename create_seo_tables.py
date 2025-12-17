"""
Create SEO-related database tables using SQL (avoids model conflicts)
Run: python create_seo_tables.py
"""
from app import app, db
from sqlalchemy import inspect, text
from datetime import datetime

def create_tables():
    """Create all SEO tables using raw SQL"""
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            print("\n" + "="*60)
            print("Database Tables Check")
            print("="*60)
            print(f"\nCurrent tables: {existing_tables}")
            print("\nCreating SEO tables using SQL...")
            
            # Detect database type
            db_url = str(db.engine.url)
            is_mysql = 'mysql' in db_url.lower()
            
            # SQL for creating tables (MySQL vs SQLite)
            if is_mysql:
                # MySQL syntax
                post_seo_sql = """
                    CREATE TABLE IF NOT EXISTS post_seo (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        post_id INT UNIQUE NOT NULL,
                        primary_keyword VARCHAR(200),
                        secondary_keywords TEXT,
                        meta_title VARCHAR(70),
                        meta_description VARCHAR(160),
                        og_title VARCHAR(100),
                        og_description TEXT,
                        og_image VARCHAR(500),
                        twitter_title VARCHAR(100),
                        twitter_description TEXT,
                        twitter_image VARCHAR(500),
                        canonical_url VARCHAR(500),
                        schema_type VARCHAR(50) DEFAULT 'Article',
                        reading_time INT,
                        word_count INT,
                        seo_score INT DEFAULT 0,
                        keyword_density FLOAT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (post_id) REFERENCES post(id)
                    )
                """
                post_images_sql = """
                    CREATE TABLE IF NOT EXISTS post_images (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        post_id INT NOT NULL,
                        image_url VARCHAR(500) NOT NULL,
                        alt_text VARCHAR(200) NOT NULL,
                        caption TEXT,
                        is_featured BOOLEAN DEFAULT 0,
                        order_index INT DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (post_id) REFERENCES post(id)
                    )
                """
                post_drafts_sql = """
                    CREATE TABLE IF NOT EXISTS post_drafts (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        post_id INT,
                        title VARCHAR(500),
                        slug VARCHAR(500),
                        content TEXT,
                        excerpt TEXT,
                        author VARCHAR(200),
                        status VARCHAR(20) DEFAULT 'draft',
                        seo_data TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (post_id) REFERENCES post(id)
                    )
                """
            else:
                # SQLite syntax
                post_seo_sql = """
                    CREATE TABLE IF NOT EXISTS post_seo (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        post_id INTEGER UNIQUE NOT NULL,
                        primary_keyword VARCHAR(200),
                        secondary_keywords TEXT,
                        meta_title VARCHAR(70),
                        meta_description VARCHAR(160),
                        og_title VARCHAR(100),
                        og_description TEXT,
                        og_image VARCHAR(500),
                        twitter_title VARCHAR(100),
                        twitter_description TEXT,
                        twitter_image VARCHAR(500),
                        canonical_url VARCHAR(500),
                        schema_type VARCHAR(50) DEFAULT 'Article',
                        reading_time INTEGER,
                        word_count INTEGER,
                        seo_score INTEGER DEFAULT 0,
                        keyword_density REAL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (post_id) REFERENCES post(id)
                    )
                """
                post_images_sql = """
                    CREATE TABLE IF NOT EXISTS post_images (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        post_id INTEGER NOT NULL,
                        image_url VARCHAR(500) NOT NULL,
                        alt_text VARCHAR(200) NOT NULL,
                        caption TEXT,
                        is_featured BOOLEAN DEFAULT 0,
                        order_index INTEGER DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (post_id) REFERENCES post(id)
                    )
                """
                post_drafts_sql = """
                    CREATE TABLE IF NOT EXISTS post_drafts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        post_id INTEGER,
                        title VARCHAR(500),
                        slug VARCHAR(500),
                        content TEXT,
                        excerpt TEXT,
                        author VARCHAR(200),
                        status VARCHAR(20) DEFAULT 'draft',
                        seo_data TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (post_id) REFERENCES post(id)
                    )
                """
            
            tables_to_create = {
                'post_seo': post_seo_sql,
                'post_images': post_images_sql,
                'post_drafts': post_drafts_sql
            }
            
            created = []
            for table_name, sql in tables_to_create.items():
                if table_name not in existing_tables:
                    try:
                        db.session.execute(text(sql))
                        db.session.commit()
                        created.append(table_name)
                        print(f"✅ Created table: {table_name}")
                    except Exception as e:
                        print(f"❌ Error creating {table_name}: {e}")
                        db.session.rollback()
                else:
                    print(f"✅ Table already exists: {table_name}")
            
            # Check final state
            inspector = inspect(db.engine)
            new_tables = inspector.get_table_names()
            
            print(f"\n✅ Tables after creation: {new_tables}")
            
            if created:
                print(f"\n✅ Created {len(created)} new table(s): {created}")
            else:
                print("\n✅ All tables already exist")
            
            # Verify table structures
            print("\n" + "="*60)
            print("Table Summary")
            print("="*60)
            
            table_info = {
                'post': 'Blog posts (main content)',
                'category': 'Categories/tags',
                'post_categories': 'Post-category relationships',
                'post_seo': 'SEO metadata (keywords, meta tags, OG tags)',
                'post_images': 'Images with ALT text',
                'post_drafts': 'Draft versions of posts'
            }
            
            for table_name, description in table_info.items():
                if table_name in new_tables:
                    columns = [col['name'] for col in inspector.get_columns(table_name)]
                    print(f"\n✅ {table_name}")
                    print(f"   Description: {description}")
                    print(f"   Columns ({len(columns)}): {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}")
            
            print("\n" + "="*60)
            print("✅ Database setup complete!")
            print("="*60)
            print("\nYou now have 6 tables:")
            print("  1. post - Blog posts")
            print("  2. category - Categories/tags")
            print("  3. post_categories - Post-category relationships")
            print("  4. post_seo - SEO metadata (NEW)")
            print("  5. post_images - Images with ALT text (NEW)")
            print("  6. post_drafts - Draft versions (NEW)")
            print("\n")
            
        except Exception as e:
            print(f"\n❌ Error creating tables: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    create_tables()
    """SEO metadata for blog posts"""
    __tablename__ = 'post_seo'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), unique=True, nullable=False)
    
    # Primary SEO fields
    primary_keyword = db.Column(db.String(200))
    secondary_keywords = db.Column(db.Text)
    meta_title = db.Column(db.String(70))
    meta_description = db.Column(db.String(160))
    
    # Open Graph fields
    og_title = db.Column(db.String(100))
    og_description = db.Column(db.Text)
    og_image = db.Column(db.String(500))
    
    # Twitter Card fields
    twitter_title = db.Column(db.String(100))
    twitter_description = db.Column(db.Text)
    twitter_image = db.Column(db.String(500))
    
    # Additional SEO
    canonical_url = db.Column(db.String(500))
    schema_type = db.Column(db.String(50), default='Article')
    reading_time = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    
    # SEO metrics
    seo_score = db.Column(db.Integer, default=0)
    keyword_density = db.Column(db.Float)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PostSEO {self.post_id}>'


class PostImage(db.Model):
    """Images with ALT text for posts"""
    __tablename__ = 'post_images'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    alt_text = db.Column(db.String(200), nullable=False)
    caption = db.Column(db.Text)
    is_featured = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PostImage {self.id}>'


class PostDraft(db.Model):
    """Draft versions of posts"""
    __tablename__ = 'post_drafts'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    title = db.Column(db.String(500))
    slug = db.Column(db.String(500))
    content = db.Column(db.Text)
    excerpt = db.Column(db.Text)
    author = db.Column(db.String(200))
    status = db.Column(db.String(20), default='draft')
    seo_data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PostDraft {self.id}>'


def create_tables():
    """Create all SEO tables"""
    with app.app_context():
        try:
            # Import models first to register them
            try:
                from admin_seo import PostSEO, PostImage, PostDraft
            except ImportError:
                # Models defined inline above
                pass
            
            # Check existing tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            print("\n" + "="*60)
            print("Database Tables Check")
            print("="*60)
            print(f"\nCurrent tables: {existing_tables}")
            print("\nCreating SEO tables...")
            
            # Create all tables (this will create new ones, skip existing)
            db.create_all()
            
            # Check new tables
            inspector = inspect(db.engine)
            new_tables = inspector.get_table_names()
            
            print(f"\n✅ Tables after creation: {new_tables}")
            
            # Show what was added
            added_tables = [t for t in new_tables if t not in existing_tables]
            if added_tables:
                print(f"\n✅ New tables created: {added_tables}")
            else:
                print("\n✅ All tables already exist")
            
            # Verify table structures
            print("\n" + "="*60)
            print("Table Summary")
            print("="*60)
            
            table_info = {
                'post': 'Blog posts (main content)',
                'category': 'Categories/tags',
                'post_categories': 'Post-category relationships',
                'post_seo': 'SEO metadata (keywords, meta tags, OG tags)',
                'post_images': 'Images with ALT text',
                'post_drafts': 'Draft versions of posts'
            }
            
            for table_name, description in table_info.items():
                if table_name in new_tables:
                    columns = [col['name'] for col in inspector.get_columns(table_name)]
                    print(f"\n✅ {table_name}")
                    print(f"   Description: {description}")
                    print(f"   Columns ({len(columns)}): {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}")
            
            print("\n" + "="*60)
            print("✅ Database setup complete!")
            print("="*60)
            print("\nYou now have 6 tables:")
            print("  1. post - Blog posts")
            print("  2. category - Categories/tags")
            print("  3. post_categories - Post-category relationships")
            print("  4. post_seo - SEO metadata (NEW)")
            print("  5. post_images - Images with ALT text (NEW)")
            print("  6. post_drafts - Draft versions (NEW)")
            print("\n")
            
        except Exception as e:
            print(f"\n❌ Error creating tables: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    create_tables()
