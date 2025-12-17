# Learning Master - Python Blog

A Python-based blog application for learning programming and web development. Covers Python, PHP, JavaScript, AWS, and modern web technologies with comprehensive tutorials and guides.

## Features

- ✅ Complete blog post migration from Blogger
- ✅ Category/Tag support
- ✅ Search functionality
- ✅ Responsive design matching Blogger style
- ✅ Pagination
- ✅ Clean, modern UI

## Setup Instructions

### 1. Install Dependencies

Activate your virtual environment and install required packages:

```bash
source myenv/bin/activate  # On macOS/Linux
# or
myenv\Scripts\activate  # On Windows

pip install -r requirements.txt
```

### 2. Scrape Blog Content

Run the scraper to fetch all posts from your Blogger blog:

```bash
python scraper.py
```

This will create a `blog_posts.json` file containing all scraped posts.

### 3. Import Posts to Database

Import the scraped posts into the SQLite database:

```bash
python import_posts.py
```

**Note:** If you've already imported posts and want to re-process them with the new content processor (to fix images, links, etc.), run:

```bash
python reprocess_posts.py
```

### 4. Run the Application

Start the Flask development server:

```bash
python app.py
```

The blog will be available at `http://localhost:5000`

## Project Structure

```
learningMaster/
├── app.py                 # Flask application
├── scraper.py             # Blog scraper
├── import_posts.py         # Import script
├── requirements.txt       # Python dependencies
├── blog_posts.json        # Scraped posts (generated)
├── blog.db                # SQLite database (generated)
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── post.html
│   ├── category.html
│   ├── search.html
│   ├── about.html
│   └── 404.html
└── static/
    └── css/
        └── style.css
```

## Usage

### Scraping

The scraper supports two methods:
1. **Atom Feed** (preferred): Fetches posts from Blogger's Atom feed
2. **HTML Scraping**: Falls back to HTML scraping if feed doesn't work

### Database

The application uses SQLite by default. To use PostgreSQL or MySQL, update the `DATABASE_URL` in `app.py`:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/blog'
```

### Customization

- **Styling**: Edit `static/css/style.css`
- **Templates**: Modify files in `templates/`
- **Blog Title**: Update in `templates/base.html`

## Troubleshooting

### Scraper Issues

If the scraper doesn't fetch all posts:
1. Check your internet connection
2. Verify the blog URL is correct
3. Blogger may have rate limiting - wait a few minutes and try again

### Import Issues

If posts don't import:
1. Ensure `blog_posts.json` exists
2. Check for duplicate slugs (they must be unique)
3. Verify the JSON file is valid

### Database Issues

If you need to reset the database:
```bash
rm blog.db
python app.py  # This will recreate the database
python import_posts.py  # Re-import posts
```

## License

This project is for personal use. All blog content belongs to the original author.

