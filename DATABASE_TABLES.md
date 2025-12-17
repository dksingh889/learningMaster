# Database Tables Overview

## 📊 Current Database Structure

Your blog database should have **6 tables** for full SEO functionality:

### Core Tables (3 - Already Exist)

1. **`post`** - Blog posts
   - id, title, slug, content, excerpt, featured_image
   - published_date, author, status, is_featured
   - created_at, updated_at

2. **`category`** - Categories/tags
   - id, name, slug

3. **`post_categories`** - Association table
   - post_id, category_id (many-to-many relationship)

### SEO Tables (3 - Need to be Created)

4. **`post_seo`** - SEO metadata for each post
   - id, post_id (foreign key to post)
   - primary_keyword, secondary_keywords
   - meta_title, meta_description
   - og_title, og_description, og_image
   - twitter_title, twitter_description, twitter_image
   - canonical_url, schema_type
   - reading_time, word_count
   - seo_score, keyword_density
   - created_at, updated_at

5. **`post_images`** - Images with ALT text
   - id, post_id (foreign key to post)
   - image_url, alt_text, caption
   - is_featured, order
   - created_at

6. **`post_drafts`** - Draft versions
   - id, post_id (nullable, for new posts)
   - title, slug, content, excerpt, author
   - status, seo_data (JSON)
   - created_at, updated_at

## 🔧 How to Create SEO Tables

### Option 1: Run the Migration Script

```bash
python create_seo_tables.py
```

This will:
- Check existing tables
- Create the 3 new SEO tables
- Show you what was created

### Option 2: Automatic Creation

The tables will be created automatically when you:
1. Start your Flask app: `python app.py`
2. The `db.create_all()` in app.py will create all tables

### Option 3: Manual SQL (if needed)

If you prefer SQL:

```sql
-- PostSEO table
CREATE TABLE post_seo (
    id INTEGER PRIMARY KEY,
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
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (post_id) REFERENCES post(id)
);

-- PostImage table
CREATE TABLE post_images (
    id INTEGER PRIMARY KEY,
    post_id INTEGER NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    alt_text VARCHAR(200) NOT NULL,
    caption TEXT,
    is_featured BOOLEAN DEFAULT 0,
    order INTEGER DEFAULT 0,
    created_at DATETIME,
    FOREIGN KEY (post_id) REFERENCES post(id)
);

-- PostDraft table
CREATE TABLE post_drafts (
    id INTEGER PRIMARY KEY,
    post_id INTEGER,
    title VARCHAR(500),
    slug VARCHAR(500),
    content TEXT,
    excerpt TEXT,
    author VARCHAR(200),
    status VARCHAR(20) DEFAULT 'draft',
    seo_data TEXT,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (post_id) REFERENCES post(id)
);
```

## ✅ Verify Tables

Check if tables exist:

```python
from app import app, db
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print("Tables:", tables)
```

Should show:
- `post`
- `category`
- `post_categories`
- `post_seo` ✅
- `post_images` ✅
- `post_drafts` ✅

## 📝 Table Relationships

```
post (1) ──< (many) post_seo
post (1) ──< (many) post_images
post (1) ──< (many) post_drafts
post (many) ──< (many) category (via post_categories)
```

## 🎯 What Each Table Does

### post_seo
- Stores all SEO metadata for each post
- One record per post (1:1 relationship)
- Used for SEO score calculation and analysis

### post_images
- Stores images with ALT text for SEO
- Multiple images per post (1:many relationship)
- Ensures all images have proper ALT text

### post_drafts
- Stores draft versions before publishing
- Allows saving work in progress
- Can have multiple drafts per post

## ⚠️ Important Notes

1. **PostSEO is Optional**: The SEO admin will work without it, but you won't get:
   - SEO score tracking
   - Historical SEO data
   - Advanced SEO analytics

2. **Backward Compatible**: Existing posts will work fine. SEO data is only added when you create posts through the SEO admin.

3. **No Data Loss**: Creating new tables won't affect existing data.

## 🚀 Quick Setup

Just run:
```bash
python create_seo_tables.py
```

Or start your app - tables will be created automatically:
```bash
python app.py
```

---

**After creating tables, you'll have a complete SEO-optimized database!** 🎉

