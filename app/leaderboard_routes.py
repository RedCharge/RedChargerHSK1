from flask import Blueprint, jsonify, request, session, render_template
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Any
from models import db, User, QuizResult, UserAchievement

# Create Blueprint for leaderboard routes
leaderboard_bp = Blueprint('leaderboard', __name__)

def get_all_users_data():
    """Get comprehensive data for all users for leaderboard from DATABASE"""
    try:
        # Get all users from database
        all_users = User.query.all()
        all_users_stats = []
        
        for user in all_users:
            # Get user's quiz results
            user_quizzes = QuizResult.query.filter_by(user_id=user.id).all()
            
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
            
            # Determine level
            level = determine_level(user.words_mastered, user.sentences_mastered, accuracy_rate)
            
            # Mark current user
            is_current_user = user.id == session.get('user_id')
            
            user_stats = {
                'user_id': user.id,
                'username': user.username,
                'avatar': user.avatar_color,  # Using avatar_color from your model
                'score': score,
                'words_mastered': user.words_mastered,
                'sentences_mastered': user.sentences_mastered,
                'current_streak': user.current_streak,
                'accuracy_rate': accuracy_rate,
                'level': level,
                'achievements': [achievement.achievement_name for achievement in user.achievements],
                'is_current_user': is_current_user
            }
            
            all_users_stats.append(user_stats)
        
        return all_users_stats
        
    except Exception as e:
        print(f"Error getting all users data from database: {e}")
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
    
    return word_score + sentence_score + streak_bonus + accuracy_bonus

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
    return render_template('leaderboard.html')

@leaderboard_bp.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get REAL leaderboard data from DATABASE with optional filtering and sorting"""
    try:
        # Get query parameters
        timeframe = request.args.get('timeframe', 'all')
        sort_by = request.args.get('sort_by', 'score')
        
        # Get all users data from DATABASE
        all_users_stats = get_all_users_data()
        
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
        
        return jsonify({
            'success': True,
            'leaderboard': limited_data,
            'timeframe': timeframe,
            'sort_by': sort_by,
            'total_users': len(limited_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to load leaderboard: {str(e)}'
        }), 500

@leaderboard_bp.route('/api/leaderboard/current-user-rank')
def get_current_user_rank():
    """Get current user's rank and stats from DATABASE"""
    try:
        current_user_id = session.get('user_id')
        if not current_user_id:
            return jsonify({
                'success': False,
                'error': 'User not authenticated'
            }), 401
        
        # Get user from database
        current_user = User.query.get(current_user_id)
        if not current_user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        all_users_stats = get_all_users_data()
        
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
            return jsonify({
                'success': False,
                'error': 'User data not found in leaderboard'
            }), 404
        
        return jsonify({
            'success': True,
            'rank': current_user_rank,
            'user_data': current_user_data,
            'total_users': len(sorted_by_score)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get user rank: {str(e)}'
        }), 500

@leaderboard_bp.route('/api/leaderboard/achievements', methods=['GET'])
def get_leaderboard_achievements():
    """Get achievements for leaderboard display from DATABASE"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User not authenticated'
            }), 401
        
        # Get user's achievements from database
        user_achievements = UserAchievement.query.filter_by(user_id=user_id).all()
        
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
        return jsonify({
            'success': False,
            'message': f'Error retrieving achievements: {str(e)}'
        }), 500

@leaderboard_bp.route('/api/leaderboard/stats', methods=['GET'])
def get_leaderboard_stats():
    """Get user stats for leaderboard progress bars from DATABASE"""
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
        
        return jsonify({
            'success': True,
            'message': 'Scores updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating scores: {str(e)}'
        }), 500

def initialize_sample_users():
    """Initialize sample users in database for testing"""
    try:
        # Check if sample users already exist
        existing_users = User.query.filter(
            User.username.in_(['ChineseMaster', 'PinyinPro', 'HanziHero', 'MandarinLearner'])
        ).count()
        
        if existing_users > 0:
            return  # Sample users already exist
        
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
        
        db.session.commit()
        print("Sample users initialized in database")
        
    except Exception as e:
        print(f"Error initializing sample users: {e}")
        db.session.rollback()

# Initialize sample users when the module is imported
initialize_sample_users()