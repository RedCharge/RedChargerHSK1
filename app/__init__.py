from flask import Flask, request
from flask_login import LoginManager
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

    
    # Configuration from .env
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'hsk1-quiz-app-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///hsk_quiz.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    
    # Firebase config
    app.config['FIREBASE_API_KEY'] = os.getenv('FIREBASE_API_KEY')
    app.config['FIREBASE_AUTH_DOMAIN'] = os.getenv('FIREBASE_AUTH_DOMAIN')
    app.config['FIREBASE_PROJECT_ID'] = os.getenv('FIREBASE_PROJECT_ID')
    app.config['FIREBASE_STORAGE_BUCKET'] = os.getenv('FIREBASE_STORAGE_BUCKET')
    app.config['FIREBASE_MESSAGING_SENDER_ID'] = os.getenv('FIREBASE_MESSAGING_SENDER_ID')
    app.config['FIREBASE_APP_ID'] = os.getenv('FIREBASE_APP_ID')
    app.config['FIREBASE_MEASUREMENT_ID'] = os.getenv('FIREBASE_MEASUREMENT_ID')
    
    # Verification codes
    verification_codes_str = os.getenv('VERIFICATION_CODES', '')
    app.config['VERIFICATION_CODES'] = [code.strip() for code in verification_codes_str.split(',') if code.strip()]
    
    print(f"🔑 Loaded {len(app.config['VERIFICATION_CODES'])} verification codes")
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login_page'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Store active sessions
    app.active_sessions = {}
    
    from .models import UserAuth, User
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user from database"""
        try:
            # Try to load from UserAuth table first (for backward compatibility)
            user_auth = UserAuth.query.get(user_id)
            if user_auth:
                # Return the associated User object if it exists
                if user_auth.user:
                    return user_auth.user
                # Otherwise create a User for this auth
                return create_user_for_auth(user_auth)
            
            # If not found in UserAuth, try User table directly
            user = User.query.get(user_id)
            if user:
                return user
                
            print(f"❌ User not found with ID: {user_id}")
            return None
            
        except Exception as e:
            print(f"❌ Error loading user {user_id}: {str(e)}")
            return None
    
    def create_user_for_auth(user_auth):
        """Create a User record for a UserAuth"""
        try:
            # Check if user already exists
            user = User.query.filter_by(username=user_auth.email.split('@')[0] if user_auth.email else f"user_{user_auth.id[:8]}").first()
            
            if not user:
                # Create new User
                username = user_auth.email.split('@')[0] if user_auth.email else f"user_{user_auth.id[:8]}"
                user = User(
                    id=user_auth.user_id or str(uuid.uuid4()),
                    username=username,
                    email=user_auth.email
                )
                
                # Link auth and user
                user_auth.user_id = user.id
                
                db.session.add(user)
                db.session.commit()
                print(f"✅ Created User record for auth: {user_auth.email or user_auth.firebase_uid[:8]}")
            
            return user
            
        except Exception as e:
            print(f"❌ Error creating user for auth: {str(e)}")
            return None
    
    # Register blueprints
    from .main_routes import main_bp
    from .words_routes import words_bp
    from .sentence_routes import sentence_bp
    from .learn_routes import learn_bp
    from .profile_routes import profile_bp
    from .auth_routes import auth_bp
    from .results_routes import results_bp
    
    # Register blueprints with proper URL prefixes
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)  # Main routes at root
    app.register_blueprint(words_bp, url_prefix='/words')
    app.register_blueprint(sentence_bp, url_prefix='/sentences')
    app.register_blueprint(learn_bp)
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(results_bp)  # API routes at root
    
    # Add route for Firebase config
    @app.route('/api/firebase-config')
    def firebase_config():
        """Securely serve Firebase config to frontend"""
        config = {
            'apiKey': app.config.get('FIREBASE_API_KEY'),
            'authDomain': app.config.get('FIREBASE_AUTH_DOMAIN'),
            'projectId': app.config.get('FIREBASE_PROJECT_ID'),
            'storageBucket': app.config.get('FIREBASE_STORAGE_BUCKET'),
            'messagingSenderId': app.config.get('FIREBASE_MESSAGING_SENDER_ID'),
            'appId': app.config.get('FIREBASE_APP_ID'),
            'measurementId': app.config.get('FIREBASE_MEASUREMENT_ID')
        }
        return jsonify(config)
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Debug: Check if tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📊 Database tables: {tables}")
            
        except Exception as e:
            print(f"❌ Database setup error: {e}")
            import traceback
            traceback.print_exc()
    
    # Add import for jsonify and uuid at the top of the function
    from flask import jsonify
    import uuid
    
    return app