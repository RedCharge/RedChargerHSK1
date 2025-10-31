from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy  # Add this back

# Remove socketio import from models
from .models import db  # Only import db, not socketio

def create_app():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')

    print(f"Looking for templates in: {template_dir}")
    print(f"Looking for static files in: {static_dir}")

    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)

    
    # Configuration
    app.config['SECRET_KEY'] = 'hsk1-quiz-app-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hsk_quiz.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions - ONLY db, no socketio
    db.init_app(app)
    
    # Register blueprints
    from .main_routes import main_bp
    from .words_routes import words_bp
    from .sentence_routes import sentence_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(words_bp, url_prefix='/words')
    app.register_blueprint(sentence_bp, url_prefix='/sentences')
    
    # REMOVE socket events registration
    # from .main_routes import register_socket_events
    # register_socket_events(socketio)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app  # Return only app, not socketio