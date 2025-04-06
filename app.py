"""
Application configuration and initialization for Women Entrepreneurs Hub.
"""
import os
import logging
from flask import Flask, render_template, session, redirect, url_for, g, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
import firebase_admin
from firebase_admin import credentials, firestore, auth

# Create a base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///wehub.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db.init_app(app)

# Initialize Firebase Admin SDK
try:
    # Get Firebase project ID from environment
    firebase_project_id = os.environ.get("FIREBASE_PROJECT_ID")
    
    # Try to initialize with credentials JSON if available
    cred_path = os.environ.get("FIREBASE_CREDENTIALS_PATH")
    if cred_path and os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            'projectId': firebase_project_id
        })
    else:
        # Otherwise initialize default app with project ID
        firebase_admin.initialize_app(options={
            'projectId': firebase_project_id
        })
    
    # Get a reference to the Firestore database
    firestore_db = firestore.client()
    logging.info("Firebase Admin SDK initialized successfully.")
except Exception as e:
    logging.error(f"Failed to initialize Firebase Admin SDK: {e}")
    firestore_db = None

# Create database tables
with app.app_context():
    import models  # Import models to ensure they're registered with SQLAlchemy
    db.create_all()

# Import routes
from routes import auth, dashboard, profile, e_commerce, community, events, business_tools, api

# Register blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(dashboard.bp)
app.register_blueprint(profile.bp)
app.register_blueprint(e_commerce.bp)
app.register_blueprint(community.bp)
app.register_blueprint(events.bp)
app.register_blueprint(business_tools.bp)
app.register_blueprint(api.bp)

@app.route('/')
def index():
    """Render the homepage of WE Hub."""
    return render_template(
        'index.html',
        firebase_api_key=os.environ.get("FIREBASE_API_KEY", ""),
        firebase_project_id=os.environ.get("FIREBASE_PROJECT_ID", ""),
        firebase_app_id=os.environ.get("FIREBASE_APP_ID", "")
    )

@app.errorhandler(404)
def page_not_found(e):
    """Handler for 404 errors."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handler for 500 errors."""
    logging.error(f"Server error: {e}")
    return render_template('500.html'), 500

@app.context_processor
def inject_user():
    """Inject user data into templates."""
    user_data = session.get('user_data')
    return dict(user_data=user_data)
