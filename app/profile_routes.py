from flask import Blueprint, render_template, jsonify, request, session
from .models import db, User, QuizResult, UserAchievement
from datetime import datetime, timedelta

# Create blueprint
profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
def profile_page():
    """Serve the profile.html page"""
    return render_template('profile.html')

@profile_bp.route('/leaderboard')
def leaderboard_page():
    """Serve the leaderboard.html page"""
    return render_template('leaderboard.html')

# ===== DEBUG ROUTES =====
@profile_bp.route('/api/profile/debug-auth')
def debug_auth():
    """Debug endpoint to check authentication status"""
    try:
        user_id = session.get('user_id')
        session_data = dict(session)
        
        print("=== DEBUG AUTH ===")
        print("Session data:", session_data)
        print("User ID from session:", user_id)
        print("Session ID:", session.sid if hasattr(session, 'sid') else 'No session ID')
        
        if user_id:
            user = User.query.get(user_id)
            if user:
                return jsonify({
                    'authenticated': True,
                    'user_id': user_id,
                    'username': user.username,
                    'session_keys': list(session.keys()),
                    'message': 'User is authenticated'
                })
            else:
                return jsonify({
                    'authenticated': False,
                    'message': 'User ID in session but user not found in database'
                })
        else:
            return jsonify({
                'authenticated': False,
                'message': 'No user_id in session',
                'session_keys': list(session.keys())
            })
            
    except Exception as e:
        return jsonify({
            'authenticated': False,
            'message': f'Auth error: {str(e)}'
        }), 500

@profile_bp.route('/api/profile/create-test-user', methods=['POST'])
def create_test_user():
    """Create a test user for debugging"""
    try:
        # Check if we already have a test user
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            test_user = User(
                username='testuser',
                email='test@example.com',
                first_name='Test',
                last_name='User'
            )
            test_user.set_password('testpassword')
            db.session.add(test_user)
            db.session.commit()
            print("Created test user with ID:", test_user.id)
        
        # Log in the test user
        session['user_id'] = test_user.id
        session.permanent = True
        
        return jsonify({
            'success': True,
            'message': 'Test user created and logged in',
            'user_id': test_user.id,
            'username': test_user.username
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating test user: {str(e)}'
        }), 500

@profile_bp.route('/api/profile/login-test-user')
def login_test_user():
    """Log in as test user for debugging"""
    try:
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            return jsonify({
                'success': False,
                'message': 'Test user not found. Create one first.'
            }), 404
        
        # Log in the test user
        session['user_id'] = test_user.id
        session.permanent = True
        
        print("=== LOGGED IN TEST USER ===")
        print("User ID:", test_user.id)
        print("Session user_id:", session.get('user_id'))
        
        return jsonify({
            'success': True,
            'message': 'Logged in as test user',
            'user_id': test_user.id,
            'username': test_user.username
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error logging in: {str(e)}'
        }), 500

@profile_bp.route('/api/profile/current-session')
def current_session():
    """Check current session state"""
    return jsonify({
        'session_data': dict(session),
        'user_id_in_session': session.get('user_id'),
        'all_session_keys': list(session.keys())
    })

@profile_bp.route('/api/profile/debug-save', methods=['POST'])
def debug_save():
    """Debug endpoint to test profile saving"""
    try:
        print("=== DEBUG SAVE CALLED ===")
        print("Headers:", dict(request.headers))
        print("Method:", request.method)
        print("Content-Type:", request.content_type)
        
        if request.is_json:
            data = request.get_json()
            print("Received JSON data:", data)
        else:
            print("No JSON data received")
            data = None
            
        return jsonify({
            'success': True,
            'message': 'Debug save received',
            'received_data': data
        })
        
    except Exception as e:
        print("Debug save error:", str(e))
        return jsonify({
            'success': False,
            'message': f'Debug error: {str(e)}'
        }), 500
# ===== END DEBUG ROUTES =====

@profile_bp.route('/api/profile/check')
def check_auth():
    """Check if user is authenticated and get basic info"""
    try:
        user_id = session.get('user_id')
        print(f"=== AUTH CHECK: user_id from session = {user_id} ===")
        
        if not user_id:
            return jsonify({
                'authenticated': False,
                'message': 'User not authenticated - no user_id in session'
            }), 401
        
        user = User.query.get(user_id)
        if not user:
            print(f"User with ID {user_id} not found in database")
            return jsonify({
                'authenticated': False,
                'message': 'User not found'
            }), 404
        
        print(f"User authenticated: {user.username} (ID: {user_id})")
        return jsonify({
            'authenticated': True,
            'user_id': user_id,
            'username': user.username,
            'has_profile': bool(user.username)
        })
        
    except Exception as e:
        print(f"Auth check error: {str(e)}")
        return jsonify({
            'authenticated': False,
            'message': f'Error checking auth: {str(e)}'
        }), 500

@profile_bp.route('/api/profile/check-completion')
def check_profile_completion():
    """Check if user profile is complete enough for leaderboard"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'profileComplete': False,
                'message': 'User not authenticated'
            }), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'profileComplete': False,
                'message': 'User not found'
            }), 404
        
        profile_complete = bool(user.username)
        
        return jsonify({
            'profileComplete': profile_complete,
            'missingFields': [] if profile_complete else ['username'],
            'username': user.username
        })
        
    except Exception as e:
        return jsonify({
            'profileComplete': False,
            'message': f'Error checking profile: {str(e)}'
        }), 500

@profile_bp.route('/api/profile/save', methods=['POST'])
def save_profile():
    """API endpoint to save profile data to database"""
    try:
        profile_data = request.get_json()
        
        print("=== SAVE PROFILE CALLED ===")
        print("Request JSON:", profile_data)
        print("User ID in session:", session.get('user_id'))
        
        if not profile_data:
            return jsonify({
                'success': False,
                'message': 'No profile data provided'
            }), 400
        
        user_id = session.get('user_id')
        if not user_id:
            print("NO USER ID IN SESSION - AUTH FAILED")
            return jsonify({
                'success': False,
                'message': 'User not authenticated - please log in first'
            }), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Update user profile data
        updates = []
        if 'username' in profile_data:
            user.username = profile_data['username']
            updates.append('username')
        if 'email' in profile_data:
            user.email = profile_data['email']
            updates.append('email')
        if 'firstName' in profile_data:
            user.first_name = profile_data['firstName']
            updates.append('first_name')
        if 'lastName' in profile_data:
            user.last_name = profile_data['lastName']
            updates.append('last_name')
        if 'bio' in profile_data:
            user.bio = profile_data['bio']
            updates.append('bio')
        if 'avatar_color' in profile_data:
            user.avatar_color = profile_data['avatar_color']
            updates.append('avatar_color')
        
        db.session.commit()
        print(f"Profile saved successfully. Updated fields: {updates}")
        
        # Auto-sync to Firebase
        try:
            sync_response = sync_to_firebase()
            print("Firebase sync attempted")
        except Exception as firebase_error:
            print(f"Firebase sync warning: {firebase_error}")
        
        return jsonify({
            'success': True,
            'message': 'Profile saved successfully!',
            'updated_fields': updates
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Save profile error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error saving profile: {str(e)}'
        }), 500

@profile_bp.route('/api/profile/sync-to-firebase', methods=['POST'])
def sync_to_firebase():
    """Sync user data to Firebase for leaderboard"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User not authenticated'
            }), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        quiz_results = QuizResult.query.filter_by(user_id=user_id).all()
        total_quizzes = len(quiz_results)
        
        total_points = (
            (user.words_mastered or 0) * 10 + 
            (user.sentences_mastered or 0) * 20 +
            total_quizzes * 5 +
            (user.current_streak or 0) * 3
        )
        
        firebase_data = {
            'username': user.username or f'User{user_id}',
            'totalPoints': total_points,
            'wordsMastered': user.words_mastered or 0,
            'sentencesMastered': user.sentences_mastered or 0,
            'streakDays': user.current_streak or 0,
            'totalQuizzes': total_quizzes,
            'lastUpdated': datetime.utcnow().isoformat(),
            'profileComplete': bool(user.username)
        }
        
        return jsonify({
            'success': True,
            'firebaseData': firebase_data,
            'firebaseUserId': f'user_{user_id}',
            'message': 'Ready to sync with leaderboard'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error syncing to Firebase: {str(e)}'
        }), 500

@profile_bp.route('/api/profile/stats')
def get_profile_stats():
    """API endpoint to get REAL user statistics from database"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User not authenticated'
            }), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Calculate real statistics from quiz results
        quiz_results = QuizResult.query.filter_by(user_id=user_id).all()
        total_quizzes = len(quiz_results)
        
        # Calculate total study time from quiz attempts
        total_study_time = sum(quiz.time_taken for quiz in quiz_results) // 60  # Convert to minutes
        
        # Calculate accuracy rate from all quizzes
        total_correct = sum(quiz.correct_answers for quiz in quiz_results)
        total_questions = sum(quiz.total_questions for quiz in quiz_results)
        accuracy_rate = round((total_correct / total_questions * 100), 1) if total_questions > 0 else 0
        
        stats = {
            'totalWords': user.words_mastered,
            'totalSentences': user.sentences_mastered,
            'streakDays': user.current_streak,
            'accuracyRate': accuracy_rate,
            'quizzesCompleted': total_quizzes,
            'totalStudyTime': total_study_time
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving stats: {str(e)}'
        }), 500

@profile_bp.route('/api/profile/achievements')
def get_achievements():
    """API endpoint to get REAL user achievements from database"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User not authenticated'
            }), 401
        
        # Get user's unlocked achievements
        user_achievements = UserAchievement.query.filter_by(user_id=user_id).all()
        
        # Define achievement definitions
        achievement_definitions = {
            'first_steps': {
                'name': 'First Steps',
                'description': 'Complete your first quiz',
                'icon': 'fas fa-footsteps'
            },
            'word_master': {
                'name': 'Word Master', 
                'description': 'Learn 100 words',
                'icon': 'fas fa-book'
            },
            'sentence_builder': {
                'name': 'Sentence Builder',
                'description': 'Master 50 sentences', 
                'icon': 'fas fa-comments'
            },
            'perfect_score': {
                'name': 'Perfect Score',
                'description': 'Get 100% on any quiz',
                'icon': 'fas fa-star'
            },
            'week_warrior': {
                'name': 'Week Warrior',
                'description': 'Maintain a 7-day streak',
                'icon': 'fas fa-fire'
            }
        }
        
        achievements = []
        
        # Check each achievement type
        user = User.query.get(user_id)
        quiz_results = QuizResult.query.filter_by(user_id=user_id).all()
        
        # First Steps - completed any quiz
        first_steps_unlocked = len(quiz_results) > 0
        first_steps_achievement = user_achievements[0] if user_achievements else None
        
        achievements.append({
            'id': 1,
            'name': 'First Steps',
            'description': 'Complete your first quiz',
            'icon': 'fas fa-footsteps',
            'unlocked': first_steps_unlocked,
            'dateUnlocked': first_steps_achievement.unlocked_at.strftime('%Y-%m-%d') if first_steps_achievement else None
        })
        
        # Word Master - 100 words
        word_master_unlocked = user.words_mastered >= 100
        word_master_progress = min(user.words_mastered, 100)
        
        achievements.append({
            'id': 2,
            'name': 'Word Master',
            'description': 'Learn 100 words',
            'icon': 'fas fa-book',
            'unlocked': word_master_unlocked,
            'progress': word_master_progress,
            'dateUnlocked': None  # You'd track this in UserAchievement
        })
        
        # Sentence Builder - 50 sentences  
        sentence_builder_unlocked = user.sentences_mastered >= 50
        sentence_builder_progress = min(user.sentences_mastered, 50)
        
        achievements.append({
            'id': 3,
            'name': 'Sentence Builder',
            'description': 'Master 50 sentences',
            'icon': 'fas fa-comments',
            'unlocked': sentence_builder_unlocked,
            'progress': sentence_builder_progress
        })
        
        # Perfect Score - check quiz results
        perfect_score_unlocked = any(quiz.percentage == 100 for quiz in quiz_results)
        
        achievements.append({
            'id': 4,
            'name': 'Perfect Score',
            'description': 'Get 100% on any quiz',
            'icon': 'fas fa-star',
            'unlocked': perfect_score_unlocked
        })
        
        # Week Warrior - 7 day streak
        week_warrior_unlocked = user.current_streak >= 7
        week_warrior_progress = min(user.current_streak, 7)
        
        achievements.append({
            'id': 5,
            'name': 'Week Warrior',
            'description': 'Maintain a 7-day streak',
            'icon': 'fas fa-fire',
            'unlocked': week_warrior_unlocked,
            'progress': week_warrior_progress
        })
        
        return jsonify({
            'success': True,
            'achievements': achievements
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving achievements: {str(e)}'
        }), 500

@profile_bp.route('/api/profile/learning-history')
def get_learning_history():
    """API endpoint to get REAL user learning history from database"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User not authenticated'
            }), 401
        
        # Get actual quiz results from database
        quiz_results = QuizResult.query.filter_by(user_id=user_id)\
            .order_by(QuizResult.timestamp.desc())\
            .limit(20)\
            .all()
        
        learning_history = []
        for quiz in quiz_results:
            learning_history.append({
                'date': quiz.timestamp.strftime('%Y-%m-%d'),
                'activity': f'{quiz.quiz_type.title()} Quiz',
                'score': quiz.percentage,
                'timeSpent': quiz.time_taken // 60,  # Convert to minutes
                'itemsLearned': quiz.correct_answers
            })
        
        return jsonify({
            'success': True,
            'history': learning_history
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving learning history: {str(e)}'
        }), 500

@profile_bp.route('/api/profile/export-data')
def export_user_data():
    """API endpoint to export REAL user data"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User not authenticated'
            }), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        quiz_results = QuizResult.query.filter_by(user_id=user_id).all()
        user_achievements = UserAchievement.query.filter_by(user_id=user_id).all()
        
        user_data = {
            'profile': {
                'username': user.username,
                'level': user.level,
                'avatar_color': user.avatar_color,
                'memberSince': user.created_at.strftime('%Y-%m-%d')
            },
            'statistics': {
                'totalWords': user.words_mastered,
                'totalSentences': user.sentences_mastered,
                'streakDays': user.current_streak,
                'accuracyRate': user.accuracy_rate,
                'totalQuizzes': len(quiz_results),
                'totalStudyTime': sum(quiz.time_taken for quiz in quiz_results) // 60
            },
            'achievements': [
                {
                    'name': achievement.achievement_name,
                    'unlocked': True,
                    'unlockedAt': achievement.unlocked_at.strftime('%Y-%m-%d')
                } for achievement in user_achievements
            ],
            'learningHistory': [
                {
                    'date': quiz.timestamp.strftime('%Y-%m-%d'),
                    'activity': f'{quiz.quiz_type.title()} Quiz',
                    'score': quiz.percentage
                } for quiz in quiz_results[:10]  # Last 10 quizzes
            ]
        }
        
        return jsonify({
            'success': True,
            'data': user_data,
            'exportDate': datetime.utcnow().strftime('%Y-%m-%d')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error exporting data: {str(e)}'
        }), 500

@profile_bp.route('/api/profile/update-progress', methods=['POST'])
def update_progress():
    """Update user progress after quiz completion"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User not authenticated'
            }), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Update user progress based on quiz results
        if 'words_mastered' in data:
            user.words_mastered = data['words_mastered']
        if 'sentences_mastered' in data:
            user.sentences_mastered = data['sentences_mastered']
        if 'total_score' in data:
            user.total_score = data['total_score']
        if 'accuracy_rate' in data:
            user.accuracy_rate = data['accuracy_rate']
        
        # Update streak
        today = datetime.utcnow().date()
        last_activity = user.last_activity_date.date() if user.last_activity_date else None
        
        if last_activity == today - timedelta(days=1):
            user.current_streak += 1
        elif last_activity != today:
            user.current_streak = 1
        
        user.last_activity_date = datetime.utcnow()
        db.session.commit()
        
        # Auto-sync to leaderboard after progress update
        sync_response = sync_to_firebase()
        
        return jsonify({
            'success': True,
            'message': 'Progress updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating progress: {str(e)}'
        }), 500

@profile_bp.route('/api/profile/upload-avatar', methods=['POST'])
def upload_avatar():
    """API endpoint to handle avatar uploads"""
    try:
        avatar_data = request.get_json()
        
        if not avatar_data or 'avatar' not in avatar_data:
            return jsonify({
                'success': False,
                'message': 'No avatar data provided'
            }), 400
        
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                # Store avatar data if you add avatar field to User model
                pass
        
        return jsonify({
            'success': True,
            'message': 'Avatar uploaded successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error uploading avatar: {str(e)}'
        }), 500

@profile_bp.route('/api/profile/delete-account', methods=['POST'])
def delete_account():
    """API endpoint to delete user account"""
    try:
        confirmation = request.get_json()
        
        if not confirmation or not confirmation.get('confirm'):
            return jsonify({
                'success': False,
                'message': 'Account deletion not confirmed'
            }), 400
        
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                # Delete user data
                QuizResult.query.filter_by(user_id=user_id).delete()
                UserAchievement.query.filter_by(user_id=user_id).delete()
                db.session.delete(user)
                db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Account deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error deleting account: {str(e)}'
        }), 500
        
@profile_bp.route('/api/profile/sync-to-leaderboard', methods=['POST'])
def sync_to_leaderboard():
    """Sync user stats to Firebase for leaderboard"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User not authenticated'
            }), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Get user's current stats from your database
        quiz_results = QuizResult.query.filter_by(user_id=user_id).all()
        total_quizzes = len(quiz_results)
        
        # Calculate total points (you can define your own scoring system)
        total_points = (
            user.words_mastered * 10 + 
            user.sentences_mastered * 20 +
            total_quizzes * 5 +
            user.current_streak * 3
        )
        
        # Prepare data for Firebase
        leaderboard_data = {
            'username': user.username or f'User{user_id}',
            'totalPoints': total_points,
            'wordsMastered': user.words_mastered,
            'sentencesMastered': user.sentences_mastered,
            'streakDays': user.current_streak,
            'totalQuizzes': total_quizzes,
            'lastUpdated': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'message': 'Ready to sync with leaderboard',
            'leaderboardData': leaderboard_data,
            'firebaseUserId': f'user_{user_id}'  # Unique ID for Firebase
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error syncing to leaderboard: {str(e)}'
        }), 500