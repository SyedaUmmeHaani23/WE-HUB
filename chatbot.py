import logging
import os
from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user
import random

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

# Check if OpenAI is enabled
OPENAI_ENABLED = os.environ.get("OPENAI_API_KEY") is not None

# Predefined responses for the basic chatbot
FAQ_RESPONSES = {
    'hello': [
        'Hello! How can I assist you today?',
        'Hi there! What can I help you with?',
        'Welcome to WE Hub! How may I help you?'
    ],
    'business': [
        'To set up your business profile, go to your Profile page after logging in and fill in your business details.',
        'Our platform offers business tools including e-commerce, marketing assistance, and analytics.',
        'You can showcase your products by adding them in the Shop section after completing your business profile.'
    ],
    'products': [
        'You can add products by navigating to Shop > My Products > Add Product.',
        'Each product can have multiple images, description, price, and category.',
        'Your products will be displayed to all users browsing the shop.'
    ],
    'payment': [
        'We support Google Pay for seamless and secure transactions.',
        'Payment processing is handled securely through our platform.',
        'You can manage your payment settings in your business profile.'
    ],
    'community': [
        'Our community features include forums and events to connect with other women entrepreneurs.',
        'You can create and participate in discussions in the Community section.',
        'Networking events are regularly posted in the Events calendar.'
    ],
    'analytics': [
        'The Analytics dashboard provides insights about your business performance.',
        'You can track views, popular products, and sales trends in your dashboard.',
        'Data is updated in real-time to help you make informed business decisions.'
    ],
    'marketing': [
        'Our platform helps with marketing by increasing your online visibility.',
        'Your business profile is integrated with Google Maps to help customers find you.',
        'We provide basic analytics to help you understand your audience better.'
    ],
    'default': [
        'I\'m not sure I understand that question. Could you rephrase it?',
        'I don\'t have information about that yet. Is there something else I can help with?',
        'That\'s beyond my current capabilities. Would you like to ask something about your business profile, products, or community features?'
    ]
}

def get_response(message):
    """Generate a response for the given message"""
    message = message.lower()
    
    if any(greeting in message for greeting in ['hello', 'hi', 'hey']):
        return random.choice(FAQ_RESPONSES['hello'])
        
    elif any(keyword in message for keyword in ['business', 'profile', 'setup']):
        return random.choice(FAQ_RESPONSES['business'])
        
    elif any(keyword in message for keyword in ['product', 'item', 'listing', 'sell']):
        return random.choice(FAQ_RESPONSES['products'])
        
    elif any(keyword in message for keyword in ['pay', 'payment', 'google pay', 'transaction']):
        return random.choice(FAQ_RESPONSES['payment'])
        
    elif any(keyword in message for keyword in ['community', 'forum', 'network', 'connect']):
        return random.choice(FAQ_RESPONSES['community'])
        
    elif any(keyword in message for keyword in ['analytics', 'data', 'performance', 'track']):
        return random.choice(FAQ_RESPONSES['analytics'])
        
    elif any(keyword in message for keyword in ['marketing', 'visibility', 'promote']):
        return random.choice(FAQ_RESPONSES['marketing'])
        
    else:
        return random.choice(FAQ_RESPONSES['default'])

@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    """API endpoint for chatbot interactions"""
    try:
        message = request.json.get('message', '').strip()
        
        if not message:
            return jsonify({'success': False, 'message': 'No message provided.'}), 400
            
        # Generate response using OpenAI if available, otherwise use basic response
        is_ai_response = False
        if OPENAI_ENABLED:
            try:
                from services.openai_service import get_chatbot_response
                
                # Get user info if authenticated
                user_info = None
                if current_user.is_authenticated:
                    user_info = {
                        'name': current_user.full_name or current_user.username,
                        'business_type': current_user.business_category,
                        'joined_date': current_user.created_at.strftime('%Y-%m-%d') if current_user.created_at else 'Recently'
                    }
                
                response = get_chatbot_response(message, user_info)
                is_ai_response = True
                logging.info("Using OpenAI for chatbot response")
            except Exception as openai_error:
                logging.error(f"Error using OpenAI: {openai_error}")
                response = get_response(message)  # Fallback to basic responses
                is_ai_response = False
        else:
            response = get_response(message)
        
        return jsonify({
            'success': True,
            'response': response,
            'is_ai': is_ai_response
        }), 200
        
    except Exception as e:
        logging.error(f"Error processing chatbot message: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@chatbot_bp.route('/widget')
def widget():
    """Render chatbot widget"""
    return render_template('chatbot/widget.html')
