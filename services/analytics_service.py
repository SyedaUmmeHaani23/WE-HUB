"""
Analytics service for Women Entrepreneurs Hub.
Provides functions for retrieving and processing analytics data.
"""
import logging
from datetime import datetime, timedelta
from app import db
from models import Product, Order, OrderItem

def get_analytics_data(firebase_uid):
    """
    Get analytics data for a user.
    
    Args:
        firebase_uid (str): The Firebase UID of the user.
        
    Returns:
        dict: A dictionary containing analytics data.
    """
    try:
        # For now, return mock data
        # In a real implementation, this would fetch data from Google Analytics or similar
        return {
            'sales_summary': get_sales_stats(firebase_uid),
            'recent_sales': get_recent_sales(firebase_uid),
            'visitor_stats': {
                'total_visitors': 120,
                'unique_visitors': 85,
                'average_session_duration': '2m 45s',
                'bounce_rate': '35%',
                'traffic_sources': {
                    'direct': 40,
                    'social': 25,
                    'search': 20,
                    'referral': 15
                }
            },
            'top_products': [
                {'name': 'Product A', 'sales': 24, 'revenue': 480.00},
                {'name': 'Product B', 'sales': 18, 'revenue': 540.00},
                {'name': 'Product C', 'sales': 12, 'revenue': 240.00}
            ],
            'sales_by_time': {
                'daily': [5, 7, 3, 8, 10, 6, 4],
                'weekly': [28, 32, 25, 43],
                'monthly': [120, 145, 132, 160, 175, 148]
            }
        }
    except Exception as e:
        logging.error(f"Error getting analytics data: {e}")
        return {
            'sales_summary': {'total_sales': 0, 'total_revenue': 0, 'average_order_value': 0},
            'recent_sales': [],
            'visitor_stats': {'total_visitors': 0, 'unique_visitors': 0},
            'top_products': [],
            'sales_by_time': {'daily': [], 'weekly': [], 'monthly': []}
        }

def get_sales_stats(firebase_uid):
    """
    Get sales statistics for a user.
    
    Args:
        firebase_uid (str): The Firebase UID of the user.
        
    Returns:
        dict: A dictionary containing sales statistics.
    """
    try:
        # In a real implementation, this would query the database for actual sales data
        from models import User, Order
        
        # Get user by Firebase UID
        user = User.query.filter_by(firebase_uid=firebase_uid).first()
        
        if not user:
            return {
                'total_sales': 0,
                'total_revenue': 0.0,
                'average_order_value': 0.0
            }
        
        # Get orders for this user
        orders = Order.query.filter_by(user_id=user.id).all()
        
        total_sales = len(orders)
        total_revenue = sum(order.total_amount for order in orders)
        average_order_value = total_revenue / total_sales if total_sales > 0 else 0
        
        return {
            'total_sales': total_sales,
            'total_revenue': round(total_revenue, 2),
            'average_order_value': round(average_order_value, 2)
        }
    except Exception as e:
        logging.error(f"Error getting sales stats: {e}")
        return {
            'total_sales': 0,
            'total_revenue': 0.0,
            'average_order_value': 0.0
        }

def get_recent_sales(firebase_uid, limit=5):
    """
    Get recent sales for a user.
    
    Args:
        firebase_uid (str): The Firebase UID of the user.
        limit (int): The maximum number of sales to return.
        
    Returns:
        list: A list of recent sales.
    """
    try:
        # In a real implementation, this would query the database for actual sales data
        from models import User, Order, OrderItem, Product
        
        # Get user by Firebase UID
        user = User.query.filter_by(firebase_uid=firebase_uid).first()
        
        if not user:
            return []
        
        # Get recent orders for this user's products
        # This assumes the user is a seller
        products = Product.query.filter_by(user_id=user.id).all()
        product_ids = [product.id for product in products]
        
        recent_order_items = OrderItem.query.filter(
            OrderItem.product_id.in_(product_ids)
        ).order_by(
            OrderItem.id.desc()
        ).limit(limit).all()
        
        # Format order items
        sales = []
        for item in recent_order_items:
            product = Product.query.get(item.product_id)
            order = Order.query.get(item.order_id)
            buyer = User.query.get(order.user_id)
            
            sales.append({
                'id': item.id,
                'product_name': product.name,
                'quantity': item.quantity,
                'price': item.price,
                'total': item.price * item.quantity,
                'date': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'buyer': buyer.username if buyer else 'Unknown'
            })
        
        return sales
    except Exception as e:
        logging.error(f"Error getting recent sales: {e}")
        return []