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
            
            # Initialize sample data for leaderboard using the new file-based system
            print("🔄 Initializing leaderboard data directory...")
            from .leaderboard_routes import leaderboard_service
            
            # Check if we have any users in the file system
            file_users = leaderboard_service.get_all_users()
            print(f"👥 Current user count in file system: {len(file_users)}")
            
            # If no users exist, create some sample data
            if len(file_users) == 0:
                print("📝 Creating sample leaderboard data...")
                from .leaderboard_routes import initialize_sample_data
                sample_users = initialize_sample_data()
                print(f"✅ Created {len(sample_users)} sample users")
                
                # Show sample users
                for user in sample_users[:3]:  # Show first 3
                    print(f"   👤 {user['username']} - Score: {user['stats']['totalScore']}")
                if len(sample_users) > 3:
                    print(f"   ... and {len(sample_users) - 3} more")
            else:
                print("✅ Leaderboard data already exists")
                # Show top 3 users
                sorted_users = leaderboard_service.sort_users(file_users, 'overall')
                for i, user in enumerate(sorted_users[:3]):
                    print(f"   {i+1}. {user['username']} - Score: {user['stats']['totalScore']}")
            
        except Exception as e:
            print(f"❌ Database setup error: {e}")
            import traceback
            traceback.print_exc()

    # Add debug route for manual user initialization
    @app.route('/debug-init-users')
    def debug_init_users():
        """Manual trigger for user initialization"""
        try:
            from .leaderboard_routes import initialize_sample_data, leaderboard_service
            
            # Count before
            users_before = leaderboard_service.get_all_users()
            count_before = len(users_before)
            
            # Initialize users
            sample_users = initialize_sample_data()
            
            # Count after
            users_after = leaderboard_service.get_all_users()
            count_after = len(users_after)
            
            # Get all users
            all_users = leaderboard_service.sort_users(users_after, 'overall')
            user_list = "<br>".join([
                f"- {u['username']} (Score: {u['stats']['totalScore']}, Words: {u['stats']['wordsMastered']})" 
                for u in all_users[:10]  # Show top 10
            ])
            
            return f"""
            <h1>Leaderboard Initialization Debug</h1>
            <p><strong>File-based Leaderboard System</strong></p>
            <p><strong>Users before:</strong> {count_before}</p>
            <p><strong>Users after:</strong> {count_after}</p>
            <p><strong>Users added:</strong> {count_after - count_before}</p>
            <p><strong>Data directory:</strong> {leaderboard_service.data_dir}</p>
            <hr>
            <h3>Top Users:</h3>
            <p>{user_list}</p>
            <hr>
            <p><a href="/api/leaderboard">Check leaderboard API</a></p>
            <p><a href="/leaderboard">View leaderboard page</a></p>
            <p><a href="/debug-leaderboard-stats">Leaderboard Stats</a></p>
            """
        except Exception as e:
            return f"<h1>Error</h1><p>{str(e)}</p><pre>{traceback.format_exc()}</pre>"

    @app.route('/debug-leaderboard-stats')
    def debug_leaderboard_stats():
        """Show leaderboard statistics"""
        try:
            from .leaderboard_routes import leaderboard_service, calculate_global_stats
            
            users = leaderboard_service.get_all_users()
            global_stats = calculate_global_stats(users)
            
            # Get top users
            top_users = leaderboard_service.sort_users(users, 'overall')[:10]
            user_details = "<br>".join([
                f"{i+1}. {u['username']}: {u['stats']['totalScore']} pts, {u['stats']['wordsMastered']} words, {u['stats']['sentencesMastered']} sentences, {u['stats']['streakDays']} day streak" 
                for i, u in enumerate(top_users)
            ])
            
            return f"""
            <h1>Leaderboard Statistics</h1>
            <p><strong>Total Users:</strong> {global_stats['totalUsers']}</p>
            <p><strong>Total Quizzes:</strong> {global_stats['totalQuizzes']}</p>
            <p><strong>Total Words Mastered:</strong> {global_stats['totalWords']}</p>
            <p><strong>Total Sentences Mastered:</strong> {global_stats['totalSentences']}</p>
            <p><strong>Average Accuracy:</strong> {global_stats['averageAccuracy']}%</p>
            <p><strong>Average Streak:</strong> {global_stats['averageStreak']} days</p>
            <p><strong>Average Level:</strong> {global_stats['averageLevel']}</p>
            <p><strong>Total XP:</strong> {global_stats['totalXP']}</p>
            <hr>
            <h3>Top 10 Users:</h3>
            <p>{user_details if user_details else 'No users found'}</p>
            <hr>
            <p><a href="/debug-init-users">Initialize Sample Users</a></p>
            <p><a href="/api/leaderboard">Leaderboard API</a></p>
            <p><a href="/leaderboard">View Leaderboard</a></p>
            """
        except Exception as e:
            return f"<h1>Error</h1><p>{str(e)}</p>"

    @app.route('/debug-clear-leaderboard')
    def debug_clear_leaderboard():
        """Clear all leaderboard data"""
        try:
            from .leaderboard_routes import leaderboard_service
            
            # Count before
            users_before = leaderboard_service.get_all_users()
            count_before = len(users_before)
            
            # Clear all user data
            for filename in os.listdir(leaderboard_service.data_dir):
                if filename.endswith('.json'):
                    os.remove(os.path.join(leaderboard_service.data_dir, filename))
            
            # Count after
            users_after = leaderboard_service.get_all_users()
            count_after = len(users_after)
            
            return f"""
            <h1>Leaderboard Data Cleared</h1>
            <p><strong>Users before:</strong> {count_before}</p>
            <p><strong>Users after:</strong> {count_after}</p>
            <p><strong>Users removed:</strong> {count_before - count_after}</p>
            <p><strong>Data directory:</strong> {leaderboard_service.data_dir}</p>
            <hr>
            <p><a href="/debug-init-users">Re-initialize Sample Users</a></p>
            <p><a href="/api/leaderboard">Check Leaderboard API</a></p>
            """
        except Exception as e:
            return f"<h1>Error</h1><p>{str(e)}</p>"

    # API debug routes
    @app.route('/api/debug/leaderboard-users')
    def debug_leaderboard_users():
        """Debug endpoint to see all leaderboard users"""
        try:
            from .leaderboard_routes import leaderboard_service
            
            users = leaderboard_service.get_all_users()
            sorted_users = leaderboard_service.sort_users(users, 'overall')
            
            user_data = []
            for i, user in enumerate(sorted_users):
                user_data.append({
                    'rank': i + 1,
                    'username': user['username'],
                    'score': user['stats']['totalScore'],
                    'words': user['stats']['wordsMastered'],
                    'sentences': user['stats']['sentencesMastered'],
                    'streak': user['stats']['streakDays'],
                    'accuracy': user['stats']['accuracyRate'],
                    'level': user['stats']['level']
                })
            
            return {
                'success': True,
                'total_users': len(users),
                'users': user_data
            }
        except Exception as e:
            return {'error': str(e)}, 500

    print("🎉 Flask app initialization complete!")
    print("🔧 Debug routes available:")
    print("   - http://localhost:5000/debug-init-users")
    print("   - http://localhost:5000/debug-leaderboard-stats")
    print("   - http://localhost:5000/debug-clear-leaderboard")
    print("   - http://localhost:5000/api/debug/leaderboard-users")
    print("   - http://localhost:5000/api/leaderboard")
    print("   - http://localhost:5000/leaderboard")
    
    return app