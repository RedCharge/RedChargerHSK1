from flask import Flask
import os

# Import db from models
from .models import db

def create_app():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')

    print(f"🔧 Looking for templates in: {template_dir}")
    print(f"🔧 Looking for static files in: {static_dir}")

    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)

    
    # Configuration
    app.config['SECRET_KEY'] = 'hsk1-quiz-app-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hsk_quiz.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Show database path for debugging
    db_path = os.path.join(base_dir, 'hsk_quiz.db')
    print(f"🗄️ Database will be created at: {db_path}")
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints - use relative imports
    print("🔄 Registering blueprints...")
    
    from .main_routes import main_bp
    from .words_routes import words_bp
    from .sentence_routes import sentence_bp
    from .learn_routes import learn_bp
    from .profile_routes import profile_bp
    from leaderboard_routes import leaderboard_bp, initialize_user_data
    
    # Import leaderboard routes
    try:
        from .leaderboard_routes import leaderboard_bp
        app.register_blueprint(leaderboard_bp)
        print("✅ Leaderboard routes registered successfully")
    except ImportError as e:
        print(f"❌ Leaderboard routes not available: {e}")
        # Create a simple leaderboard blueprint as fallback
        from flask import Blueprint
        leaderboard_bp = Blueprint('leaderboard', __name__)
        
        @leaderboard_bp.route('/leaderboard')
        def leaderboard_fallback():
            return "Leaderboard coming soon"
            
        app.register_blueprint(leaderboard_bp)
        print("⚠️ Using fallback leaderboard routes")

    app.register_blueprint(main_bp)
    app.register_blueprint(words_bp, url_prefix='/words')
    app.register_blueprint(sentence_bp, url_prefix='/sentences')
    app.register_blueprint(learn_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(leaderboard_bp)
    
    print("✅ All blueprints registered successfully")
    
    # Create database tables and initialize data
    with app.app_context():
        try:
            print("🗄️ Creating database tables...")
            db.create_all()
            print("✅ Database tables created")
            
            # Check current user count
            from .models import User
            user_count = User.query.count()
            print(f"👥 Current user count in database: {user_count}")
            
            # Initialize sample data for leaderboard
            print("🔄 Initializing sample users...")
            from .leaderboard_routes import initialize_sample_users
            initialize_sample_users()
            
            # Check user count after initialization
            user_count_after = User.query.count()
            print(f"👥 User count after initialization: {user_count_after}")
            
            if user_count_after > 0:
                print("✅ Sample users initialized successfully")
                # Show the users that were created
                users = User.query.all()
                for user in users:
                    print(f"   👤 {user.username} - Score: {user.total_score}")
            else:
                print("❌ No users were created during initialization")
            
        except Exception as e:
            print(f"❌ Database setup error: {e}")
            import traceback
            traceback.print_exc()

    # Add debug route for manual user initialization
    @app.route('/debug-init-users')
    def debug_init_users():
        """Manual trigger for user initialization"""
        try:
            from .leaderboard_routes import initialize_sample_users
            from .models import User
            
            # Count before
            count_before = User.query.count()
            
            # Initialize users
            initialize_sample_users()
            
            # Count after
            count_after = User.query.count()
            
            # Get all users
            users = User.query.all()
            user_list = "<br>".join([f"- {u.username} (Score: {u.total_score})" for u in users])
            
            return f"""
            <h1>User Initialization Debug</h1>
            <p><strong>Users before:</strong> {count_before}</p>
            <p><strong>Users after:</strong> {count_after}</p>
            <p><strong>Users added:</strong> {count_after - count_before}</p>
            <p><strong>Current users:</strong><br>{user_list}</p>
            <hr>
            <p><a href="/api/debug/users">Check users API</a></p>
            <p><a href="/api/leaderboard">Check leaderboard API</a></p>
            <p><a href="/leaderboard">View leaderboard page</a></p>
            <p><a href="/api/debug/add-users-now">Force add users now</a></p>
            """
        except Exception as e:
            return f"<h1>Error</h1><p>{str(e)}</p>"

    @app.route('/debug-database-info')
    def debug_database_info():
        """Show database information"""
        try:
            from .models import User, QuizResult, UserAchievement
            
            user_count = User.query.count()
            quiz_count = QuizResult.query.count()
            achievement_count = UserAchievement.query.count()
            
            users = User.query.all()
            user_details = "<br>".join([
                f"- {u.username}: {u.words_mastered} words, {u.sentences_mastered} sentences, {u.total_score} score" 
                for u in users
            ])
            
            return f"""
            <h1>Database Information</h1>
            <p><strong>Users:</strong> {user_count}</p>
            <p><strong>Quiz Results:</strong> {quiz_count}</p>
            <p><strong>Achievements:</strong> {achievement_count}</p>
            <hr>
            <h2>User Details:</h2>
            <p>{user_details if user_details else 'No users found'}</p>
            <hr>
            <p><a href="/debug-init-users">Initialize Users</a></p>
            <p><a href="/api/debug/add-users-now">Force Add Users</a></p>
            <p><a href="/api/leaderboard">Leaderboard API</a></p>
            """
        except Exception as e:
            return f"<h1>Error</h1><p>{str(e)}</p>"

    print("🎉 Flask app initialization complete!")
    print("🔧 Debug routes available:")
    print("   - http://localhost:5000/debug-init-users")
    print("   - http://localhost:5000/debug-database-info")
    print("   - http://localhost:5000/api/debug/add-users-now")
    print("   - http://localhost:5000/api/debug/users")
    print("   - http://localhost:5000/api/leaderboard")
    
    return app