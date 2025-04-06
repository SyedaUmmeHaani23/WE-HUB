"""
Authentication routes for Women Entrepreneurs Hub.
Handles user login, registration, token verification, and authentication flow.
"""
import os
import logging
from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
import firebase_admin
from firebase_admin import auth as firebase_auth
from app import db, firestore_db
from models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET'])
def login():
    """Render the login page."""
    return render_template(
        'login.html',
        firebase_api_key=os.environ.get("FIREBASE_API_KEY", ""),
        firebase_project_id=os.environ.get("FIREBASE_PROJECT_ID", ""),
        firebase_app_id=os.environ.get("FIREBASE_APP_ID", "")
    )

@bp.route('/verify-token', methods=['POST'])
def verify_token():
    """Verify Firebase ID token and create/update user in the database."""
    try:
        # Get the ID token from the POST request
        id_token = request.json.get('idToken')
        if not id_token:
            return jsonify({'success': False, 'message': 'No ID token provided'}), 400
        
        # Verify the ID token
        decoded_token = firebase_auth.verify_id_token(id_token)
        firebase_uid = decoded_token['uid']
        
        # Get user data from the decoded token
        email = decoded_token.get('email', '')
        name = decoded_token.get('name', '')
        picture = decoded_token.get('picture', '')
        
        # Check if user exists in the database
        user = User.query.filter_by(firebase_uid=firebase_uid).first()
        
        if not user:
            # Create a new user if they don't exist
            username = email.split('@')[0]  # Simple username generation
            
            # Check if username exists and modify if needed
            existing_username = User.query.filter_by(username=username).first()
            if existing_username:
                username = f"{username}{firebase_uid[:5]}"
                
            user = User(
                firebase_uid=firebase_uid,
                username=username,
                email=email,
                full_name=name,
                profile_picture=picture
            )
            db.session.add(user)
            db.session.commit()
            
            # Create the user in Firestore too
            if firestore_db:
                firestore_db.collection('users').document(firebase_uid).set({
                    'firebase_uid': firebase_uid,
                    'username': username,
                    'email': email,
                    'full_name': name,
                    'profile_picture': picture,
                    'created_at': firebase_admin.firestore.SERVER_TIMESTAMP
                })
                
            logging.info(f"Created new user: {username}")
        else:
            # Update existing user's details if needed
            if name and name != user.full_name:
                user.full_name = name
            if picture and picture != user.profile_picture:
                user.profile_picture = picture
                
            db.session.commit()
            logging.info(f"Updated existing user: {user.username}")
            
        # Store user info in session
        session['user_id'] = user.id
        session['firebase_uid'] = firebase_uid
        session['user_data'] = {
            'id': user.id,
            'firebase_uid': firebase_uid,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'profile_picture': user.profile_picture,
            'business_name': user.business_name
        }
        
        # Return a success response
        return jsonify({
            'success': True,
            'message': 'User authenticated successfully',
            'redirect': url_for('dashboard.index')
        })
        
    except firebase_auth.InvalidIdTokenError:
        logging.error('Invalid ID token')
        return jsonify({'success': False, 'message': 'Invalid token'}), 401
    except Exception as e:
        logging.error(f'Error in verify-token: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/logout', methods=['POST'])
def logout():
    """Log out the user by clearing the session."""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@bp.route('/user', methods=['GET'])
def get_user():
    """Get the current user's information."""
    user_data = session.get('user_data')
    if user_data:
        return jsonify({'success': True, 'user': user_data})
    else:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
