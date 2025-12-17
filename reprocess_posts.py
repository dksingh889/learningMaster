"""
Re-process existing posts in the database with the new content processor
"""
from app import app, db, Post
from utils import process_blog_content


def reprocess_all_posts():
    """Re-process all posts in the database"""
    with app.app_context():
        posts = Post.query.all()
        print(f"Found {len(posts)} posts to process...")
        
        updated = 0
        for post in posts:
            try:
                # Process the content
                processed_content = process_blog_content(post.content)
                
                # Update the post
                post.content = processed_content
                db.session.commit()
                
                updated += 1
                print(f"Updated: {post.title[:50]}...")
            except Exception as e:
                print(f"Error processing post {post.id}: {e}")
                db.session.rollback()
        
        print(f"\nRe-processing complete!")
        print(f"Updated: {updated} posts")


if __name__ == '__main__':
    reprocess_all_posts()

