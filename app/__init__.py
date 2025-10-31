from flask import Flask
import os
# Remove these lines - we'll import from models
# from flask_sqlalchemy import SQLAlchemy  
# from flask_socketio import SocketIO

# Import db and socketio from models
from .models import db, socketio

# Remove these - using imports from models instead
# db = SQLAlchemy()
# socketio = SocketIO()

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
    
    # Initialize extensions
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Register blueprints
    from .main_routes import main_bp
    from .words_routes import words_bp
    from .sentence_routes import sentence_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(words_bp, url_prefix='/words')
    app.register_blueprint(sentence_bp, url_prefix='/sentences')
    
    # Import and register socket events
    from .main_routes import register_socket_events
    register_socket_events(socketio)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app, socketio