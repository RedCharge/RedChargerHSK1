from flask import Blueprint, jsonify, request, session, render_template
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Any

# Create Blueprint for leaderboard routes
leaderboard_bp = Blueprint('leaderboard', __name__)

# Shared user data storage
USERS_DATA_FILE = 'data/users.json'
QUIZ_HISTORY_FILE = 'data/quiz_history.json'

def get_all_users_data():
    """Get comprehensive data for all users for leaderboard"""
    try:
        users_data = load_users_data()
        quiz_history = load_quiz_history()
        
        all_users_stats = []
        
        for user_id, user_data in users_data.items():
            # Calculate user stats (same as your existing get_user_stats function)
            user_quizzes = quiz_history.get(user_id, [])
            
            # Calculate basic stats
            total_words = user_data.get('words_mastered', 0)
            total_sentences = user_data.get('sentences_mastered', 0)
            current_streak = user_data.get('current_streak', 0)
            
            # Calculate accuracy from quiz history
            total_correct = 0
            total_questions = 0
            
            for quiz in user_quizzes:
                total_correct += quiz.get('correct_answers', 0)
                total_questions += quiz.get('total_questions', 0)
            
            accuracy_rate = round((total_correct / total_questions * 100)) if total_questions > 0 else 0
            
            # Calculate score
            score = calculate_user_score({
                'words_mastered': total_words,
                'sentences_mastered': total_sentences,
                'current_streak': current_streak,
                'accuracy_rate': accuracy_rate
            })
            
            # Determine level
            level = determine_level(total_words, total_sentences, accuracy_rate)
            
            # Mark current user
            is_current_user = user_id == session.get('user_id')
            
            user_stats = {
                'user_id': user_id,
                'username': user_data.get('username', 'Anonymous'),
                'avatar': user_data.get('avatar', ''),
                'score': score,
                'words_mastered': total_words,
                'sentences_mastered': total_sentences,
                'current_streak': current_streak,
                'accuracy_rate': accuracy_rate,
                'level': level,
                'achievements': user_data.get('achievements', []),
                'is_current_user': is_current_user
            }
            
            all_users_stats.append(user_stats)
        
        return all_users_stats
        
    except Exception as e:
        print(f"Error getting all users data: {e}")
        return []

# Your existing functions remain the same...
def load_users_data():
    """Load users data from JSON file"""
    try:
        if os.path.exists(USERS_DATA_FILE):
            with open(USERS_DATA_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading users data: {e}")
    return {}

def save_users_data(data):
    """Save users data to JSON file"""
    try:
        os.makedirs(os.path.dirname(USERS_DATA_FILE), exist_ok=True)
        with open(USERS_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving users data: {e}")

def load_quiz_history():
    """Load quiz history from JSON file"""
    try:
        if os.path.exists(QUIZ_HISTORY_FILE):
            with open(QUIZ_HISTORY_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading quiz history: {e}")
    return {}

def calculate_user_score(user_data: Dict) -> int:
    """Calculate user score based on their performance"""
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

# Your existing routes remain the same...
@leaderboard_bp.route('/leaderboard')
def leaderboard_page():
    """Serve the main leaderboard HTML page"""
    return render_template('leaderboard.html')

@leaderboard_bp.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get leaderboard data with optional filtering and sorting"""
    try:
        # Get query parameters
        timeframe = request.args.get('timeframe', 'all')
        sort_by = request.args.get('sort_by', 'score')
        
        # Get all users data
        all_users_stats = get_all_users_data()
        
        # Sort the data
        if sort_by == 'words':
            sorted_data = sorted(all_users_stats, key=lambda x: x['words_mastered'], reverse=True)
        elif sort_by == 'sentences':
            sorted_data = sorted(all_users_stats, key=lambda x: x['sentences_mastered'], reverse=True)
        elif sort_by == 'streak':
            sorted_data = sorted(all_users_stats, key=lambda x: x['current_streak'], reverse=True)
        else:  # Default to score
            sorted_data = sorted(all_users_stats, key=lambda x: x['score'], reverse=True)
        
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

# Add this new endpoint to get current user's rank and stats
@leaderboard_bp.route('/api/leaderboard/current-user-rank')
def get_current_user_rank():
    """Get current user's rank and stats"""
    try:
        current_user_id = session.get('user_id')
        if not current_user_id:
            return jsonify({
                'success': False,
                'error': 'User not authenticated'
            }), 401
        
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
                'error': 'User data not found'
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

# Your other existing routes...
@leaderboard_bp.route('/api/leaderboard/achievements', methods=['GET'])
def get_user_achievements():
    # ... your existing achievements code
    pass

@leaderboard_bp.route('/api/leaderboard/stats', methods=['GET'])
def get_user_stats_route():
    # ... your existing stats code
    pass

# Mock data initialization (UPDATED WITH MORE USERS)
def initialize_mock_data():
    """Initialize mock data for development and testing"""
    users_data = {
        'user_001': {
            'username': 'ChineseMaster',
            'avatar': '',
            'words_mastered': 150,
            'sentences_mastered': 100,
            'current_streak': 21,
            'achievements': [
                {'name': 'Word Master', 'date': '2024-01-15'},
                {'name': 'Perfect Score', 'date': '2024-01-12'},
                {'name': 'Week Warrior', 'date': '2024-01-20'}
            ]
        },
        'user_002': {
            'username': 'PinyinPro',
            'avatar': '',
            'words_mastered': 148,
            'sentences_mastered': 95,
            'current_streak': 18,
            'achievements': [
                {'name': 'Sentence Builder', 'date': '2024-01-18'},
                {'name': 'Quick Learner', 'date': '2024-01-14'}
            ]
        },
        'user_003': {
            'username': 'HanziHero',
            'avatar': '',
            'words_mastered': 142,
            'sentences_mastered': 88,
            'current_streak': 15,
            'achievements': [
                {'name': 'First Steps', 'date': '2024-01-10'},
                {'name': 'Consistent Learner', 'date': '2024-01-22'}
            ]
        },
        'user_004': {
            'username': 'MandarinLearner',
            'avatar': '',
            'words_mastered': 135,
            'sentences_mastered': 82,
            'current_streak': 12,
            'achievements': [
                {'name': 'Word Collector', 'date': '2024-01-16'}
            ]
        },
        'user_005': {
            'username': 'BeginnerBob',
            'avatar': '',
            'words_mastered': 115,
            'sentences_mastered': 65,
            'current_streak': 5,
            'achievements': [
                {'name': 'First Steps', 'date': '2024-01-08'}
            ]
        },
        'user_006': {
            'username': 'LanguageLover',
            'avatar': '',
            'words_mastered': 98,
            'sentences_mastered': 58,
            'current_streak': 3,
            'achievements': [
                {'name': 'First Steps', 'date': '2024-01-05'}
            ]
        },
        'user_007': {
            'username': 'CurrentUser',  # This will be the logged-in user
            'avatar': '',
            'words_mastered': 128,
            'sentences_mastered': 78,
            'current_streak': 8,
            'achievements': [
                {'name': 'First Steps', 'date': '2024-01-07'},
                {'name': 'Quick Starter', 'date': '2024-01-14'}
            ]
        }
    }
    
    # Only save if file doesn't exist
    if not os.path.exists(USERS_DATA_FILE):
        save_users_data(users_data)

# Initialize mock data when the module is imported
initialize_mock_data()