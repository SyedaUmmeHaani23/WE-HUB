"""
OpenAI service for Women Entrepreneurs Hub.
Provides integration with OpenAI's models for chatbot and other AI features.
"""
import os
import json
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service class for interacting with OpenAI API."""
    
    def __init__(self):
        """Initialize the OpenAI service with API key from environment."""
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = None
        
        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info("OpenAI service initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing OpenAI client: {e}")
        else:
            logger.warning("OpenAI API key not found, service will use fallback responses")
    
    def generate_response(self, message, user_data=None, context=None):
        """
        Generate a response for the chatbot using OpenAI's models.
        
        Args:
            message (str): The user's message to respond to
            user_data (dict, optional): User data for personalization
            context (list, optional): Previous conversation history
            
        Returns:
            str: The generated response
        """
        if not self.client:
            return self._fallback_response(message)
        
        try:
            # Create a system message with information about WE Hub
            system_message = """You are the Women Entrepreneurs Hub (WE Hub) assistant. 
            You provide helpful, supportive, and informative responses to women entrepreneurs. 
            Your goal is to assist them with business questions, platform navigation, and accessing resources.
            Keep your responses concise, friendly, and empowering. Use a supportive and encouraging tone.
            Focus on practical advice, platform features, and resources available through WE Hub."""
            
            # Add user context if available
            if user_data:
                system_message += f"\n\nUser information: {json.dumps(user_data)}"
            
            # Create messages array
            messages = [{"role": "system", "content": system_message}]
            
            # Add conversation history if available
            if context:
                for item in context:
                    messages.append(item)
            
            # Add the user's current message
            messages.append({"role": "user", "content": message})
            
            # Call the OpenAI API
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            return self._fallback_response(message)
    
    def _fallback_response(self, message):
        """
        Provide a fallback response when OpenAI is unavailable.
        
        Args:
            message (str): The user's message
            
        Returns:
            str: A fallback response
        """
        # Basic response logic based on keywords in the message
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return "Hello! I'm the WE Hub assistant. How can I help you today?"
        
        elif any(word in message_lower for word in ['bye', 'goodbye', 'see you']):
            return "Goodbye! Feel free to reach out if you need assistance in the future."
            
        elif any(word in message_lower for word in ['thank', 'thanks', 'appreciate']):
            return "You're welcome! I'm here to help women entrepreneurs like you succeed."
            
        elif any(word in message_lower for word in ['login', 'sign in', 'account']):
            return "To log in, click the 'Login' button in the top right corner. You can sign in with Google or use your email and password."
            
        elif any(word in message_lower for word in ['product', 'sell', 'store', 'shop']):
            return "You can list your products through our e-commerce platform. Go to 'E-Commerce' in the navigation menu and click 'Add Product'."
            
        elif any(word in message_lower for word in ['event', 'workshop', 'webinar']):
            return "Check out our 'Events' section to find upcoming workshops and networking opportunities. You can also create your own events for the community."
            
        elif any(word in message_lower for word in ['community', 'forum', 'connect']):
            return "Our 'Community' section offers forums to connect with other women entrepreneurs, share experiences, and seek advice."
            
        elif any(word in message_lower for word in ['analytics', 'data', 'stats', 'performance']):
            return "The 'Dashboard' provides analytics on your business performance, customer demographics, and sales trends to help you make informed decisions."
            
        elif any(word in message_lower for word in ['marketing', 'promote', 'advertise']):
            return "Explore our 'Business Tools' section for marketing resources, SEO optimization tips, and Google Analytics integration."
            
        else:
            return "I'm here to help with your business journey. Could you please provide more details about what you're looking for?"