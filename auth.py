"""
Simple authentication for admin panel
"""
from functools import wraps
from flask import session, redirect, url_for, request, flash
import os

# Admin credentials (can be moved to environment variables)
# You can set these via environment variables: ADMIN_USERNAME and ADMIN_PASSWORD
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')  # Change this in production!


def login_required(f):
    """Decorator to require login for admin routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please login to access the admin panel', 'warning')
            return redirect(url_for('admin_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def init_auth_routes(app):
    """Initialize authentication routes"""
    
    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        """Admin login page"""
        if session.get('admin_logged_in'):
            return redirect(url_for('admin_seo_dashboard'))
        
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            next_url = request.args.get('next', url_for('admin_seo_dashboard'))
            
            # Check credentials
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                session['admin_logged_in'] = True
                session['admin_username'] = username
                flash('Login successful!', 'success')
                return redirect(next_url)
            else:
                flash('Invalid username or password', 'error')
        
        from flask import render_template
        return render_template('admin/login.html')
    
    @app.route('/admin/logout')
    def admin_logout():
        """Admin logout"""
        session.pop('admin_logged_in', None)
        session.pop('admin_username', None)
        flash('You have been logged out', 'info')
        return redirect(url_for('admin_login'))

