import os
import logging
from flask import Flask, render_template, session, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, current_user, login_required
import firebase_admin
from firebase_admin import credentials, firestore, auth as firebase_auth, storage
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize Firebase Admin
try:
    cred_dict = {
        "type": "service_account",
        "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
        "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID", ""),
        "private_key": os.environ.get("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n'),
        "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL", ""),
        "client_id": os.environ.get("FIREBASE_CLIENT_ID", ""),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_CERT_URL", "")
    }
    
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        'storageBucket': f"{os.environ.get('FIREBASE_PROJECT_ID')}.appspot.com"
    })
    db = firestore.client()
    bucket = storage.bucket()
    logging.info("Firebase Admin initialized successfully.")
except Exception as e:
    logging.error(f"Firebase Admin initialization failed: {e}")
    db = None
    bucket = None

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Import blueprints
from auth import auth_bp
from ecommerce import ecommerce_bp
from community import community_bp
from dashboard import dashboard_bp
from chatbot import chatbot_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(ecommerce_bp)
app.register_blueprint(community_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(chatbot_bp)

@app.route('/')
def index():
    """Render the homepage"""
    return render_template(
        'index.html',
        firebase_api_key=os.environ.get("FIREBASE_API_KEY"),
        firebase_project_id=os.environ.get("FIREBASE_PROJECT_ID"),
        firebase_app_id=os.environ.get("FIREBASE_APP_ID"),
        user=current_user if current_user.is_authenticated else None
    )

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('base.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logging.error(f"Server error: {e}")
    return render_template('base.html', error="Internal server error"), 500

@app.context_processor
def inject_globals():
    """Inject global variables into templates"""
    return {
        'firebase_api_key': os.environ.get("FIREBASE_API_KEY"),
        'firebase_project_id': os.environ.get("FIREBASE_PROJECT_ID"),
        'firebase_app_id': os.environ.get("FIREBASE_APP_ID")
    }
