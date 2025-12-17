# Post Management Guide

This guide explains where your blog posts are stored and how to add new posts.

## 📊 Where Posts Are Stored

### Database Location
Your blog posts are stored in a **SQLite database** file:
- **Location**: `instance/blog.db` (or `blog.db` in the project root)
- **Format**: SQLite database
- **Tables**: 
  - `post` - Blog posts
  - `category` - Categories/tags
  - `post_categories` - Relationship table

### Database Configuration
The database is configured in `app.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')
```

You can change this to use PostgreSQL, MySQL, or other databases by setting the `DATABASE_URL` environment variable.

## ✍️ How to Add New Posts

You have **three methods** to add new posts:

### Method 1: Admin Web Interface (Recommended) 🎯

The easiest way to add posts is through the web-based admin interface.

1. **Option A: Add admin routes to main app** (Recommended)
   
   Add this line to the end of `app.py` (before `if __name__ == '__main__':`):
   ```python
   # Import admin routes
   from admin import admin_app
   ```
   
   Then access admin at: `http://localhost:5000/admin`

2. **Option B: Run admin separately**
   
   Stop your main Flask app, then run:
   ```bash
   python admin.py
   ```
   
   Then access admin at: `http://localhost:5000/admin`
   
   **Note:** You can't run both simultaneously with this method.

3. **Click "New Post"** and fill in the form:
   - Title
   - Content (HTML supported)
   - Author
   - Published Date
   - Categories

4. **Click "Create Post"** - Done! ✅

**Features:**
- ✅ Visual editor interface
- ✅ Edit existing posts
- ✅ Delete posts
- ✅ Manage categories
- ✅ View all posts in a table

**Note:** The admin runs on port 5001, while your main blog runs on port 5000. You can run both simultaneously.

### Method 2: Command Line Script (Interactive)

Use the interactive command-line script:

```bash
python add_post.py
```

The script will prompt you for:
- Post title
- Content (type your content, then type 'END' on a new line)
- Author name
- Categories (comma-separated)
- Published date

**Example:**
```bash
$ python add_post.py

Enter post title: Getting Started with Python
Enter post content (HTML supported). Type 'END' on a new line when finished:
<p>This is my first post about Python...</p>
END

Enter author name (default: Admin): John Doe
Enter categories (comma-separated): Python, Tutorial
Enter published date (YYYY-MM-DD) or press Enter for today: 2024-11-27

✅ Successfully added post: Getting Started with Python
```

### Method 3: Command Line Script (From File)

If you have your post content in an HTML file:

```bash
python add_post.py --file "Post Title" content.html "Author Name"
```

**Example:**
```bash
python add_post.py --file "Python Tutorial" my_post.html "John Doe"
```

## 📝 Post Content Format

### HTML Support
Your posts support HTML content, including:
- Headings (`<h1>`, `<h2>`, etc.)
- Paragraphs (`<p>`)
- Links (`<a href="">`)
- Images (`<img src="">`)
- Lists (`<ul>`, `<ol>`)
- Code blocks (will be automatically highlighted)
- And more!

### Example Post Content:
```html
<h2>Introduction</h2>
<p>This is a paragraph about Python programming.</p>

<h3>Code Example</h3>
<pre><code class="language-python">
def hello():
    print("Hello, World!")
</code></pre>

<p>For more information, visit <a href="https://python.org">Python.org</a></p>
```

## 🔧 Managing Posts

### View All Posts
- **Admin Interface**: http://localhost:5001/admin/posts
- **Command Line**: Check the database directly (see below)

### Edit Posts
1. Go to admin interface: http://localhost:5001/admin/posts
2. Click "Edit" next to the post you want to modify
3. Make your changes
4. Click "Update Post"

### Delete Posts
1. Go to admin interface: http://localhost:5001/admin/posts
2. Click "Delete" next to the post
3. Confirm deletion

### View Post in Database
You can view posts directly in the database using SQLite:

```bash
sqlite3 instance/blog.db

# View all posts
SELECT id, title, slug, author, published_date FROM post;

# View a specific post
SELECT title, content FROM post WHERE slug = 'your-post-slug';

# Exit
.quit
```

## 🏷️ Categories/Tags

### Adding Categories
Categories are automatically created when you:
- Add a post with new category names
- Use the admin interface to select/create categories

### Viewing Categories
- **Admin Interface**: Dashboard shows category count
- **Database**: `SELECT * FROM category;`

## 📋 Best Practices

1. **Use Descriptive Titles**: Make titles clear and SEO-friendly
2. **Add Categories**: Always categorize your posts
3. **Use HTML Properly**: Format your content with proper HTML tags
4. **Add Images**: Include relevant images in your posts
5. **Set Dates**: Use appropriate published dates
6. **Regular Updates**: Post regularly to keep your blog active

## 🔐 Security Note

**Important**: The admin interface has basic authentication. For production use:

1. Add proper authentication (login/password)
2. Use environment variables for secrets
3. Restrict admin access to specific IPs
4. Use HTTPS in production

## 🚀 Production Deployment

When deploying to production:

1. **Set Environment Variables**:
   ```bash
   export SECRET_KEY='your-secret-key-here'
   export DATABASE_URL='postgresql://user:pass@localhost/blog'
   ```

2. **Use Production Database**: Consider PostgreSQL or MySQL instead of SQLite

3. **Add Authentication**: Implement proper login system for admin

4. **Use HTTPS**: Always use SSL/TLS in production

## 📚 Additional Resources

- **Database Models**: See `app.py` for Post and Category models
- **Content Processing**: See `utils.py` for how content is processed
- **Templates**: See `templates/` for how posts are displayed

---

**Happy Blogging!** 🎉

