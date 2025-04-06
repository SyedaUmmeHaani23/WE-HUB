"""
Business tools routes for Women Entrepreneurs Hub.
Handles marketing, analytics, SEO, and other business tools.
"""
import logging
import os
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from services.analytics_service import get_analytics_data
from services.google_maps_service import get_business_info

bp = Blueprint('business_tools', __name__, url_prefix='/business-tools')

@bp.route('/', methods=['GET'])
def index():
    """Render the business tools main page."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return redirect(url_for('auth.login'))
    
    return render_template(
        'business-tools.html',
        user_data=user_data
    )

@bp.route('/marketing', methods=['GET'])
def marketing():
    """Render the marketing tools page."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return redirect(url_for('auth.login'))
    
    return render_template(
        'marketing-tools.html',
        user_data=user_data
    )

@bp.route('/marketing/google-ads', methods=['GET'])
def google_ads():
    """Render the Google Ads integration page."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return redirect(url_for('auth.login'))
    
    return render_template(
        'google-ads.html',
        user_data=user_data
    )

@bp.route('/analytics', methods=['GET'])
def analytics():
    """Render the analytics dashboard."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return redirect(url_for('auth.login'))
    
    try:
        # Get analytics data
        firebase_uid = user_data.get('firebase_uid')
        analytics_data = get_analytics_data(firebase_uid)
        
        return render_template(
            'analytics-dashboard.html',
            user_data=user_data,
            analytics_data=analytics_data
        )
    
    except Exception as e:
        logging.error(f"Error loading analytics dashboard: {e}")
        return render_template(
            'analytics-dashboard.html',
            user_data=user_data,
            error="An error occurred while loading analytics data."
        )

@bp.route('/seo', methods=['GET'])
def seo():
    """Render the SEO tools page."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return redirect(url_for('auth.login'))
    
    return render_template(
        'seo-tools.html',
        user_data=user_data
    )

@bp.route('/integration/google-my-business', methods=['GET'])
def google_my_business():
    """Render the Google My Business integration page."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return redirect(url_for('auth.login'))
    
    try:
        # Get business info from Google My Business
        firebase_uid = user_data.get('firebase_uid')
        business_info = get_business_info(firebase_uid)
        
        # Get Google Maps API key from environment
        google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY', '')
        
        return render_template(
            'google-my-business.html',
            user_data=user_data,
            business_info=business_info,
            google_maps_api_key=google_maps_api_key
        )
    
    except Exception as e:
        logging.error(f"Error loading Google My Business page: {e}")
        return render_template(
            'google-my-business.html',
            user_data=user_data,
            error="An error occurred while loading business information."
        )

@bp.route('/api/analytics/overview', methods=['GET'])
def get_analytics_overview():
    """Get overview analytics data."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        # Get user's firebase UID
        firebase_uid = user_data.get('firebase_uid')
        
        # Get analytics data
        analytics_data = get_analytics_data(firebase_uid)
        
        return jsonify({
            'success': True,
            'data': analytics_data
        })
    
    except Exception as e:
        logging.error(f"Error fetching analytics overview: {e}")
        return jsonify({
            'success': False,
            'message': 'Error fetching analytics data'
        }), 500

@bp.route('/api/marketing/create-ad', methods=['POST'])
def create_ad_campaign():
    """Create a new Google Ads campaign."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        # Get JSON data
        data = request.json
        
        # Validate required fields
        required_fields = ['name', 'budget', 'target_keywords']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # This would connect to Google Ads API in a real implementation
        # For now, return a success response
        
        return jsonify({
            'success': True,
            'message': 'Ad campaign created successfully',
            'campaign_id': 'sample_campaign_id'
        })
    
    except Exception as e:
        logging.error(f"Error creating ad campaign: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/seo/analyze', methods=['POST'])
def analyze_website_seo():
    """Analyze a website for SEO optimization."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        # Get URL from request
        url = request.json.get('url')
        if not url:
            return jsonify({'success': False, 'message': 'No URL provided'}), 400
        
        # This would connect to an SEO analysis service in a real implementation
        # For now, return mock data
        
        return jsonify({
            'success': True,
            'data': {
                'score': 85,
                'title': 'Good',
                'meta_description': 'Needs improvement',
                'headers': 'Good',
                'content': 'Good',
                'images': 'Needs improvement',
                'mobile_friendly': True,
                'page_speed': 'Medium',
                'suggested_keywords': ['women entrepreneurs', 'small business', 'e-commerce']
            }
        })
    
    except Exception as e:
        logging.error(f"Error analyzing website SEO: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
