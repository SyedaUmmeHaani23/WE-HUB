"""
Firebase service for Women Entrepreneurs Hub.
Provides functions for interacting with Firebase services.
"""
import logging
import os
import uuid
import firebase_admin
from firebase_admin import storage
from app import db, firestore_db

def upload_profile_image(firebase_uid, image_data):
    """
    Upload a profile image to Firebase Storage.
    
    Args:
        firebase_uid (str): The Firebase UID of the user.
        image_data (bytes): The image data to upload.
        
    Returns:
        str: The URL of the uploaded image.
    """
    try:
        # In a real implementation, this would upload to Firebase Storage
        # For now, return a placeholder URL
        from models import User
        
        # Get user by Firebase UID
        user = User.query.filter_by(firebase_uid=firebase_uid).first()
        
        if not user:
            return None
        
        # Generate a unique filename
        filename = f"profile_{firebase_uid}_{uuid.uuid4().hex[:8]}.jpg"
        
        # If running in a real Firebase environment, upload to Storage
        if firestore_db:
            try:
                bucket = storage.bucket()
                blob = bucket.blob(f"profiles/{filename}")
                blob.upload_from_string(image_data, content_type='image/jpeg')
                blob.make_public()
                
                image_url = blob.public_url
                
                # Update user's profile_picture in database
                user.profile_picture = image_url
                db.session.commit()
                
                return image_url
            except Exception as e:
                logging.error(f"Error uploading to Firebase Storage: {e}")
                return None
        else:
            # For development without Firebase, use a placeholder
            placeholder_url = f"https://via.placeholder.com/150?text={user.username[0]}"
            
            # Update user's profile_picture in database
            user.profile_picture = placeholder_url
            db.session.commit()
            
            return placeholder_url
    except Exception as e:
        logging.error(f"Error uploading profile image: {e}")
        return None