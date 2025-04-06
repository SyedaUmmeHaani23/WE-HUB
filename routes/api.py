"""
API routes for Women Entrepreneurs Hub.
Contains RESTful API endpoints for integration with external services.
"""
import logging
import firebase_admin
from firebase_admin import firestore
from flask import Blueprint, request, jsonify, session
from app import db, firestore_db
from models import User, Product, Order

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/status', methods=['GET'])
def status():
    """API status endpoint."""
    return jsonify({
        'status': 'online',
        'version': '1.0.0',
        'service': 'Women Entrepreneurs Hub API'
    })

@bp.route('/user/profile', methods=['GET'])
def get_user_profile():
    """Get the current user's profile information."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        # Get user by ID
        user_id = user_data.get('id')
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Return user profile data
        return jsonify({
            'success': True,
            'profile': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'profile_picture': user.profile_picture,
                'business_name': user.business_name,
                'business_description': user.business_description,
                'business_category': user.business_category,
                'website': user.website,
                'phone': user.phone,
                'address': user.address
            }
        })
    
    except Exception as e:
        logging.error(f"Error getting user profile: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/products/featured', methods=['GET'])
def get_featured_products():
    """Get featured products."""
    try:
        # In a real implementation, this might have specific criteria for "featured" products
        # For now, just get a few available products
        products = Product.query.filter_by(is_available=True).limit(6).all()
        
        # Format products for JSON response
        products_data = []
        for product in products:
            seller = User.query.get(product.user_id)
            products_data.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'image_url': product.image_url,
                'category': product.category,
                'seller': {
                    'id': seller.id,
                    'username': seller.username,
                    'business_name': seller.business_name,
                    'profile_picture': seller.profile_picture
                }
            })
        
        return jsonify({
            'success': True,
            'products': products_data
        })
    
    except Exception as e:
        logging.error(f"Error getting featured products: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Check database connectivity
        User.query.first()
        
        # Check Firebase connectivity if available
        firebase_status = False
        if firestore_db:
            # Try a simple Firestore operation
            try:
                firestore_db.collection('health_check').document('test').set({'timestamp': firebase_admin.firestore.SERVER_TIMESTAMP})
                firebase_status = True
            except Exception as e:
                logging.warning(f"Firebase health check failed: {e}")
        
        return jsonify({
            'status': 'healthy',
            'database': True,
            'firebase': firebase_status
        })
    
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500