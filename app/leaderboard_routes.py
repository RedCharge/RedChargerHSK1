from flask import Blueprint, jsonify, request, session, render_template
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Any

# Create Blueprint for leaderboard routes
leaderboard_bp = Blueprint('leaderboard', __name__)

def get_all_users_data():
    """Get comprehensive data for all users for leaderboard from DATABASE"""
    try:
        # Import inside function to avoid circular imports
        from .models import User, QuizResult
        
        print("🔍 Fetching all users from database...")
        
        # Get all users from database
        all_users = User.query.all()
        print(f"✅ Found {len(all_users)} total users in database")
        
        if not all_users:
            print("❌ No users found in database!")
            return []
        
        all_users_stats = []
        
        for user in all_users:
            print(f"👤 Processing user: {user.username} - ID: {user.id}")
            print(f"   Raw data - Words: {user.words_mastered}, Sentences: {user.sentences_mastered}, Score: {user.total_score}")
            
            # Get user's quiz results
            user_quizzes = QuizResult.query.filter_by(user_id=user.id).all()
            print(f"   📊 User has {len(user_quizzes)} quiz results")
            
            # Calculate stats from actual data
            total_correct = sum(quiz.correct_answers for quiz in user_quizzes)
            total_questions = sum(quiz.total_questions for quiz in user_quizzes)
            accuracy_rate = round((total_correct / total_questions * 100), 1) if total_questions > 0 else 0
            
            # Calculate score using consistent formula
            score = calculate_user_score({
                'words_mastered': user.words_mastered,
                'sentences_mastered': user.sentences_mastered,
                'current_streak': user.current_streak,
                'accuracy_rate': accuracy_rate
            })
            
            print(f"   🎯 Calculated score: {score} (from formula)")
            print(f"   📈 Stored score: {user.total_score} (in database)")
            
            # Use the higher score between calculated and stored
            final_score = max(score, user.total_score or 0)
            
            # Determine level
            level = determine_level(user.words_mastered, user.sentences_mastered, accuracy_rate)
            
            # Mark current user
            is_current_user = user.id == session.get('user_id')
            
            user_stats = {
                'user_id': user.id,
                'username': user.username,
                'avatar': user.avatar_color,
                'score': final_score,
                'words_mastered': user.words_mastered,
                'sentences_mastered': user.sentences_mastered,
                'current_streak': user.current_streak,
                'accuracy_rate': accuracy_rate,
                'level': level,
                'achievements': [achievement.achievement_name for achievement in user.achievements],
                'is_current_user': is_current_user
            }
            
            all_users_stats.append(user_stats)
            print(f"   ✅ Added {user.username} to leaderboard with score: {final_score}")
        
        print(f"🎉 Returning {len(all_users_stats)} users for leaderboard")
        return all_users_stats
        
    except Exception as e:
        print(f"❌ Error getting all users data from database: {e}")
        import traceback
        traceback.print_exc()
        return []

def calculate_user_score(user_data: Dict) -> int:
    """Calculate user score based on their performance - CONSISTENT FORMULA"""
    words_mastered = user_data.get('words_mastered', 0)
    sentences_mastered = user_data.get('sentences_mastered', 0)
    current_streak = user_data.get('current_streak', 0)
    accuracy_rate = user_data.get('accuracy_rate', 0)
    
    word_score = words_mastered * 10
    sentence_score = sentences_mastered * 15
    streak_bonus = current_streak * 5
    accuracy_bonus = accuracy_rate * 2
    
    total_score = word_score + sentence_score + streak_bonus + accuracy_bonus
    
    print(f"   🧮 Score calculation: {words_mastered} words × 10 = {word_score}")
    print(f"   🧮 {sentences_mastered} sentences × 15 = {sentence_score}")
    print(f"   🧮 {current_streak} streak × 5 = {streak_bonus}")
    print(f"   🧮 {accuracy_rate}% accuracy × 2 = {accuracy_bonus}")
    print(f"   🧮 TOTAL: {total_score}")
    
    return total_score

def determine_level(words: int, sentences: int, accuracy: int) -> str:
    """Determine user level based on their progress"""
    if words >= 140 and sentences >= 90 and accuracy >= 90:
        return "HSK1 Expert"
    elif words >= 120 and sentences >= 75 and accuracy >= 85:
        return "HSK1 Advanced"
    elif words >= 80 and sentences >= 50 and accuracy >= 75:
        return "HSK1 Intermediate"
    elif words >= 40 and sentences >= 25:
        return "HSK1 Learner"
    else:
        return "HSK1 Beginner"

@leaderboard_bp.route('/leaderboard')
def leaderboard_page():
    """Serve the main leaderboard HTML page"""
    print("🌐 Serving leaderboard page...")
    return render_template('leaderboard.html')

@leaderboard_bp.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get REAL leaderboard data from DATABASE with optional filtering and sorting"""
    try:
        print("🚀 API: /api/leaderboard called")
        
        # Get query parameters
        timeframe = request.args.get('timeframe', 'all')
        sort_by = request.args.get('sort_by', 'score')
        
        print(f"📋 Parameters - timeframe: {timeframe}, sort_by: {sort_by}")
        
        # Get all users data from DATABASE
        all_users_stats = get_all_users_data()
        
        if not all_users_stats:
            print("❌ No user data available for leaderboard")
            return jsonify({
                'success': True,
                'leaderboard': [],
                'timeframe': timeframe,
                'sort_by': sort_by,
                'total_users': 0,
                'message': 'No users found in database'
            })
        
        print(f"📊 Sorting {len(all_users_stats)} users by {sort_by}...")
        
        # Sort the data based on parameter
        if sort_by == 'words':
            sorted_data = sorted(all_users_stats, key=lambda x: x['words_mastered'], reverse=True)
        elif sort_by == 'sentences':
            sorted_data = sorted(all_users_stats, key=lambda x: x['sentences_mastered'], reverse=True)
        elif sort_by == 'streak':
            sorted_data = sorted(all_users_stats, key=lambda x: x['current_streak'], reverse=True)
        else:  # Default to score
            sorted_data = sorted(all_users_stats, key=lambda x: x['score'], reverse=True)
        
        # Add rankings based on SCORE (not the current sort)
        score_sorted = sorted(all_users_stats, key=lambda x: x['score'], reverse=True)
        score_rankings = {user['user_id']: rank + 1 for rank, user in enumerate(score_sorted)}
        
        # Add score-based rank to each user
        for user in sorted_data:
            user['rank'] = score_rankings.get(user['user_id'], len(score_sorted) + 1)
        
        # Limit to top 100 users
        limited_data = sorted_data[:100]
        
        print(f"✅ Returning leaderboard with {len(limited_data)} users")
        for i, user in enumerate(limited_data[:5]):  # Show top 5 for debugging
            print(f"   {i+1}. {user['username']} - Score: {user['score']} - Rank: {user['rank']}")
        
        return jsonify({
            'success': True,
            'leaderboard': limited_data,
            'timeframe': timeframe,
            'sort_by': sort_by,
            'total_users': len(limited_data)
        })
        
    except Exception as e:
        print(f"❌ Failed to load leaderboard: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to load leaderboard: {str(e)}'
        }), 500

@leaderboard_bp.route('/api/leaderboard/current-user-rank')
def get_current_user_rank():
    """Get current user's rank and stats from DATABASE"""
    try:
        current_user_id = session.get('user_id')
        print(f"🔍 Getting current user rank for user_id: {current_user_id}")
        
        if not current_user_id:
            print("❌ User not authenticated")
            return jsonify({
                'success': False,
                'error': 'User not authenticated'
            }), 401
        
        # Import inside function to avoid circular imports
        from .models import User
        
        # Get user from database
        current_user = User.query.get(current_user_id)
        if not current_user:
            print("❌ User not found in database")
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        print(f"👤 Found current user: {current_user.username}")
        
        all_users_stats = get_all_users_data()
        
        if not all_users_stats:
            print("❌ No users in leaderboard")
            return jsonify({
                'success': False,
                'error': 'No users in leaderboard'
            }), 404
        
        # Sort by score to calculate rank
        sorted_by_score = sorted(all_users_stats, key=lambda x: x['score'], reverse=True)
        
        # Find current user and their rank
        current_user_data = None
        current_user_rank = None
        
        for rank, user in enumerate(sorted_by_score, 1):
            if user['user_id'] == current_user_id:
                current_user_data = user
                current_user_rank = rank
                break
        
        if not current_user_data:
            print("❌ Current user not found in leaderboard data")
            return jsonify({
                'success': False,
                'error': 'User data not found in leaderboard'
            }), 404
        
        print(f"✅ Current user rank: #{current_user_rank} out of {len(sorted_by_score)} users")
        
        return jsonify({
            'success': True,
            'rank': current_user_rank,
            'user_data': current_user_data,
            'total_users': len(sorted_by_score)
        })
        
    except Exception as e:
        print(f"❌ Failed to get user rank: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to get user rank: {str(e)}'
        }), 500

@leaderboard_bp.route('/api/leaderboard/achievements', methods=['GET'])
def get_leaderboard_achievements():
    """Get achievements for leaderboard display from DATABASE"""
    try:
        user_id = session.get('user_id')
        print(f"🔍 Getting achievements for user_id: {user_id}")
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User not authenticated'
            }), 401
        
        # Import inside function to avoid circular imports
        from .models import UserAchievement
        
        # Get user's achievements from database
        user_achievements = UserAchievement.query.filter_by(user_id=user_id).all()
        
        print(f"🏆 Found {len(user_achievements)} achievements for user")
        
        achievements_data = []
        for achievement in user_achievements:
            achievements_data.append({
                'name': achievement.achievement_name,
                'description': achievement.achievement_description,
                'icon': achievement.achievement_icon,
                'unlocked': True,
                'date': achievement.unlocked_at.strftime('%Y-%m-%d') if achievement.unlocked_at else None
            })
        
        return jsonify({
            'success': True,
            'achievements': achievements_data
        })
        
    except Exception as e:
        print(f"❌ Error retrieving achievements: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error retrieving achievements: {str(e)}'
        }), 500

@leaderboard_bp.route('/api/leaderboard/stats', methods=['GET'])
def get_leaderboard_stats():
    """Get user stats for leaderboard progress bars from DATABASE"""
    try:
        user_id = session.get('user_id')
        print(f"🔍 Getting stats for user_id: {user_id}")
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User not authenticated'
            }), 401
        
        # Import inside function to avoid circular imports
        from .models import User
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        print(f"📊 User stats - Words: {user.words_mastered}, Sentences: {user.sentences_mastered}, Streak: {user.current_streak}")
        
        # Calculate progress percentages
        words_progress = min((user.words_mastered / 150) * 100, 100)
        sentences_progress = min((user.sentences_mastered / 100) * 100, 100)
        streak_progress = min((user.current_streak / 7) * 100, 100)
        
        stats = {
            'stats': {
                'words_mastered': user.words_mastered,
                'sentences_mastered': user.sentences_mastered,
                'current_streak': user.current_streak,
                'accuracy_rate': user.accuracy_rate
            },
            'progress': {
                'words': {
                    'current': user.words_mastered,
                    'target': 150,
                    'percentage': round(words_progress, 1)
                },
                'sentences': {
                    'current': user.sentences_mastered,
                    'target': 100,
                    'percentage': round(sentences_progress, 1)
                },
                'streak': {
                    'current': user.current_streak,
                    'target': 7,
                    'percentage': round(streak_progress, 1)
                }
            }
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        print(f"❌ Error retrieving stats: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error retrieving stats: {str(e)}'
        }), 500

@leaderboard_bp.route('/api/leaderboard/update-scores', methods=['POST'])
def update_leaderboard_scores():
    """Update user scores in database (called after quizzes)"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        print(f"🔄 Updating scores for user_id: {user_id}")
        print(f"📥 Update data: {data}")
        
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User not authenticated'
            }), 401
        
        # Import inside function to avoid circular imports
        from .models import User, db
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Update user stats
        if 'words_mastered' in data:
            user.words_mastered = data['words_mastered']
        if 'sentences_mastered' in data:
            user.sentences_mastered = data['sentences_mastered']
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
        
        print(f"✅ Scores updated successfully for {user.username}")
        
        return jsonify({
            'success': True,
            'message': 'Scores updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error updating scores: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error updating scores: {str(e)}'
        }), 500

def initialize_sample_users():
    """Initialize sample users in database for testing"""
    try:
        print("🎯 Initializing sample users...")
        
        # Import inside function to avoid circular imports
        from .models import User, db
        
        # Check if sample users already exist
        existing_users = User.query.filter(
            User.username.in_(['ChineseMaster', 'PinyinPro', 'HanziHero', 'MandarinLearner'])
        ).all()
        
        print(f"🔍 Found {len(existing_users)} existing sample users")
        
        for user in existing_users:
            print(f"   📝 Existing: {user.username} - Score: {user.total_score}")
        
        if existing_users:
            print("✅ Sample users already exist, skipping initialization")
            return  # Sample users already exist
        
        print("🆕 Creating new sample users...")
        
        # Create sample users
        sample_users = [
            User(
                username='ChineseMaster',
                level='HSK1 Expert',
                avatar_color='primary-blue',
                words_mastered=150,
                sentences_mastered=100,
                current_streak=21,
                accuracy_rate=94,
                total_score=2850
            ),
            User(
                username='PinyinPro', 
                level='HSK1 Advanced',
                avatar_color='secondary-cyan',
                words_mastered=148,
                sentences_mastered=95,
                current_streak=18,
                accuracy_rate=92,
                total_score=2670
            ),
            User(
                username='HanziHero',
                level='HSK1 Intermediate', 
                avatar_color='accent-purple',
                words_mastered=142,
                sentences_mastered=88,
                current_streak=15,
                accuracy_rate=89,
                total_score=2540
            ),
            User(
                username='MandarinLearner',
                level='HSK1 Intermediate',
                avatar_color='success-green', 
                words_mastered=135,
                sentences_mastered=82,
                current_streak=12,
                accuracy_rate=87,
                total_score=2380
            )
        ]
        
        for user in sample_users:
            db.session.add(user)
            print(f"   ➕ Added: {user.username} - Score: {user.total_score}")
        
        db.session.commit()
        print("🎉 Sample users initialized in database successfully")
        
    except Exception as e:
        print(f"❌ Error initializing sample users: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()

# Don't call initialize_sample_users() here - let __init__.py call it within app context