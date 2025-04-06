import logging
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models import Product
from app import db
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/analytics')
@login_required
def analytics():
    """Business analytics dashboard"""
    try:
        # Get user's products
        products = Product.get_by_user(current_user.id)
        
        # Basic analytics data
        analytics_data = {
            'total_products': len(products),
            'product_categories': {},
            'newest_products': []
        }
        
        # Process products for analytics
        for product in products:
            # Count by category
            category = product.category or 'Uncategorized'
            if category in analytics_data['product_categories']:
                analytics_data['product_categories'][category] += 1
            else:
                analytics_data['product_categories'][category] = 1
                
            # Add to newest products (limited to 5)
            if len(analytics_data['newest_products']) < 5:
                analytics_data['newest_products'].append({
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'image': product.images[0] if product.images else None
                })
                
        # Mock analytics data for demonstration (would be replaced with real analytics in production)
        mock_views = {
            'today': 15,
            'week': 85,
            'month': 350
        }
        
        # Generate dates for the past week for chart data
        dates = []
        daily_views = []
        today = datetime.now()
        for i in range(7):
            date = today - timedelta(days=6-i)
            dates.append(date.strftime('%a'))
            # Mock data - would be replaced with real analytics in production
            daily_views.append(10 + (i * 5))
            
        return render_template(
            'dashboard/analytics.html', 
            analytics=analytics_data, 
            views=mock_views,
            chart_dates=dates,
            chart_views=daily_views
        )
    
    except Exception as e:
        logging.error(f"Error loading analytics dashboard: {e}")
        return render_template('dashboard/analytics.html', analytics={}, views={}, chart_dates=[], chart_views=[])

@dashboard_bp.route('/nearby-businesses')
@login_required
def nearby_businesses():
    """Find nearby women-owned businesses"""
    try:
        businesses = []
        
        # Get women-owned businesses from Firestore
        if db:
            user_docs = db.collection('users').stream()
            
            for doc in user_docs:
                user_data = doc.to_dict()
                business_data = user_data.get('business_data', {})
                
                if business_data and business_data.get('name'):
                    businesses.append({
                        'id': doc.id,
                        'name': business_data.get('name'),
                        'description': business_data.get('description'),
                        'category': business_data.get('category'),
                        'location': business_data.get('location'),
                        'owner': user_data.get('display_name'),
                        'photo': user_data.get('photo_url')
                    })
                    
        return render_template('dashboard/nearby_businesses.html', businesses=businesses)
    
    except Exception as e:
        logging.error(f"Error loading nearby businesses: {e}")
        return render_template('dashboard/nearby_businesses.html', businesses=[])

@dashboard_bp.route('/api/analytics')
@login_required
def api_analytics():
    """API endpoint to get analytics data"""
    try:
        # Mock analytics data (would be replaced with real analytics in production)
        # Generate data for the past 30 days
        dates = []
        views = []
        today = datetime.now()
        for i in range(30):
            date = today - timedelta(days=29-i)
            dates.append(date.strftime('%Y-%m-%d'))
            # Mock data with some randomness
            views.append(5 + (i * 2) + (i % 5))
            
        return jsonify({
            'success': True,
            'data': {
                'dates': dates,
                'views': views
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting analytics data: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
