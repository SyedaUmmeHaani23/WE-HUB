"""
Main entry point for the Women Entrepreneurs Hub (WE Hub) application.
"""
import logging
import sys
from app import app

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)
print("Starting Women Entrepreneurs Hub application...", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)

if __name__ == "__main__":
    # Run the Flask application
    # The application will be accessible at http://localhost:5000
    app.run(host="0.0.0.0", port=5000, debug=True)

# This app object is used by gunicorn
print("Application ready to serve requests at http://0.0.0.0:5000", file=sys.stderr)
