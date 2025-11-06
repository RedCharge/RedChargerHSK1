from flask import Flask
import os

# Import db from models
from .models import db

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
    
    # Register blueprints - use relative imports
    from .main_routes import main_bp
    from .words_routes import words_bp
    from .sentence_routes import sentence_bp
    from .learn_routes import learn_bp
    from .profile_routes import profile_bp
    from chat_routes import chat_bp
    
    # Import leaderboard routes
    try:
        from .leaderboard_routes import leaderboard_bp
        app.register_blueprint(leaderboard_bp)
        print("Leaderboard routes registered successfully")
    except ImportError as e:
        print(f"Leaderboard routes not available: {e}")
        # Create a simple leaderboard blueprint as fallback
        from flask import Blueprint
        leaderboard_bp = Blueprint('leaderboard', __name__)
        
        @leaderboard_bp.route('/leaderboard')
        def leaderboard_fallback():
            return "Leaderboard coming soon"
            
        app.register_blueprint(leaderboard_bp)
        print("Using fallback leaderboard routes")

    app.register_blueprint(main_bp)
    app.register_blueprint(words_bp, url_prefix='/words')
    app.register_blueprint(sentence_bp, url_prefix='/sentences')
    app.register_blueprint(learn_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(chat_bp)
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created")
            
            # Initialize sample data for leaderboard
            from .leaderboard_routes import initialize_sample_users
            initialize_sample_users()
            
        except Exception as e:
            print(f"Database setup error: {e}")
    
    return app  # Return only app, no socketio