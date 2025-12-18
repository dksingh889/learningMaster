"""
Simple admin interface for managing blog posts
Run: python admin.py (standalone)
Or import register_admin_routes() in app.py
"""
from flask import render_template, request, redirect, url_for, flash
from datetime import datetime
import re
from utils import process_blog_content
from auth import login_required


def create_slug(text):
    """Create URL-friendly slug"""
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug[:100]


def register_admin_routes(app, db, Post, Category):
    """Register admin routes with the Flask app - Redirects to SEO dashboard"""
    
    @app.route('/admin')
    @login_required
    def admin_index():
        """Redirect to SEO dashboard"""
        try:
            return redirect(url_for('admin_seo_dashboard'))
        except:
            # Fallback if SEO routes not loaded
            flash('SEO admin panel is loading...', 'info')
            return redirect('/')
    
    @app.route('/admin/posts')
    @login_required
    def admin_posts():
        """Redirect to SEO posts list"""
        try:
            return redirect(url_for('admin_seo_posts'))
        except:
            return redirect('/')
    
    @app.route('/admin/posts/new', methods=['GET', 'POST'])
    @login_required
    def admin_new_post():
        """Redirect to SEO post creation"""
        return redirect(url_for('admin_seo_new_post'))
        """Create new post"""
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            author = request.form.get('author', 'Admin').strip() or 'Admin'
            category_names = request.form.getlist('categories')
            published_date_str = request.form.get('published_date', '')
            
            if not title or not content:
                flash('Title and content are required!', 'error')
                return redirect(request.url)
            
            # Create slug
            slug = create_slug(title)
            
            # Check if slug exists
            existing = Post.query.filter_by(slug=slug).first()
            if existing:
                flash(f'A post with slug "{slug}" already exists!', 'error')
                return redirect(request.url)
            
            # Process content
            processed_content = process_blog_content(content)
            
            # Parse date
            if published_date_str:
                try:
                    published_date = datetime.strptime(published_date_str, '%Y-%m-%d')
                except ValueError:
                    published_date = datetime.now()
            else:
                published_date = datetime.now()
            
            # Handle categories
            categories = []
            for cat_name in category_names:
                if cat_name:
                    cat_slug = create_slug(cat_name)
                    category = Category.query.filter_by(slug=cat_slug).first()
                    if not category:
                        category = Category(name=cat_name, slug=cat_slug)
                        db.session.add(category)
                        db.session.flush()
                    categories.append(category)
            
            # Create post
            post = Post(
                title=title,
                slug=slug,
                content=processed_content,
                published_date=published_date,
                author=author
            )
            
            post.categories = categories
            
            try:
                db.session.add(post)
                db.session.commit()
                flash(f'Post "{title}" created successfully!', 'success')
                return redirect(url_for('admin_posts'))
            except Exception as e:
                flash(f'Error creating post: {str(e)}', 'error')
                db.session.rollback()
                return redirect(request.url)
        
        # GET request - show form
        categories = Category.query.all()
        today_date = datetime.now().strftime('%Y-%m-%d')
        return render_template('admin/new_post.html', categories=categories, today_date=today_date)
    
    @app.route('/admin/posts/<int:post_id>/edit', methods=['GET', 'POST'])
    @login_required
    def admin_edit_post(post_id):
        """Redirect to SEO post detail/analysis"""
        try:
            return redirect(url_for('admin_seo_post_detail', post_id=post_id))
        except:
            return redirect('/')
        """Edit existing post"""
        post = Post.query.get_or_404(post_id)
        
        if request.method == 'POST':
            post.title = request.form.get('title', '').strip()
            post.content = request.form.get('content', '').strip()
            post.author = request.form.get('author', 'Admin').strip() or 'Admin'
            category_names = request.form.getlist('categories')
            published_date_str = request.form.get('published_date', '')
            
            if not post.title or not post.content:
                flash('Title and content are required!', 'error')
                return redirect(request.url)
            
            # Update slug if title changed
            new_slug = create_slug(post.title)
            if new_slug != post.slug:
                existing = Post.query.filter_by(slug=new_slug).first()
                if existing and existing.id != post.id:
                    flash(f'A post with slug "{new_slug}" already exists!', 'error')
                    return redirect(request.url)
                post.slug = new_slug
            
            # Process content
            post.content = process_blog_content(post.content)
            
            # Parse date
            if published_date_str:
                try:
                    post.published_date = datetime.strptime(published_date_str, '%Y-%m-%d')
                except ValueError:
                    pass
            
            # Update categories
            categories = []
            for cat_name in category_names:
                if cat_name:
                    cat_slug = create_slug(cat_name)
                    category = Category.query.filter_by(slug=cat_slug).first()
                    if not category:
                        category = Category(name=cat_name, slug=cat_slug)
                        db.session.add(category)
                        db.session.flush()
                    categories.append(category)
            
            post.categories = categories
            post.updated_at = datetime.now()
            
            try:
                db.session.commit()
                flash(f'Post "{post.title}" updated successfully!', 'success')
                return redirect(url_for('admin_posts'))
            except Exception as e:
                flash(f'Error updating post: {str(e)}', 'error')
                db.session.rollback()
                return redirect(request.url)
        
        # GET request - show form
        categories = Category.query.all()
        post_categories = post.categories.all()
        today_date = datetime.now().strftime('%Y-%m-%d')
        return render_template('admin/edit_post.html', post=post, categories=categories, post_categories=post_categories, today_date=today_date)
    
    @app.route('/admin/posts/<int:post_id>/delete', methods=['POST'])
    @login_required
    def admin_delete_post(post_id):
        """Delete a post"""
        post = Post.query.get_or_404(post_id)
        title = post.title
        
        try:
            db.session.delete(post)
            db.session.commit()
            flash(f'Post "{title}" deleted successfully!', 'success')
        except Exception as e:
            flash(f'Error deleting post: {str(e)}', 'error')
            db.session.rollback()
        
        try:
            return redirect(url_for('admin_seo_posts'))
        except:
            return redirect('/')


# Standalone mode - for running admin separately
if __name__ == '__main__':
    from app import app, db, Post, Category
    register_admin_routes(app, db, Post, Category)
    
    # Also register SEO admin routes
    try:
        from admin_seo import register_seo_admin_routes
        register_seo_admin_routes(app, db, Post, Category)
    except ImportError:
        pass
    
    with app.app_context():
        db.create_all()
    
    print("\n" + "="*60)
    print("Admin Panel Starting...")
    print("="*60)
    print("Visit: http://localhost:5000/admin")
    print("SEO Admin: http://localhost:5000/admin/seo")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
