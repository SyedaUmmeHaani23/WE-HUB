"""
Chatbot module for Women Entrepreneurs Hub.
Provides an AI assistant for users to get help and information.
"""

import os
import json
import logging
import requests
from flask import Blueprint, render_template, request, jsonify, current_app

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

def get_perplexity_response(message):
    """
    Get a response from the Perplexity AI API.
    
    Args:
        message (str): The user's message
        
    Returns:
        str: The AI's response
    """
    api_key = os.environ.get('PERPLEXITY_API_KEY')
    
    if not api_key:
        logger.warning("Perplexity API key not set. Using fallback response system.")
        return get_basic_response(message)
    
    try:
        url = "https://api.perplexity.ai/chat/completions"
        
        payload = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an AI assistant for women entrepreneurs. Your name is WE Hub Assistant. Keep responses helpful, concise, and focused on business advice, resources, and guidance for female business owners. Provide practical actionable advice. Use a friendly, professional tone with bullet points for clarity when appropriate. Avoid being overly technical or jargon-heavy."
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            "temperature": 0.2,
            "top_p": 0.9,
            "stream": False,
            "presence_penalty": 0,
            "frequency_penalty": 1
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        
        if 'choices' in response_data and len(response_data['choices']) > 0:
            return response_data['choices'][0]['message']['content']
        else:
            logger.error(f"Unexpected API response format: {response_data}")
            return "I'm sorry, I couldn't process your request right now."
            
    except Exception as e:
        logger.error(f"Error getting response from Perplexity API: {e}")
        return "I'm sorry, I'm having trouble connecting to my knowledge base right now. Please try again later."

def get_basic_response(message):
    """
    Get a basic response when the API is not available.
    
    Args:
        message (str): The user's message
        
    Returns:
        str: A basic response
    """
    # Convert message to lowercase for easier matching
    message_lower = message.lower()
    
    # Basic responses for common questions
    if any(word in message_lower for word in ['hello', 'hi', 'hey']):
        return "Hello! How can I assist you today with your business needs?"
    
    elif 'funding' in message_lower or 'invest' in message_lower or 'capital' in message_lower:
        return "There are several funding options for women entrepreneurs:\n\n• SBA loans and grants specifically for women-owned businesses\n• Women-focused venture capital firms like Female Founders Fund\n• Crowdfunding platforms like iFundWomen\n• Angel investor networks like Pipeline Angels\n\nCheck the Business Tools section for more resources."
    
    elif 'marketing' in message_lower or 'promote' in message_lower or 'advertise' in message_lower:
        return "For marketing your business, consider:\n\n• Using social media platforms like Instagram and LinkedIn\n• Content marketing through blogs and newsletters\n• Collaborating with other women entrepreneurs\n• Using Google Ad Grants for nonprofits\n• Exploring local networking opportunities\n\nOur Business Tools section has marketing resources to help you get started."
    
    elif 'community' in message_lower or 'connect' in message_lower or 'network' in message_lower:
        return "You can connect with other entrepreneurs through:\n\n• Our community forum on the platform\n• Upcoming events and workshops (check the Events section)\n• Mentorship opportunities in the Community section\n• Local business organizations for women\n• Industry-specific groups relevant to your business"
    
    elif 'sell' in message_lower or 'product' in message_lower or 'e-commerce' in message_lower or 'shop' in message_lower:
        return "To start selling your products on WE Hub:\n\n• Go to the E-Commerce section\n• Click on 'My Products'\n• Use the 'Add Product' button to create a listing\n• Add high-quality images and detailed descriptions\n• Set your pricing and inventory\n\nYou can manage all your products and orders from the dashboard."
    
    elif 'event' in message_lower or 'workshop' in message_lower:
        return "To find or create events:\n\n• Visit the Events section to see upcoming workshops and networking opportunities\n• Filter events by category, date, or format (in-person/virtual)\n• Click on any event for details and registration\n• Create your own event using the 'Create Event' button if you want to host something\n\nEvents are a great way to build your network and skills!"
    
    elif 'profile' in message_lower or 'account' in message_lower:
        return "To update your profile:\n\n• Click on your name in the top right corner\n• Select 'My Profile' from the dropdown menu\n• Edit your personal information, business details, and contact info\n• Add your social media links\n• Upload a profile picture\n\nA complete profile helps other entrepreneurs connect with you!"
    
    else:
        return "I'm here to help with your entrepreneurship journey. You can ask me about funding options, marketing strategies, using our platform features, connecting with other entrepreneurs, or any other business-related questions you have."

@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    """API endpoint for chatbot interactions"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'success': False, 'error': 'No message provided'}), 400
        
        message = data['message']
        logger.info(f"Received chat message: {message}")
        
        # Get response from Perplexity API
        response = get_perplexity_response(message)
        
        return jsonify({
            'success': True,
            'response': response
        })
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@chatbot_bp.route('/widget', methods=['GET'])
def widget():
    """Render chatbot widget"""
    return render_template('chatbot/widget.html')
