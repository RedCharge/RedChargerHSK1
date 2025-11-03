from flask import Flask
import os

# Import db and socketio from models
from .models import db, socketio

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
    
    # For PythonAnywhere, disable SocketIO or use polling
    socketio.init_app(app, 
                     cors_allowed_origins="*",
                     async_mode='threading')  # Use threading instead of eventlet
    
    # Register blueprints
    from .main_routes import main_bp
    from .words_routes import words_bp
    from .sentence_routes import sentence_bp
    from .learn_routes import learn_bp
    from .profile_routes import profile_bp
    from leaderboard_routes import leaderboard_bp




    app.register_blueprint(main_bp)
    app.register_blueprint(words_bp, url_prefix='/words')
    app.register_blueprint(sentence_bp, url_prefix='/sentences')
    app.register_blueprint(learn_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(leaderboard_bp)
    
    # Import and register socket events (comment out if causing issues)
    try:
        from .main_routes import register_socket_events
        register_socket_events(socketio)
    except Exception as e:
        print(f"SocketIO events registration failed: {e}")
        print("Continuing without SocketIO events...")
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app, socketio