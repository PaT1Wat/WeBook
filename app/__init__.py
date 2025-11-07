from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
import os
import json

db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///webook.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Only initialize SocketIO if not in testing mode
    if not os.getenv('TESTING'):
        socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
    
    # Register custom template filters
    @app.template_filter('from_json')
    def from_json_filter(value):
        """Convert JSON string to Python object"""
        if not value:
            return []
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return []
    
    # Register blueprints
    from app.routes import auth, books, reviews, forum, chat, admin, recommendations
    app.register_blueprint(auth.bp)
    app.register_blueprint(books.bp)
    app.register_blueprint(reviews.bp)
    app.register_blueprint(forum.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(recommendations.bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
