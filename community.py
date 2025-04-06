import logging
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from models import ForumPost, Event
from app import db
from datetime import datetime

community_bp = Blueprint('community', __name__, url_prefix='/community')

@community_bp.route('/forum')
def forum():
    """Community forum page"""
    try:
        # Get all forum posts from Firestore
        posts = []
        if db:
            post_docs = db.collection('forum_posts').order_by('created_at', direction='DESCENDING').stream()
            
            for doc in post_docs:
                post_data = doc.to_dict()
                post = {
                    'id': doc.id,
                    'title': post_data.get('title'),
                    'content': post_data.get('content'),
                    'category': post_data.get('category'),
                    'user_id': post_data.get('user_id'),
                    'created_at': post_data.get('created_at'),
                    'comments': post_data.get('comments', [])
                }
                
                # Get author information
                author_doc = db.collection('users').document(post['user_id']).get()
                if author_doc.exists:
                    author_data = author_doc.to_dict()
                    post['author'] = {
                        'display_name': author_data.get('display_name'),
                        'photo_url': author_data.get('photo_url'),
                        'business_name': author_data.get('business_data', {}).get('name')
                    }
                    
                posts.append(post)
                
        return render_template('community/forum.html', posts=posts)
    
    except Exception as e:
        logging.error(f"Error loading forum: {e}")
        flash("Error loading forum. Please try again later.", "danger")
        return render_template('community/forum.html', posts=[])

@community_bp.route('/forum/post/<post_id>')
def forum_post(post_id):
    """Individual forum post page"""
    try:
        post = ForumPost.get(post_id)
        if not post:
            flash("Post not found.", "warning")
            return redirect(url_for('community.forum'))
            
        # Get author information
        author = None
        if db:
            author_doc = db.collection('users').document(post.user_id).get()
            if author_doc.exists:
                author_data = author_doc.to_dict()
                author = {
                    'id': post.user_id,
                    'display_name': author_data.get('display_name'),
                    'photo_url': author_data.get('photo_url'),
                    'business_name': author_data.get('business_data', {}).get('name')
                }
                
            # Get commenter information for each comment
            for comment in post.comments:
                commenter_doc = db.collection('users').document(comment.get('user_id')).get()
                if commenter_doc.exists:
                    commenter_data = commenter_doc.to_dict()
                    comment['author'] = {
                        'display_name': commenter_data.get('display_name'),
                        'photo_url': commenter_data.get('photo_url'),
                        'business_name': commenter_data.get('business_data', {}).get('name')
                    }
                
        return render_template('community/forum_post.html', post=post, author=author)
    
    except Exception as e:
        logging.error(f"Error loading forum post: {e}")
        flash("Error loading forum post. Please try again later.", "danger")
        return redirect(url_for('community.forum'))

@community_bp.route('/forum/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """Create new forum post form and handler"""
    if request.method == 'POST':
        try:
            # Get post details from form
            title = request.form.get('title')
            content = request.form.get('content')
            category = request.form.get('category')
            
            # Create new forum post
            post = ForumPost(
                user_id=current_user.id,
                title=title,
                content=content,
                category=category
            )
            
            # Save post
            post_id = post.save()
            
            if not post_id:
                flash("Failed to create post. Please try again later.", "danger")
                return redirect(url_for('community.forum'))
                
            flash("Post created successfully!", "success")
            return redirect(url_for('community.forum_post', post_id=post_id))
            
        except Exception as e:
            logging.error(f"Error creating forum post: {e}")
            flash(f"An error occurred: {str(e)}", "danger")
            
    return render_template('community/create_post.html')

@community_bp.route('/forum/post/<post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    """Add comment to forum post"""
    try:
        post = ForumPost.get(post_id)
        if not post:
            return jsonify({'success': False, 'message': 'Post not found.'}), 404
            
        # Get comment content from request
        content = request.json.get('content')
        
        if not content:
            return jsonify({'success': False, 'message': 'Comment cannot be empty.'}), 400
            
        # Create new comment
        comment = {
            'user_id': current_user.id,
            'content': content,
            'created_at': datetime.now().isoformat()
        }
        
        # Add comment to post
        post.comments.append(comment)
        post.save()
        
        # Get commenter info for response
        commenter = {
            'display_name': current_user.display_name,
            'photo_url': current_user.photo_url,
            'business_name': current_user.business_data.get('name') if current_user.business_data else None
        }
        
        return jsonify({
            'success': True, 
            'message': 'Comment added successfully!',
            'comment': {
                'content': content,
                'created_at': comment['created_at'],
                'author': commenter
            }
        }), 200
            
    except Exception as e:
        logging.error(f"Error adding comment: {e}")
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'}), 500

@community_bp.route('/events')
def events():
    """Community events page"""
    try:
        # Get all events from Firestore
        events_list = []
        if db:
            event_docs = db.collection('events').order_by('date').stream()
            
            for doc in event_docs:
                event_data = doc.to_dict()
                event = {
                    'id': doc.id,
                    'title': event_data.get('title'),
                    'description': event_data.get('description'),
                    'date': event_data.get('date'),
                    'time': event_data.get('time'),
                    'location': event_data.get('location'),
                    'is_virtual': event_data.get('is_virtual', False),
                    'meeting_link': event_data.get('meeting_link'),
                    'user_id': event_data.get('user_id')
                }
                
                # Get organizer information
                organizer_doc = db.collection('users').document(event['user_id']).get()
                if organizer_doc.exists:
                    organizer_data = organizer_doc.to_dict()
                    event['organizer'] = {
                        'display_name': organizer_data.get('display_name'),
                        'photo_url': organizer_data.get('photo_url'),
                        'business_name': organizer_data.get('business_data', {}).get('name')
                    }
                    
                events_list.append(event)
                
        return render_template('community/events.html', events=events_list)
    
    except Exception as e:
        logging.error(f"Error loading events: {e}")
        flash("Error loading events. Please try again later.", "danger")
        return render_template('community/events.html', events=[])

@community_bp.route('/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    """Create new event form and handler"""
    if request.method == 'POST':
        try:
            # Get event details from form
            title = request.form.get('title')
            description = request.form.get('description')
            date = request.form.get('date')
            time = request.form.get('time')
            location = request.form.get('location')
            is_virtual = 'is_virtual' in request.form
            meeting_link = request.form.get('meeting_link') if is_virtual else None
            
            # Create new event
            event = Event(
                user_id=current_user.id,
                title=title,
                description=description,
                date=date,
                time=time,
                location=location,
                is_virtual=is_virtual,
                meeting_link=meeting_link
            )
            
            # Save event
            event_id = event.save()
            
            if not event_id:
                flash("Failed to create event. Please try again later.", "danger")
                return redirect(url_for('community.events'))
                
            flash("Event created successfully!", "success")
            return redirect(url_for('community.events'))
            
        except Exception as e:
            logging.error(f"Error creating event: {e}")
            flash(f"An error occurred: {str(e)}", "danger")
            
    return render_template('community/create_event.html')

@community_bp.route('/events/<event_id>')
def event_detail(event_id):
    """Event detail page"""
    try:
        event = Event.get(event_id)
        if not event:
            flash("Event not found.", "warning")
            return redirect(url_for('community.events'))
            
        # Get organizer information
        organizer = None
        if db:
            organizer_doc = db.collection('users').document(event.user_id).get()
            if organizer_doc.exists:
                organizer_data = organizer_doc.to_dict()
                organizer = {
                    'id': event.user_id,
                    'display_name': organizer_data.get('display_name'),
                    'photo_url': organizer_data.get('photo_url'),
                    'business_name': organizer_data.get('business_data', {}).get('name')
                }
                
        return render_template('community/event_detail.html', event=event, organizer=organizer)
    
    except Exception as e:
        logging.error(f"Error loading event details: {e}")
        flash("Error loading event details. Please try again later.", "danger")
        return redirect(url_for('community.events'))
