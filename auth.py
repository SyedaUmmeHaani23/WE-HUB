import logging
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import firebase_admin
from firebase_admin import auth as firebase_auth, firestore
from app import app, login_manager, db
from models import User
import os
import json

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    """Load user from Firestore by ID"""
    return User.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    """Handle unauthorized access attempt"""
    flash("You must be logged in to access this page.", "warning")
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler"""
    # If user is already authenticated, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.analytics'))
    
    return render_template(
        'auth/login.html',
        firebase_api_key=os.environ.get("FIREBASE_API_KEY"),
        firebase_project_id=os.environ.get("FIREBASE_PROJECT_ID"),
        firebase_app_id=os.environ.get("FIREBASE_APP_ID"),
    )

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page and handler"""
    # If user is already authenticated, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.analytics'))
    
    return render_template(
        'auth/register.html',
        firebase_api_key=os.environ.get("FIREBASE_API_KEY"),
        firebase_project_id=os.environ.get("FIREBASE_PROJECT_ID"),
        firebase_app_id=os.environ.get("FIREBASE_APP_ID"),
    )

@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """Verify Firebase ID token and log user in"""
    try:
        id_token = request.json.get('idToken')
        if not id_token:
            return jsonify({'error': 'No ID token provided'}), 400
        
        # Verify the ID token
        decoded_token = firebase_auth.verify_id_token(id_token)
        user_id = decoded_token['uid']
        
        # Get user data from Firebase Auth
        firebase_user = firebase_auth.get_user(user_id)
        
        # Check if user exists in Firestore
        user_doc = db.collection('users').document(user_id).get()
        
        if user_doc.exists:
            # Update user data
            user_data = user_doc.to_dict()
            user = User(
                uid=user_id,
                email=firebase_user.email,
                display_name=firebase_user.display_name,
                photo_url=firebase_user.photo_url,
                business_data=user_data.get('business_data', {})
            )
        else:
            # Create new user in Firestore
            user = User(
                uid=user_id, 
                email=firebase_user.email,
                display_name=firebase_user.display_name,
                photo_url=firebase_user.photo_url
            )
            
        # Save user to Firestore
        user.save()
        
        # Log in the user with Flask-Login
        login_user(user)
        
        # Set cookie with Firebase ID token
        session['firebase_token'] = id_token
        
        return jsonify({
            'success': True,
            'redirect': url_for('dashboard.analytics')
        })
        
    except Exception as e:
        logging.error(f"Error verifying token: {e}")
        return jsonify({'error': str(e)}), 401

@auth_bp.route('/logout')
def logout():
    """Log out the current user"""
    logout_user()
    session.pop('firebase_token', None)
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page and update handler"""
    if request.method == 'POST':
        try:
            # Update business profile data
            business_name = request.form.get('business_name')
            business_description = request.form.get('business_description')
            business_category = request.form.get('business_category')
            business_location = request.form.get('business_location')
            business_website = request.form.get('business_website')
            business_phone = request.form.get('business_phone')
            
            # Update user's business data
            current_user.business_data = {
                'name': business_name,
                'description': business_description,
                'category': business_category,
                'location': business_location,
                'website': business_website,
                'phone': business_phone,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            # Save updated user data
            if current_user.save():
                flash("Profile updated successfully!", "success")
            else:
                flash("Failed to update profile. Please try again.", "danger")
                
        except Exception as e:
            logging.error(f"Error updating profile: {e}")
            flash(f"An error occurred: {str(e)}", "danger")
            
    return render_template('auth/profile.html', user=current_user)
