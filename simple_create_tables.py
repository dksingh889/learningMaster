"""
Simple script to create SEO tables
Run: python simple_create_tables.py
"""
from app import app, db

def create_seo_tables():
    """Create SEO tables using SQL"""
    with app.app_context():
        from sqlalchemy import inspect, text
        
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        print("\n" + "="*60)
        print("Creating SEO Tables")
        print("="*60)
        print(f"\nExisting tables: {existing_tables}\n")
        
        # SQL statements to create tables
        tables_sql = {
            'post_seo': """
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
                    keyword_density FLOAT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (post_id) REFERENCES post(id)
                )
            """,
            'post_images': """
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
            """,
            'post_drafts': """
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
        }
        
        created = []
        for table_name, sql in tables_sql.items():
            if table_name not in existing_tables:
                try:
                    # Use raw SQL to create table
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
        final_tables = inspector.get_table_names()
        
        print("\n" + "="*60)
        print("Final Tables")
        print("="*60)
        print(f"\nAll tables: {final_tables}")
        
        if created:
            print(f"\n✅ Created {len(created)} new table(s): {created}")
        else:
            print("\n✅ All tables already exist")
        
        print("\n" + "="*60)
        print("✅ Done!")
        print("="*60)
        print("\nYou now have these tables:")
        for table in final_tables:
            print(f"  - {table}")

if __name__ == '__main__':
    create_seo_tables()

