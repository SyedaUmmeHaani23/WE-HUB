"""
Application configuration and initialization for Women Entrepreneurs Hub.
"""
import os
import sys
import logging
from flask import Flask, render_template, session, redirect, url_for, g, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Setup better logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Create a base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

logger.info("Creating Flask application")
# Create Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "temporary_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///wehub.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

logger.info("Initializing database")
# Initialize database
db.init_app(app)

# Initialize Firebase variables
firebase_project_id = os.environ.get("FIREBASE_PROJECT_ID")
firebase_api_key = os.environ.get("FIREBASE_API_KEY")
firebase_app_id = os.environ.get("FIREBASE_APP_ID")

logger.info(f"Firebase environment variables: PROJECT_ID: {firebase_project_id is not None}, API_KEY: {firebase_api_key is not None}, APP_ID: {firebase_app_id is not None}")

# We'll initialize Firebase Admin in a simpler way and with better error handling
firestore_db = None

# Deferring Firebase Admin initialization to prevent startup issues
# It will be initialized when first needed

# Create database tables
try:
    with app.app_context():
        logger.info("Creating database tables")
        import models  # Import models to ensure they're registered with SQLAlchemy
        db.create_all()
        logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {e}")

logger.info("Importing routes")
# Import routes
try:
    from routes import auth, dashboard, profile, e_commerce, community, events, business_tools, api
    
    # Register blueprints
    logger.info("Registering blueprints")
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(profile.bp)
    app.register_blueprint(e_commerce.bp)
    app.register_blueprint(community.bp)
    app.register_blueprint(events.bp)
    app.register_blueprint(business_tools.bp)
    app.register_blueprint(api.bp)
    logger.info("All blueprints registered successfully")
except Exception as e:
    logger.error(f"Error registering blueprints: {e}")

@app.route('/')
def index():
    """Render the homepage of WE Hub."""
    try:
        logger.info("Rendering index page")
        return render_template(
            'index.html',
            firebase_api_key=os.environ.get("FIREBASE_API_KEY", ""),
            firebase_project_id=os.environ.get("FIREBASE_PROJECT_ID", ""),
            firebase_app_id=os.environ.get("FIREBASE_APP_ID", "")
        )
    except Exception as e:
        logger.error(f"Error rendering index page: {e}")
        return f"<h1>WE Hub is starting up</h1><p>Error: {str(e)}</p><p>We are experiencing technical difficulties. Please try again later.</p>"

@app.errorhandler(404)
def page_not_found(e):
    """Handler for 404 errors."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handler for 500 errors."""
    logging.error(f"Server error: {e}")
    return render_template('500.html'), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok"})

@app.context_processor
def inject_user():
    """Inject user data into templates."""
    user_data = session.get('user_data')
    return dict(user_data=user_data)
