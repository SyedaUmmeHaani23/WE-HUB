"""
Community routes for Women Entrepreneurs Hub.
Handles forum posts, discussions, and community features.
"""
import logging
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from app import db, firestore_db
from models import User, ForumPost, ForumComment
import firebase_admin
from datetime import datetime

bp = Blueprint('community', __name__, url_prefix='/community')

@bp.route('/', methods=['GET'])
def index():
    """Render the community homepage."""
    # Check if user is logged in
    user_data = session.get('user_data')
    
    return render_template(
        'community.html',
        user_data=user_data
    )

@bp.route('/forum', methods=['GET'])
def forum():
    """View the forum with all posts."""
    # Get category filter from query parameters
    category = request.args.get('category')
    
    # Get forum posts
    try:
        # Query posts from the database
        if category and category != 'all':
            posts_query = ForumPost.query.filter_by(category=category)
        else:
            posts_query = ForumPost.query
        
        # Add pagination
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Number of posts per page
        pagination = posts_query.order_by(ForumPost.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        posts = pagination.items
        
        # Get post authors and comment counts
        for post in posts:
            post.author = User.query.get(post.user_id)
            post.comment_count = ForumComment.query.filter_by(post_id=post.id).count()
        
        return render_template(
            'forum.html',
            posts=posts,
            category=category,
            pagination=pagination,
            user_data=session.get('user_data')
        )
    
    except Exception as e:
        logging.error(f"Error loading forum page: {e}")
        return render_template(
            'forum.html',
            posts=[],
            category=category,
            error="An error occurred while loading forum posts.",
            user_data=session.get('user_data')
        )

@bp.route('/forum/post/<int:post_id>', methods=['GET'])
def view_post(post_id):
    """View a single forum post with comments."""
    try:
        # Get post from database
        post = ForumPost.query.get_or_404(post_id)
        post.author = User.query.get(post.user_id)
        
        # Get comments
        comments = ForumComment.query.filter_by(post_id=post_id).order_by(ForumComment.created_at.asc()).all()
        
        # Get comment authors
        for comment in comments:
            comment.author = User.query.get(comment.user_id)
        
        return render_template(
            'forum-post.html',
            post=post,
            comments=comments,
            user_data=session.get('user_data')
        )
    
    except Exception as e:
        logging.error(f"Error viewing post {post_id}: {e}")
        return redirect(url_for('community.forum'))

@bp.route('/forum/new', methods=['GET'])
def new_post_form():
    """Render the form to create a new forum post."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return redirect(url_for('auth.login'))
    
    return render_template(
        'new-post.html',
        user_data=user_data
    )

@bp.route('/api/forum/posts', methods=['POST'])
def create_post():
    """Create a new forum post."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        # Get JSON data
        data = request.json
        
        # Validate required fields
        required_fields = ['title', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # Get user ID
        user_id = user_data.get('id')
        
        # Create new post
        post = ForumPost(
            user_id=user_id,
            firebase_id=data.get('firebase_id'),
            title=data.get('title'),
            content=data.get('content'),
            category=data.get('category'),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add to database
        db.session.add(post)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Post created successfully',
            'post_id': post.id
        })
    
    except Exception as e:
        logging.error(f"Error creating post: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/forum/posts/<post_id>', methods=['PUT'])
def update_post(post_id):
    """Update an existing forum post."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        # Get post from database
        post = ForumPost.query.get(post_id)
        if not post:
            return jsonify({'success': False, 'message': 'Post not found'}), 404
        
        # Check if the post belongs to the current user
        if post.user_id != user_data.get('id'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Get JSON data
        data = request.json
        
        # Update post fields
        if 'title' in data:
            post.title = data.get('title')
        
        if 'content' in data:
            post.content = data.get('content')
        
        if 'category' in data:
            post.category = data.get('category')
        
        post.updated_at = datetime.utcnow()
        
        # Update database
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Post updated successfully'
        })
    
    except Exception as e:
        logging.error(f"Error updating post {post_id}: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/forum/posts/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Delete a forum post."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        # Get post from database
        post = ForumPost.query.get(post_id)
        if not post:
            return jsonify({'success': False, 'message': 'Post not found'}), 404
        
        # Check if the post belongs to the current user
        if post.user_id != user_data.get('id'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Delete all comments on the post
        ForumComment.query.filter_by(post_id=post.id).delete()
        
        # Delete the post
        db.session.delete(post)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Post deleted successfully'
        })
    
    except Exception as e:
        logging.error(f"Error deleting post {post_id}: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/forum/comments', methods=['POST'])
def create_comment():
    """Create a new comment on a forum post."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        # Get JSON data
        data = request.json
        
        # Validate required fields
        required_fields = ['post_id', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # Get user ID
        user_id = user_data.get('id')
        
        # Check if post exists
        post_id = data.get('post_id')
        post = ForumPost.query.get(post_id)
        if not post:
            return jsonify({'success': False, 'message': 'Post not found'}), 404
        
        # Create new comment
        comment = ForumComment(
            post_id=post_id,
            user_id=user_id,
            firebase_id=data.get('firebase_id'),
            content=data.get('content'),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add to database
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Comment created successfully',
            'comment_id': comment.id
        })
    
    except Exception as e:
        logging.error(f"Error creating comment: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/community/stats', methods=['GET'])
def get_community_stats():
    """Get community statistics."""
    try:
        # Get total members (users)
        total_members = User.query.count()
        
        # Get active discussions (posts in the last 30 days)
        thirty_days_ago = datetime.utcnow() - firebase_admin.datetime.timedelta(days=30)
        active_discussions = ForumPost.query.filter(ForumPost.created_at >= thirty_days_ago).count()
        
        # Get posts this week
        seven_days_ago = datetime.utcnow() - firebase_admin.datetime.timedelta(days=7)
        weekly_posts = ForumPost.query.filter(ForumPost.created_at >= seven_days_ago).count()
        
        return jsonify({
            'success': True,
            'total_members': total_members,
            'active_discussions': active_discussions,
            'weekly_posts': weekly_posts
        })
    
    except Exception as e:
        logging.error(f"Error getting community stats: {e}")
        return jsonify({
            'success': False,
            'message': 'Error getting community statistics',
            'total_members': 0,
            'active_discussions': 0,
            'weekly_posts': 0
        }), 500

@bp.route('/mentorship', methods=['GET'])
def mentorship():
    """View the mentorship program page."""
    return render_template(
        'mentorship.html',
        user_data=session.get('user_data')
    )
