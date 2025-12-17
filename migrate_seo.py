"""
Database migration script to add SEO fields
Run: python migrate_seo.py
"""
from app import app, db
from sqlalchemy import text

def migrate_database():
    """Add SEO-related columns to existing tables"""
    with app.app_context():
        try:
            # Check if PostSEO table exists
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'post_seo' not in tables:
                print("Creating PostSEO table...")
                db.create_all()
                print("✅ PostSEO table created")
            else:
                print("✅ PostSEO table already exists")
            
            # Add new columns to Post table if they don't exist
            print("\nChecking Post table columns...")
            post_columns = [col['name'] for col in inspector.get_columns('post')]
            
            new_columns = {
                'excerpt': 'TEXT',
                'featured_image': 'VARCHAR(500)',
                'status': "VARCHAR(20) DEFAULT 'published'",
                'is_featured': 'BOOLEAN DEFAULT 0'
            }
            
            for col_name, col_type in new_columns.items():
                if col_name not in post_columns:
                    try:
                        if 'DEFAULT' in col_type:
                            # Extract type and default separately
                            if 'VARCHAR' in col_type:
                                default_val = col_type.split("DEFAULT '")[1].split("'")[0]
                                sql = f"ALTER TABLE post ADD COLUMN {col_name} VARCHAR(20) DEFAULT '{default_val}'"
                            elif 'BOOLEAN' in col_type:
                                default_val = col_type.split('DEFAULT ')[1]
                                sql = f"ALTER TABLE post ADD COLUMN {col_name} BOOLEAN DEFAULT {default_val}"
                            else:
                                sql = f"ALTER TABLE post ADD COLUMN {col_name} {col_type}"
                        else:
                            sql = f"ALTER TABLE post ADD COLUMN {col_name} {col_type}"
                        
                        db.session.execute(text(sql))
                        db.session.commit()
                        print(f"✅ Added column: {col_name}")
                    except Exception as e:
                        print(f"⚠️  Could not add column {col_name}: {e}")
                        db.session.rollback()
                else:
                    print(f"✅ Column {col_name} already exists")
            
            print("\n✅ Migration complete!")
            print("\nNote: If you see errors about PostSEO model, you may need to:")
            print("1. Import models_seo in app.py")
            print("2. Run db.create_all() again")
            
        except Exception as e:
            print(f"❌ Migration error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    migrate_database()

