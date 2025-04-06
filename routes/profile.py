"""
Profile routes for Women Entrepreneurs Hub.
Handles user profile views and updates.
"""
import logging
import os
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from app import db, firestore_db
from models import User
from services.firebase_service import upload_profile_image

bp = Blueprint('profile', __name__, url_prefix='/profile')

@bp.route('/', methods=['GET'])
def index():
    """Render the user profile page."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return redirect(url_for('auth.login'))
    
    # Get Google Maps API key from environment
    google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    
    return render_template(
        'profile.html', 
        user_data=user_data,
        google_maps_api_key=google_maps_api_key
    )

@bp.route('/update', methods=['POST'])
def update_profile():
    """Update the user's profile information."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        # Get user ID from session
        user_id = user_data.get('id')
        firebase_uid = user_data.get('firebase_uid')
        
        # Get user from database
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Get form data
        form_data = request.form.to_dict()
        
        # Handle profile image if provided
        profile_image = request.files.get('profile_picture')
        if profile_image and profile_image.filename:
            try:
                # Upload image to Firebase Storage
                image_url = upload_profile_image(profile_image, firebase_uid)
                if image_url:
                    user.profile_picture = image_url
                    # Update session data
                    user_data['profile_picture'] = image_url
                    session['user_data'] = user_data
            except Exception as e:
                logging.error(f"Error uploading profile image: {e}")
                # Continue with other updates even if image upload fails
        
        # Update user fields
        if 'full_name' in form_data:
            user.full_name = form_data.get('full_name')
            user_data['full_name'] = form_data.get('full_name')
        
        if 'username' in form_data and form_data.get('username') != user.username:
            # Check if username is already taken
            existing_user = User.query.filter_by(username=form_data.get('username')).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'success': False, 'message': 'Username already taken'}), 400
            
            user.username = form_data.get('username')
            user_data['username'] = form_data.get('username')
        
        if 'business_name' in form_data:
            user.business_name = form_data.get('business_name')
            user_data['business_name'] = form_data.get('business_name')
        
        if 'business_description' in form_data:
            user.business_description = form_data.get('business_description')
        
        if 'business_category' in form_data:
            user.business_category = form_data.get('business_category')
        
        if 'phone' in form_data:
            user.phone = form_data.get('phone')
        
        if 'website' in form_data:
            user.website = form_data.get('website')
        
        if 'address' in form_data:
            user.address = form_data.get('address')
        
        if 'latitude' in form_data and 'longitude' in form_data:
            try:
                user.latitude = float(form_data.get('latitude')) if form_data.get('latitude') else None
                user.longitude = float(form_data.get('longitude')) if form_data.get('longitude') else None
            except ValueError:
                # Invalid coordinates, ignore them
                pass
        
        # Update user in database
        db.session.commit()
        
        # Update user in Firestore
        if firestore_db:
            firestore_db.collection('users').document(firebase_uid).update({
                'full_name': user.full_name,
                'username': user.username,
                'business_name': user.business_name,
                'business_description': user.business_description,
                'business_category': user.business_category,
                'phone': user.phone,
                'website': user.website,
                'address': user.address,
                'latitude': user.latitude,
                'longitude': user.longitude,
                'profile_picture': user.profile_picture
            })
        
        # Update session data
        session['user_data'] = user_data
        
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    
    except Exception as e:
        logging.error(f"Error updating profile: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/personal-info', methods=['POST'])
def update_personal_info():
    """Update personal information."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        # Get user ID from session
        user_id = user_data.get('id')
        firebase_uid = user_data.get('firebase_uid')
        
        # Get user from database
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Get form data
        form_data = request.form.to_dict()
        
        # Update user fields
        if 'full_name' in form_data:
            user.full_name = form_data.get('full_name')
            user_data['full_name'] = form_data.get('full_name')
        
        if 'username' in form_data and form_data.get('username') != user.username:
            # Check if username is already taken
            existing_user = User.query.filter_by(username=form_data.get('username')).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'success': False, 'message': 'Username already taken'}), 400
            
            user.username = form_data.get('username')
            user_data['username'] = form_data.get('username')
        
        if 'phone' in form_data:
            user.phone = form_data.get('phone')
        
        if 'bio' in form_data:
            user.business_description = form_data.get('bio')
        
        # Update user in database
        db.session.commit()
        
        # Update user in Firestore
        if firestore_db:
            firestore_db.collection('users').document(firebase_uid).update({
                'full_name': user.full_name,
                'username': user.username,
                'phone': user.phone,
                'business_description': user.business_description
            })
        
        # Update session data
        session['user_data'] = user_data
        
        return jsonify({'success': True, 'message': 'Personal information updated successfully'})
    
    except Exception as e:
        logging.error(f"Error updating personal information: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/business-info', methods=['POST'])
def update_business_info():
    """Update business information."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        # Get user ID from session
        user_id = user_data.get('id')
        firebase_uid = user_data.get('firebase_uid')
        
        # Get user from database
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Get form data
        form_data = request.form.to_dict()
        
        # Update user fields
        if 'business_name' in form_data:
            user.business_name = form_data.get('business_name')
            user_data['business_name'] = form_data.get('business_name')
        
        if 'business_category' in form_data:
            user.business_category = form_data.get('business_category')
        
        if 'business_description' in form_data:
            user.business_description = form_data.get('business_description')
        
        if 'website' in form_data:
            user.website = form_data.get('website')
        
        # Update user in database
        db.session.commit()
        
        # Update user in Firestore
        if firestore_db:
            firestore_db.collection('users').document(firebase_uid).update({
                'business_name': user.business_name,
                'business_category': user.business_category,
                'business_description': user.business_description,
                'website': user.website
            })
        
        # Update session data
        session['user_data'] = user_data
        
        return jsonify({'success': True, 'message': 'Business information updated successfully'})
    
    except Exception as e:
        logging.error(f"Error updating business information: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/location', methods=['POST'])
def update_location():
    """Update location information."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        # Get user ID from session
        user_id = user_data.get('id')
        firebase_uid = user_data.get('firebase_uid')
        
        # Get user from database
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Get form data
        form_data = request.form.to_dict()
        
        # Update user fields
        if 'address' in form_data:
            user.address = form_data.get('address')
        
        # Additional address fields if needed
        address_parts = []
        if 'address' in form_data and form_data.get('address'):
            address_parts.append(form_data.get('address'))
        if 'city' in form_data and form_data.get('city'):
            address_parts.append(form_data.get('city'))
        if 'state' in form_data and form_data.get('state'):
            address_parts.append(form_data.get('state'))
        if 'postal_code' in form_data and form_data.get('postal_code'):
            address_parts.append(form_data.get('postal_code'))
        if 'country' in form_data and form_data.get('country'):
            address_parts.append(form_data.get('country'))
        
        if address_parts:
            user.address = ", ".join(address_parts)
        
        if 'latitude' in form_data and 'longitude' in form_data:
            try:
                user.latitude = float(form_data.get('latitude')) if form_data.get('latitude') else None
                user.longitude = float(form_data.get('longitude')) if form_data.get('longitude') else None
            except ValueError:
                # Invalid coordinates, ignore them
                pass
        
        # Update user in database
        db.session.commit()
        
        # Update user in Firestore
        if firestore_db:
            firestore_db.collection('users').document(firebase_uid).update({
                'address': user.address,
                'latitude': user.latitude,
                'longitude': user.longitude
            })
        
        return jsonify({'success': True, 'message': 'Location updated successfully'})
    
    except Exception as e:
        logging.error(f"Error updating location: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/social-profiles', methods=['POST'])
def update_social_profiles():
    """Update social media profiles."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        # Get user ID from session
        user_id = user_data.get('id')
        firebase_uid = user_data.get('firebase_uid')
        
        # Get user from database
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Get form data - we'll store these in Firestore only
        form_data = request.form.to_dict()
        
        # Update in Firestore
        if firestore_db:
            social_data = {}
            for platform in ['facebook', 'instagram', 'twitter', 'linkedin', 'pinterest']:
                if platform in form_data:
                    social_data[platform] = form_data.get(platform)
            
            firestore_db.collection('users').document(firebase_uid).update({
                'social_profiles': social_data
            })
        
        return jsonify({'success': True, 'message': 'Social profiles updated successfully'})
    
    except Exception as e:
        logging.error(f"Error updating social profiles: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
