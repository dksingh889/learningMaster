"""
SEO-Optimized Admin Panel for Blog Posts
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, Response
from datetime import datetime
import os
import re
import json
from werkzeug.utils import secure_filename
from sqlalchemy import text
from utils import process_blog_content
from seo_utils import (
    calculate_word_count, calculate_reading_time, extract_headings,
    calculate_keyword_density, generate_meta_description, suggest_headings,
    suggest_faqs, calculate_seo_score, validate_seo_fields, generate_internal_link_suggestions
)
from flask import url_for

# SEO models - will be defined inside register_seo_admin_routes to avoid circular imports
PostSEO = None
PostImage = None
PostDraft = None

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
UPLOAD_FOLDER = 'static/uploads'


def create_slug(text):
    """Create URL-friendly slug"""
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug[:100]


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def register_seo_admin_routes(app, db, Post, Category):
    """Register SEO-optimized admin routes"""
    
    # Define SEO models here to avoid circular imports
    global PostSEO, PostImage, PostDraft
    
    if PostSEO is None:
        class _PostSEO(db.Model):
            """SEO metadata for blog posts"""
            __tablename__ = 'post_seo'
            id = db.Column(db.Integer, primary_key=True)
            post_id = db.Column(db.Integer, db.ForeignKey('post.id'), unique=True, nullable=False)
            primary_keyword = db.Column(db.String(200))
            secondary_keywords = db.Column(db.Text)
            meta_title = db.Column(db.String(70))
            meta_description = db.Column(db.String(160))
            og_title = db.Column(db.String(100))
            og_description = db.Column(db.Text)
            og_image = db.Column(db.String(500))
            twitter_title = db.Column(db.String(100))
            twitter_description = db.Column(db.Text)
            twitter_image = db.Column(db.String(500))
            canonical_url = db.Column(db.String(500))
            schema_type = db.Column(db.String(50), default='Article')
            reading_time = db.Column(db.Integer)
            word_count = db.Column(db.Integer)
            seo_score = db.Column(db.Integer, default=0)
            keyword_density = db.Column(db.Float)
            created_at = db.Column(db.DateTime, default=datetime.utcnow)
            updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        class _PostImage(db.Model):
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
        
        class _PostDraft(db.Model):
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
        
        # Assign to global variables
        PostSEO = _PostSEO
        PostImage = _PostImage
        PostDraft = _PostDraft
    
    # Ensure upload directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    @app.route('/admin')
    @app.route('/admin/seo')
    def admin_seo_dashboard():
        """SEO Dashboard - Main admin entry point"""
        total_posts = Post.query.count()
        # Count published posts (handle both old and new status field)
        try:
            published_posts = Post.query.filter_by(status='published').count()
        except:
            published_posts = Post.query.count()  # Fallback if status column doesn't exist
        
        try:
            draft_posts = Post.query.filter_by(status='draft').count()
        except:
            draft_posts = 0
        
        # Calculate average SEO score (if PostSEO exists)
        avg_seo_score = 0
        if PostSEO:
            try:
                seo_records = PostSEO.query.all()
                if seo_records:
                    scores = [s.seo_score for s in seo_records if s.seo_score]
                    avg_seo_score = sum(scores) / len(scores) if scores else 0
            except:
                pass
        
        recent_posts = Post.query.order_by(Post.created_at.desc()).limit(10).all()
        
        return render_template('admin/seo_dashboard.html',
                             total_posts=total_posts,
                             published_posts=published_posts,
                             draft_posts=draft_posts,
                             avg_seo_score=round(avg_seo_score, 1),
                             recent_posts=recent_posts)
    
    @app.route('/admin/posts/new', methods=['GET', 'POST'])
    @app.route('/admin/seo/posts/new', methods=['GET', 'POST'])
    def admin_seo_new_post():
        """Create new post with SEO optimization"""
        if request.method == 'POST':
            # Get form data
            title = request.form.get('title', '').strip()
            slug = request.form.get('slug', '').strip()
            content = request.form.get('content', '').strip()
            excerpt = request.form.get('excerpt', '').strip()
            author = request.form.get('author', 'Admin').strip() or 'Admin'
            category_names = request.form.getlist('categories')
            featured_image = request.form.get('featured_image', '').strip()
            status = request.form.get('status', 'draft').strip()
            published_date_str = request.form.get('published_date', '')
            
            # Get SEO data
            seo_data = {
                'primary_keyword': request.form.get('primary_keyword', '').strip(),
                'secondary_keywords': request.form.get('secondary_keywords', '').strip(),
                'meta_title': request.form.get('meta_title', '').strip(),
                'meta_description': request.form.get('meta_description', '').strip(),
                'og_title': request.form.get('og_title', '').strip(),
                'og_description': request.form.get('og_description', '').strip(),
                'og_image': request.form.get('og_image', '').strip(),
                'twitter_title': request.form.get('twitter_title', '').strip(),
                'twitter_description': request.form.get('twitter_description', '').strip(),
                'twitter_image': request.form.get('twitter_image', '').strip(),
                'canonical_url': request.form.get('canonical_url', '').strip(),
                'schema_type': request.form.get('schema_type', 'Article').strip(),
            }
            
            # Validation
            errors = []
            if not title:
                errors.append('Title is required')
            if not content:
                errors.append('Content is required')
            if not slug:
                slug = create_slug(title)
            
            # SEO validation
            seo_errors, seo_warnings = validate_seo_fields(seo_data)
            errors.extend(seo_errors)
            
            if errors:
                for error in errors:
                    flash(error, 'error')
                # Return to form with data
                categories = Category.query.all()
                today_date = datetime.now().strftime('%Y-%m-%d')
                return render_template('admin/seo_new_post.html',
                                     categories=categories,
                                     today_date=today_date,
                                     form_data=request.form,
                                     seo_data=seo_data,
                                     errors=errors,
                                     warnings=seo_warnings)
            
            # Check if slug exists
            existing = Post.query.filter_by(slug=slug).first()
            if existing:
                flash(f'A post with slug "{slug}" already exists!', 'error')
                categories = Category.query.all()
                today_date = datetime.now().strftime('%Y-%m-%d')
                return render_template('admin/seo_new_post.html',
                                     categories=categories,
                                     today_date=today_date,
                                     form_data=request.form,
                                     seo_data=seo_data)
            
            # Process content
            processed_content = process_blog_content(content)
            
            # Calculate SEO metrics
            word_count = calculate_word_count(content)
            reading_time = calculate_reading_time(content)
            keyword_density = 0
            if seo_data['primary_keyword']:
                keyword_density = calculate_keyword_density(content, seo_data['primary_keyword'])
            
            # Parse date
            if published_date_str:
                try:
                    published_date = datetime.strptime(published_date_str, '%Y-%m-%d')
                except ValueError:
                    published_date = datetime.now()
            else:
                published_date = datetime.now()
            
            # Create post
            post = Post(
                title=title,
                slug=slug,
                content=processed_content,
                excerpt=excerpt,
                featured_image=featured_image,
                published_date=published_date,
                author=author,
                status=status
            )
            
            # Handle categories
            categories_list = []
            for cat_name in category_names:
                if cat_name:
                    cat_slug = create_slug(cat_name)
                    category = Category.query.filter_by(slug=cat_slug).first()
                    if not category:
                        category = Category(name=cat_name, slug=cat_slug)
                        db.session.add(category)
                        db.session.flush()
                    categories_list.append(category)
            
            post.categories = categories_list
            
            try:
                db.session.add(post)
                db.session.flush()  # Get post.id
                
                # Create SEO record
                try:
                    seo_score = calculate_seo_score(post, seo_data)
                    post_seo = PostSEO(
                        post_id=post.id,
                        primary_keyword=seo_data['primary_keyword'],
                        secondary_keywords=seo_data['secondary_keywords'],
                        meta_title=seo_data['meta_title'],
                        meta_description=seo_data['meta_description'],
                        og_title=seo_data['og_title'] or seo_data['meta_title'],
                        og_description=seo_data['og_description'] or seo_data['meta_description'],
                        og_image=seo_data['og_image'] or featured_image,
                        twitter_title=seo_data['twitter_title'] or seo_data['meta_title'],
                        twitter_description=seo_data['twitter_description'] or seo_data['meta_description'],
                        twitter_image=seo_data['twitter_image'] or featured_image,
                        canonical_url=seo_data['canonical_url'],
                        schema_type=seo_data['schema_type'],
                        reading_time=reading_time,
                        word_count=word_count,
                        keyword_density=keyword_density,
                        seo_score=seo_score
                    )
                    db.session.add(post_seo)
                except Exception as seo_error:
                    flash(f'Warning: SEO data could not be saved ({seo_error})', 'warning')
                    seo_score = None
                
                db.session.commit()
                
                # Show warnings if any
                for warning in seo_warnings:
                    flash(warning, 'warning')
                
                flash(f'Post "{title}" created successfully! SEO Score: {seo_score if PostSEO else "N/A"}', 'success')
                return redirect(url_for('admin_seo_posts'))
            except Exception as e:
                flash(f'Error creating post: {str(e)}', 'error')
                db.session.rollback()
                categories = Category.query.all()
                today_date = datetime.now().strftime('%Y-%m-%d')
                # Convert form data to dict with categories as list
                form_data_dict = dict(request.form)
                form_data_dict['categories'] = request.form.getlist('categories')
                return render_template('admin/seo_new_post.html',
                                     categories=categories,
                                     today_date=today_date,
                                     form_data=form_data_dict,
                                     seo_data=seo_data)
        
        # GET request - show form
        categories = Category.query.all()
        today_date = datetime.now().strftime('%Y-%m-%d')
        return render_template('admin/seo_new_post.html',
                             categories=categories,
                             today_date=today_date)
    
    @app.route('/admin/seo/posts/<int:post_id>/edit', methods=['GET', 'POST'])
    def admin_seo_edit_post(post_id):
        """Edit existing post with SEO optimization"""
        post = Post.query.get_or_404(post_id)
        
        if request.method == 'POST':
            # Get form data
            title = request.form.get('title', '').strip()
            slug = request.form.get('slug', '').strip()
            content = request.form.get('content', '').strip()
            excerpt = request.form.get('excerpt', '').strip()
            author = request.form.get('author', 'Admin').strip() or 'Admin'
            featured_image = request.form.get('featured_image', '').strip()
            status = request.form.get('status', 'published').strip()
            published_date_str = request.form.get('published_date', '')
            category_names = request.form.getlist('categories')
            
            # SEO data
            seo_data = {
                'primary_keyword': request.form.get('primary_keyword', '').strip(),
                'secondary_keywords': request.form.get('secondary_keywords', '').strip(),
                'meta_title': request.form.get('meta_title', '').strip(),
                'meta_description': request.form.get('meta_description', '').strip(),
                'og_title': request.form.get('og_title', '').strip(),
                'og_description': request.form.get('og_description', '').strip(),
                'og_image': request.form.get('og_image', '').strip(),
                'twitter_title': request.form.get('twitter_title', '').strip(),
                'twitter_description': request.form.get('twitter_description', '').strip(),
                'twitter_image': request.form.get('twitter_image', '').strip(),
                'canonical_url': request.form.get('canonical_url', '').strip(),
                'schema_type': request.form.get('schema_type', 'Article').strip()
            }
            
            # Validate
            if not title or not content:
                flash('Title and content are required!', 'error')
                categories = Category.query.all()
                post_categories = post.categories.all()
                today_date = datetime.now().strftime('%Y-%m-%d')
                return render_template('admin/seo_edit_post.html',
                                     post=post,
                                     categories=categories,
                                     post_categories=post_categories,
                                     today_date=today_date,
                                     form_data=request.form,
                                     seo_data=seo_data)
            
            # Validate SEO fields
            seo_warnings = validate_seo_fields(seo_data)
            
            # Update slug if title changed
            if title != post.title:
                new_slug = create_slug(title)
                if new_slug != post.slug:
                    existing = Post.query.filter_by(slug=new_slug).first()
                    if existing and existing.id != post.id:
                        flash(f'A post with slug "{new_slug}" already exists!', 'error')
                        categories = Category.query.all()
                        post_categories = post.categories.all()
                        today_date = datetime.now().strftime('%Y-%m-%d')
                        return render_template('admin/seo_edit_post.html',
                                             post=post,
                                             categories=categories,
                                             post_categories=post_categories,
                                             today_date=today_date,
                                             form_data=request.form,
                                             seo_data=seo_data)
                    post.slug = new_slug
            
            # Update post
            post.title = title
            post.content = process_blog_content(content)
            post.excerpt = excerpt
            post.author = author
            post.featured_image = featured_image
            post.status = status
            post.updated_at = datetime.now()
            
            # Parse date
            if published_date_str:
                try:
                    post.published_date = datetime.strptime(published_date_str, '%Y-%m-%d')
                except ValueError:
                    pass
            
            # Update categories
            categories_list = []
            for cat_name in category_names:
                if cat_name:
                    cat_slug = create_slug(cat_name)
                    category = Category.query.filter_by(slug=cat_slug).first()
                    if not category:
                        category = Category(name=cat_name, slug=cat_slug)
                        db.session.add(category)
                        db.session.flush()
                    categories_list.append(category)
            
            post.categories = categories_list
            
            # Calculate SEO metrics
            word_count = calculate_word_count(content)
            reading_time = calculate_reading_time(content)
            keyword_density = 0
            if seo_data['primary_keyword']:
                keyword_density = calculate_keyword_density(content, seo_data['primary_keyword'])
            
            try:
                db.session.flush()
                
                # Update or create SEO record
                try:
                    seo_score = calculate_seo_score(post, seo_data)
                    post_seo = PostSEO.query.filter_by(post_id=post.id).first()
                    if post_seo:
                        # Update existing
                        post_seo.primary_keyword = seo_data['primary_keyword']
                        post_seo.secondary_keywords = seo_data['secondary_keywords']
                        post_seo.meta_title = seo_data['meta_title']
                        post_seo.meta_description = seo_data['meta_description']
                        post_seo.og_title = seo_data['og_title'] or seo_data['meta_title']
                        post_seo.og_description = seo_data['og_description'] or seo_data['meta_description']
                        post_seo.og_image = seo_data['og_image'] or featured_image
                        post_seo.twitter_title = seo_data['twitter_title'] or seo_data['meta_title']
                        post_seo.twitter_description = seo_data['twitter_description'] or seo_data['meta_description']
                        post_seo.twitter_image = seo_data['twitter_image'] or featured_image
                        post_seo.canonical_url = seo_data['canonical_url']
                        post_seo.schema_type = seo_data['schema_type']
                        post_seo.reading_time = reading_time
                        post_seo.word_count = word_count
                        post_seo.keyword_density = keyword_density
                        post_seo.seo_score = seo_score
                        post_seo.updated_at = datetime.now()
                    else:
                        # Create new
                        post_seo = PostSEO(
                            post_id=post.id,
                            primary_keyword=seo_data['primary_keyword'],
                            secondary_keywords=seo_data['secondary_keywords'],
                            meta_title=seo_data['meta_title'],
                            meta_description=seo_data['meta_description'],
                            og_title=seo_data['og_title'] or seo_data['meta_title'],
                            og_description=seo_data['og_description'] or seo_data['meta_description'],
                            og_image=seo_data['og_image'] or featured_image,
                            twitter_title=seo_data['twitter_title'] or seo_data['meta_title'],
                            twitter_description=seo_data['twitter_description'] or seo_data['meta_description'],
                            twitter_image=seo_data['twitter_image'] or featured_image,
                            canonical_url=seo_data['canonical_url'],
                            schema_type=seo_data['schema_type'],
                            reading_time=reading_time,
                            word_count=word_count,
                            keyword_density=keyword_density,
                            seo_score=seo_score
                        )
                        db.session.add(post_seo)
                except Exception as seo_error:
                    flash(f'Warning: SEO data could not be saved ({seo_error})', 'warning')
                    seo_score = None
                
                db.session.commit()
                
                # Show warnings if any
                for warning in seo_warnings:
                    flash(warning, 'warning')
                
                flash(f'Post "{title}" updated successfully! SEO Score: {seo_score if seo_score else "N/A"}', 'success')
                return redirect(url_for('admin_seo_posts'))
            except Exception as e:
                flash(f'Error updating post: {str(e)}', 'error')
                db.session.rollback()
                categories = Category.query.all()
                post_categories = post.categories.all()
                today_date = datetime.now().strftime('%Y-%m-%d')
                return render_template('admin/seo_edit_post.html',
                                     post=post,
                                     categories=categories,
                                     post_categories=post_categories,
                                     today_date=today_date,
                                     form_data=request.form,
                                     seo_data=seo_data)
        
        # GET request - show form
        categories = Category.query.all()
        post_categories = post.categories.all()
        today_date = datetime.now().strftime('%Y-%m-%d')
        
        # Get existing SEO data
        seo_data = None
        try:
            seo_data_obj = PostSEO.query.filter_by(post_id=post.id).first()
            if seo_data_obj:
                seo_data = {
                    'primary_keyword': seo_data_obj.primary_keyword if seo_data_obj.primary_keyword else '',
                    'secondary_keywords': seo_data_obj.secondary_keywords if seo_data_obj.secondary_keywords else '',
                    'meta_title': seo_data_obj.meta_title if seo_data_obj.meta_title else '',
                    'meta_description': seo_data_obj.meta_description if seo_data_obj.meta_description else '',
                    'og_title': seo_data_obj.og_title if seo_data_obj.og_title else '',
                    'og_description': seo_data_obj.og_description if seo_data_obj.og_description else '',
                    'og_image': seo_data_obj.og_image if seo_data_obj.og_image else '',
                    'twitter_title': seo_data_obj.twitter_title if seo_data_obj.twitter_title else '',
                    'twitter_description': seo_data_obj.twitter_description if seo_data_obj.twitter_description else '',
                    'twitter_image': seo_data_obj.twitter_image if seo_data_obj.twitter_image else '',
                    'canonical_url': seo_data_obj.canonical_url if seo_data_obj.canonical_url else '',
                    'schema_type': seo_data_obj.schema_type if seo_data_obj.schema_type else 'Article'
                }
                print(f"DEBUG: Loaded SEO data for post {post.id}: primary_keyword={seo_data['primary_keyword']}, meta_title={seo_data['meta_title']}")
            else:
                print(f"DEBUG: No SEO data found for post {post.id}")
        except Exception as e:
            print(f"DEBUG: Error loading SEO data: {str(e)}")
            import traceback
            traceback.print_exc()
            # Continue with empty seo_data
        
        # Prepare form data
        form_data = {
            'title': post.title,
            'slug': post.slug,
            'content': post.content,
            'excerpt': post.excerpt or '',
            'author': post.author,
            'featured_image': post.featured_image or '',
            'status': post.status,
            'published_date': post.published_date.strftime('%Y-%m-%d') if post.published_date else today_date
        }
        
        # Ensure seo_data is always a dict (never None)
        if not seo_data:
            seo_data = {
                'primary_keyword': '',
                'secondary_keywords': '',
                'meta_title': '',
                'meta_description': '',
                'og_title': '',
                'og_description': '',
                'og_image': '',
                'twitter_title': '',
                'twitter_description': '',
                'twitter_image': '',
                'canonical_url': '',
                'schema_type': 'Article'
            }
        
        # Debug: Print SEO data to verify it's being loaded
        print(f"DEBUG: Rendering edit form for post {post.id}")
        print(f"DEBUG: SEO data keys: {list(seo_data.keys()) if seo_data else 'None'}")
        print(f"DEBUG: Primary keyword: '{seo_data.get('primary_keyword', 'NOT FOUND')}'")
        print(f"DEBUG: Meta title: '{seo_data.get('meta_title', 'NOT FOUND')}'")
        
        return render_template('admin/seo_edit_post.html',
                             post=post,
                             categories=categories,
                             post_categories=post_categories,
                             today_date=today_date,
                             form_data=form_data,
                             seo_data=seo_data)
    
    @app.route('/admin/posts')
    @app.route('/admin/seo/posts')
    def admin_seo_posts():
        """List all posts with SEO scores"""
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        posts = Post.query.order_by(Post.published_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get SEO scores
        seo_scores = {}
        try:
            for post in posts.items:
                seo = PostSEO.query.filter_by(post_id=post.id).first()
                if seo:
                    seo_scores[post.id] = seo.seo_score
        except:
            pass  # Table doesn't exist yet
        
        return render_template('admin/seo_posts.html', posts=posts, seo_scores=seo_scores)
    
    @app.route('/admin/seo/posts/<int:post_id>/delete', methods=['POST'])
    def admin_seo_delete_post(post_id):
        """Delete a post and its related SEO data"""
        post = Post.query.get_or_404(post_id)
        title = post.title
        
        try:
            # IMPORTANT: Delete child records FIRST to avoid foreign key constraint errors
            # Use raw SQL if needed to ensure deletions happen
            
            # 1. Clear categories relationship (many-to-many)
            post.categories = []
            db.session.flush()
            
            # 2. Delete related SEO data - use raw SQL first to ensure it works
            # This is more reliable than ORM for foreign key constraints
            try:
                # Use raw SQL directly - more reliable for FK constraints
                result = db.session.execute(
                    text("DELETE FROM post_seo WHERE post_id = :post_id"),
                    {"post_id": post_id}
                )
                db.session.flush()
                print(f"Deleted {result.rowcount} SEO record(s) for post {post_id}")
            except Exception as e:
                # If table doesn't exist or other error, try ORM as fallback
                try:
                    seo_records = PostSEO.query.filter_by(post_id=post_id).all()
                    if seo_records:
                        for seo in seo_records:
                            db.session.delete(seo)
                        db.session.flush()
                        print(f"Deleted {len(seo_records)} SEO record(s) via ORM for post {post_id}")
                except Exception as orm_e:
                    print(f"Note: Could not delete SEO records: {str(orm_e)}")
                    # Don't rollback - continue with other deletions
            
            # 3. Delete related images
            try:
                images = PostImage.query.filter_by(post_id=post_id).all()
                for img in images:
                    # Optionally delete image file from filesystem
                    if img.image_url and img.image_url.startswith('/static/uploads/'):
                        image_path = img.image_url.replace('/static/', 'static/')
                        if os.path.exists(image_path):
                            try:
                                os.remove(image_path)
                            except:
                                pass  # Ignore file deletion errors
                    db.session.delete(img)
                if images:
                    db.session.flush()
                
                # Backup: raw SQL
                db.session.execute(
                    text("DELETE FROM post_images WHERE post_id = :post_id"),
                    {"post_id": post_id}
                )
                db.session.flush()
            except Exception as e:
                try:
                    db.session.execute(
                        text("DELETE FROM post_images WHERE post_id = :post_id"),
                        {"post_id": post_id}
                    )
                    db.session.flush()
                except:
                    print(f"Note: Could not delete image records: {str(e)}")
            
            # 4. Delete drafts
            try:
                drafts = PostDraft.query.filter_by(post_id=post_id).all()
                for draft in drafts:
                    db.session.delete(draft)
                if drafts:
                    db.session.flush()
                
                # Backup: raw SQL
                db.session.execute(
                    text("DELETE FROM post_drafts WHERE post_id = :post_id"),
                    {"post_id": post_id}
                )
                db.session.flush()
            except Exception as e:
                try:
                    db.session.execute(
                        text("DELETE FROM post_drafts WHERE post_id = :post_id"),
                        {"post_id": post_id}
                    )
                    db.session.flush()
                except:
                    print(f"Note: Could not delete draft records: {str(e)}")
            
            # 5. Now delete the post (parent record) - all child records should be gone
            db.session.delete(post)
            db.session.commit()
            flash(f'Post "{title}" deleted successfully!', 'success')
        except Exception as e:
            flash(f'Error deleting post: {str(e)}', 'error')
            db.session.rollback()
            import traceback
            traceback.print_exc()
        
        return redirect(url_for('admin_seo_posts'))
    
    @app.route('/admin/posts/<int:post_id>')
    @app.route('/admin/seo/posts/<int:post_id>')
    def admin_seo_post_detail(post_id):
        """View post with SEO analysis"""
        post = Post.query.get_or_404(post_id)
        
        # Get SEO data
        seo_data = None
        calculated_seo_score = None
        try:
            seo_data = PostSEO.query.filter_by(post_id=post.id).first()
        except:
            pass  # Table doesn't exist yet
        
        # Calculate current metrics
        word_count = calculate_word_count(post.content)
        reading_time = calculate_reading_time(post.content)
        try:
            headings = extract_headings(post.content)
        except Exception as e:
            headings = []
            flash(f'Could not extract headings: {str(e)}', 'warning')
        
        # Calculate SEO score if not available
        if seo_data and seo_data.seo_score:
            calculated_seo_score = seo_data.seo_score
        else:
            # Calculate on-the-fly for posts without SEO data
            try:
                seo_data_dict = {
                    'meta_title': seo_data.meta_title if seo_data else '',
                    'meta_description': seo_data.meta_description if seo_data else '',
                    'primary_keyword': seo_data.primary_keyword if seo_data else '',
                    'keyword_density': seo_data.keyword_density if seo_data and seo_data.primary_keyword else None,
                    'og_title': seo_data.og_title if seo_data else '',
                    'og_description': seo_data.og_description if seo_data else ''
                }
                if seo_data and seo_data.primary_keyword:
                    # Calculate keyword density if not set
                    if not seo_data_dict['keyword_density']:
                        seo_data_dict['keyword_density'] = calculate_keyword_density(post.content, seo_data.primary_keyword)
                calculated_seo_score = calculate_seo_score(post, seo_data_dict)
            except Exception as e:
                print(f"Could not calculate SEO score: {str(e)}")
                calculated_seo_score = None
        
        # Get suggestions (guarded to avoid breaking the page)
        suggestions = {'headings': [], 'faqs': [], 'internal_links': []}
        try:
            primary_kw = seo_data.primary_keyword if seo_data else ''
            suggestions['headings'] = suggest_headings(post.content, primary_kw)
            suggestions['faqs'] = suggest_faqs(post.content, primary_kw)
            suggestions['internal_links'] = generate_internal_link_suggestions(post.title, Post.query.filter(Post.id != post.id).all())
        except Exception as e:
            flash(f'SEO suggestions unavailable: {str(e)}', 'warning')
        
        return render_template('admin/seo_post_detail.html',
                             post=post,
                             seo_data=seo_data,
                             seo_score=calculated_seo_score,
                             word_count=word_count,
                             reading_time=reading_time,
                             headings=headings,
                             suggestions=suggestions)
    
    @app.route('/admin/seo/api/suggestions', methods=['POST'])
    def api_seo_suggestions():
        """API endpoint for SEO suggestions"""
        data = request.get_json()
        title = data.get('title', '')
        content = data.get('content', '')
        keyword = data.get('keyword', '')
        
        suggestions = {
            'meta_description': generate_meta_description(content, keyword=keyword),
            'headings': suggest_headings(content, keyword),
            'faqs': suggest_faqs(content, keyword),
            'word_count': calculate_word_count(content),
            'reading_time': calculate_reading_time(content),
        }
        
        if keyword:
            suggestions['keyword_density'] = calculate_keyword_density(content, keyword)
        
        return jsonify(suggestions)
    
    @app.route('/admin/seo/api/auto-generate-seo', methods=['POST'])
    def api_auto_generate_seo():
        """API endpoint to auto-generate all SEO fields"""
        try:
            from seo_utils import (
                generate_meta_title, generate_meta_description,
                extract_primary_keyword, generate_secondary_keywords,
                generate_og_tags, generate_twitter_tags
            )
            
            data = request.get_json()
            title = data.get('title', '').strip()
            content = data.get('content', '').strip()
            existing_keyword = data.get('existing_keyword', '').strip()
            
            if not title:
                return jsonify({'success': False, 'message': 'Title is required'}), 400
            
            # Extract primary keyword
            primary_keyword = existing_keyword or extract_primary_keyword(title, content)
            
            # Generate secondary keywords
            secondary_keywords = generate_secondary_keywords(primary_keyword, content)
            
            # Generate meta title
            meta_title = generate_meta_title(title, primary_keyword)
            
            # Generate meta description
            meta_description = generate_meta_description(content, keyword=primary_keyword)
            
            # Generate OG tags
            og_tags = generate_og_tags(title, meta_description, primary_keyword)
            
            # Generate Twitter tags
            twitter_tags = generate_twitter_tags(title, meta_description, primary_keyword)
            
            return jsonify({
                'success': True,
                'data': {
                    'primary_keyword': primary_keyword,
                    'secondary_keywords': secondary_keywords,
                    'meta_title': meta_title,
                    'meta_description': meta_description,
                    'og_title': og_tags['og_title'],
                    'og_description': og_tags['og_description'],
                    'twitter_title': twitter_tags['twitter_title'],
                    'twitter_description': twitter_tags['twitter_description']
                }
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    
    @app.route('/admin/seo/api/preview', methods=['POST'])
    def api_seo_preview():
        """API endpoint for post preview"""
        data = request.get_json()
        
        preview_data = {
            'title': data.get('title', ''),
            'content': data.get('content', ''),
            'meta_title': data.get('meta_title', ''),
            'meta_description': data.get('meta_description', ''),
            'url': f"/post/{data.get('slug', '')}",
        }
        
        return jsonify(preview_data)
    
    @app.route('/admin/seo/upload', methods=['POST'])
    def admin_seo_upload_image():
        """Upload image for blog post"""
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to avoid conflicts
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Ensure directory exists
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file.save(filepath)
            
            # Return URL (relative path starting with /)
            url = f'/static/uploads/{filename}'
            return jsonify({'url': url, 'filename': filename})
        
        return jsonify({'error': 'Invalid file type'}), 400
    
    @app.route('/admin/seo/api/generate-post', methods=['POST'])
    def api_generate_ai_post():
        """API endpoint to generate AI SEO-optimized post"""
        try:
            data = request.get_json()
            topic = data.get('topic', '').strip()
            provider = data.get('provider', 'openai')  # 'openai' or 'anthropic'
            api_key = data.get('api_key')  # Optional, uses env var if not provided
            post_id = data.get('post_id')  # Optional, for regenerating existing post
            
            if not topic:
                return jsonify({'success': False, 'message': 'Topic is required'}), 400
            
            # Import AI post generator
            from ai_post_generator import generate_seo_post
            
            # Generate content
            generated_data = generate_seo_post(topic, api_key, provider)
            
            if generated_data:
                return jsonify({
                    'success': True,
                    'data': generated_data,
                    'message': 'AI content generated successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to generate content. Please check your API key (OPENAI_API_KEY or ANTHROPIC_API_KEY)'
                }), 500
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    
    @app.route('/admin/seo/api/regenerate-post', methods=['POST'])
    def api_regenerate_ai_post():
        """API endpoint to regenerate AI content for existing post"""
        try:
            data = request.get_json()
            post_id = data.get('post_id')
            provider = data.get('provider', 'openai')
            api_key = data.get('api_key')
            
            if not post_id:
                return jsonify({'success': False, 'message': 'Post ID is required'}), 400
            
            post = Post.query.get_or_404(post_id)
            
            # Use post title as topic, or generate from content
            topic = post.title
            if not topic or len(topic) < 5:
                # Extract topic from content
                import re
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(post.content, 'html.parser')
                text = soup.get_text()[:200]
                topic = text.split('.')[0] if text else 'Blog Post'
            
            # Import AI post generator
            from ai_post_generator import generate_seo_post
            
            # Generate new content
            generated_data = generate_seo_post(topic, api_key, provider)
            
            if generated_data:
                return jsonify({
                    'success': True,
                    'data': generated_data,
                    'message': 'AI content regenerated successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to regenerate content. Please check your API key'
                }), 500
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

