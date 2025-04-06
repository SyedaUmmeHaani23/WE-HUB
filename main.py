"""
Main entry point for the Women Entrepreneurs Hub (WE Hub) application.
"""
import logging
from app import app

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    # Run the Flask application
    # The application will be accessible at http://localhost:5000
    app.run(host="0.0.0.0", port=5000, debug=True)
