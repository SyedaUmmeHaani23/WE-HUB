"""
Dashboard routes for Women Entrepreneurs Hub.
Handles dashboard views and data.
"""
import logging
import os
from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from services.analytics_service import get_sales_stats, get_recent_sales
from services.google_maps_service import get_nearby_businesses

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/', methods=['GET'])
def index():
    """Render the main dashboard page."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return redirect(url_for('auth.login'))
    
    # Get Google Maps API key from environment
    google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    
    return render_template(
        'dashboard.html', 
        user_data=user_data,
        google_maps_api_key=google_maps_api_key
    )

@bp.route('/stats', methods=['GET'])
def stats():
    """Get dashboard statistics for the current user."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        # Get user's firebase UID
        firebase_uid = user_data.get('firebase_uid')
        
        # Get sales statistics
        stats_data = get_sales_stats(firebase_uid)
        
        return jsonify({
            'success': True,
            'data': stats_data
        })
    
    except Exception as e:
        logging.error(f"Error fetching dashboard stats: {e}")
        return jsonify({
            'success': False,
            'message': 'Error fetching dashboard statistics'
        }), 500

@bp.route('/recent-sales', methods=['GET'])
def recent_sales():
    """Get recent sales for the current user."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        # Get user's firebase UID
        firebase_uid = user_data.get('firebase_uid')
        
        # Get limit parameter, default to 5
        limit = request.args.get('limit', 5, type=int)
        
        # Get recent sales
        sales_data = get_recent_sales(firebase_uid, limit)
        
        return jsonify({
            'success': True,
            'data': sales_data
        })
    
    except Exception as e:
        logging.error(f"Error fetching recent sales: {e}")
        return jsonify({
            'success': False,
            'message': 'Error fetching recent sales'
        }), 500

@bp.route('/nearby-businesses', methods=['GET'])
def nearby_businesses():
    """Get nearby women-owned businesses."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        # Get coordinates from request
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        radius = request.args.get('radius', 10, type=int)  # Default 10km radius
        
        if not lat or not lng:
            return jsonify({'success': False, 'message': 'Latitude and longitude are required'}), 400
        
        # Get nearby businesses
        businesses = get_nearby_businesses(lat, lng, radius)
        
        return jsonify({
            'success': True,
            'data': businesses
        })
    
    except Exception as e:
        logging.error(f"Error fetching nearby businesses: {e}")
        return jsonify({
            'success': False,
            'message': 'Error fetching nearby businesses'
        }), 500
