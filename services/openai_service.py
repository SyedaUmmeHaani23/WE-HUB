"""
OpenAI service for Women Entrepreneurs Hub.
Provides chatbot functionality using OpenAI's GPT models.
"""
import os
import json
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = None
try:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    if OPENAI_API_KEY:
        client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("OpenAI client initialized successfully")
    else:
        logger.warning("OPENAI_API_KEY not found in environment variables")
except Exception as e:
    logger.error(f"Error initializing OpenAI client: {e}")

def get_chatbot_response(message, user_info=None):
    """
    Get a response from the OpenAI chatbot.
    
    Args:
        message (str): The message from the user
        user_info (dict, optional): Information about the user for context
        
    Returns:
        str: The response from the chatbot
    """
    # If OpenAI is not available, fall back to predefined responses
    if not client or not OPENAI_API_KEY:
        from chatbot import get_response
        return get_response(message)
    
    try:
        # Create system message with context about WE Hub
        system_message = """
        You are an AI assistant for the Women Entrepreneurs Hub (WE Hub), a platform designed to help women 
        entrepreneurs grow their businesses. You assist users with questions about e-commerce, 
        marketing tools, community features, business analytics, and platform usage.
        
        Be helpful, concise, and focused on empowering women entrepreneurs. Provide practical advice 
        and guide them to the right features in the platform.
        
        Platform features include:
        1. E-commerce: Product listing, management, and sales
        2. Marketing & Visibility: Tools for online presence and campaigns
        3. Community & Networking: Forums, events, and mentorship
        4. Data & Insights: Business analytics dashboard
        5. Account management: Profile settings and preferences
        
        Always maintain a positive, encouraging tone. If you don't know an answer, suggest where 
        they might find help within the platform instead of making up information.
        """
        
        # Add user context if available
        if user_info:
            user_context = f"""
            Some context about this user:
            - Name: {user_info.get('name', 'Unknown')}
            - Business Type: {user_info.get('business_type', 'Unknown')}
            - Joined: {user_info.get('joined_date', 'Recently')}
            """
            system_message += user_context
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": message}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error getting OpenAI response: {e}")
        # Fall back to predefined responses if OpenAI fails
        from chatbot import get_response
        return get_response(message)