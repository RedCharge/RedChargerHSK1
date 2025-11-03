from flask import Blueprint, jsonify, request, session
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Any

# Create Blueprint for leaderboard routes
leaderboard_bp = Blueprint('leaderboard', __name__)

# Mock user data storage (in production, use a database)
USERS_DATA_FILE = 'data/users.json'
QUIZ_HISTORY_FILE = 'data/quiz_history.json'

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

def get_user_stats(user_id: str) -> Dict[str, Any]:
    """Calculate comprehensive user statistics"""
    users_data = load_users_data()
    quiz_history = load_quiz_history()
    
    user_data = users_data.get(user_id, {})
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
    
    return {
        'user_id': user_id,
        'username': user_data.get('username', 'Anonymous'),
        'avatar': user_data.get('avatar', ''),
        'score': score,
        'words_mastered': total_words,
        'sentences_mastered': total_sentences,
        'current_streak': current_streak,
        'accuracy_rate': accuracy_rate,
        'level': determine_level(total_words, total_sentences, accuracy_rate),
        'achievements': user_data.get('achievements', []),
        'is_current_user': False  # This will be set when building leaderboard
    }

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

def filter_leaderboard_by_timeframe(leaderboard_data: List[Dict], timeframe: str) -> List[Dict]:
    """Filter leaderboard data based on timeframe"""
    if timeframe == 'all':
        return leaderboard_data
    
    now = datetime.now()
    if timeframe == 'weekly':
        cutoff_date = now - timedelta(days=7)
    elif timeframe == 'monthly':
        cutoff_date = now - timedelta(days=30)
    else:
        return leaderboard_data
    
    # In a real implementation, you would filter quiz history by date
    # and recalculate scores for the timeframe
    # For now, we'll return all data as we don't have date-based scoring
    return leaderboard_data

def sort_leaderboard_data(leaderboard_data: List[Dict], sort_by: str) -> List[Dict]:
    """Sort leaderboard data based on the specified criteria"""
    if sort_by == 'words':
        return sorted(leaderboard_data, key=lambda x: x['words_mastered'], reverse=True)
    elif sort_by == 'sentences':
        return sorted(leaderboard_data, key=lambda x: x['sentences_mastered'], reverse=True)
    elif sort_by == 'streak':
        return sorted(leaderboard_data, key=lambda x: x['current_streak'], reverse=True)
    else:  # Default to score
        return sorted(leaderboard_data, key=lambda x: x['score'], reverse=True)

@leaderboard_bp.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get leaderboard data with optional filtering and sorting"""
    try:
        # Get query parameters
        timeframe = request.args.get('timeframe', 'all')
        sort_by = request.args.get('sort_by', 'score')
        current_user_id = session.get('user_id')
        
        # Load all users data
        users_data = load_users_data()
        
        # Calculate stats for all users
        leaderboard_data = []
        for user_id in users_data.keys():
            user_stats = get_user_stats(user_id)
            leaderboard_data.append(user_stats)
        
        # Filter by timeframe
        filtered_data = filter_leaderboard_by_timeframe(leaderboard_data, timeframe)
        
        # Sort the data
        sorted_data = sort_leaderboard_data(filtered_data, sort_by)
        
        # Mark current user
        for user in sorted_data:
            if user['user_id'] == current_user_id:
                user['is_current_user'] = True
                break
        
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

@leaderboard_bp.route('/api/leaderboard/user/<user_id>', methods=['GET'])
def get_user_leaderboard_data(user_id):
    """Get specific user's leaderboard data"""
    try:
        user_stats = get_user_stats(user_id)
        
        # Calculate rank
        users_data = load_users_data()
        all_users_stats = [get_user_stats(uid) for uid in users_data.keys()]
        sorted_users = sorted(all_users_stats, key=lambda x: x['score'], reverse=True)
        
        rank = next((i + 1 for i, user in enumerate(sorted_users) if user['user_id'] == user_id), None)
        
        return jsonify({
            'success': True,
            'user_data': user_stats,
            'rank': rank,
            'total_users': len(sorted_users)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to load user data: {str(e)}'
        }), 500

@leaderboard_bp.route('/api/leaderboard/current-user', methods=['GET'])
def get_current_user_leaderboard():
    """Get current user's leaderboard data and rank"""
    try:
        current_user_id = session.get('user_id')
        if not current_user_id:
            return jsonify({
                'success': False,
                'error': 'User not authenticated'
            }), 401
        
        user_stats = get_user_stats(current_user_id)
        user_stats['is_current_user'] = True
        
        # Calculate rank
        users_data = load_users_data()
        all_users_stats = [get_user_stats(uid) for uid in users_data.keys()]
        sorted_users = sorted(all_users_stats, key=lambda x: x['score'], reverse=True)
        
        rank = next((i + 1 for i, user in enumerate(sorted_users) if user['user_id'] == current_user_id), None)
        
        return jsonify({
            'success': True,
            'user_data': user_stats,
            'rank': rank,
            'total_users': len(sorted_users)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to load current user data: {str(e)}'
        }), 500

@leaderboard_bp.route('/api/leaderboard/achievements', methods=['GET'])
def get_user_achievements():
    """Get current user's achievements"""
    try:
        current_user_id = session.get('user_id')
        if not current_user_id:
            return jsonify({
                'success': False,
                'error': 'User not authenticated'
            }), 401
        
        users_data = load_users_data()
        user_data = users_data.get(current_user_id, {})
        
        achievements = user_data.get('achievements', [])
        
        # Mock achievements data (in production, calculate based on user progress)
        all_achievements = [
            {
                'name': 'Word Master',
                'description': 'Master 100+ words',
                'icon': 'fas fa-book',
                'unlocked': len([a for a in achievements if a.get('name') == 'Word Master']) > 0,
                'date': next((a.get('date') for a in achievements if a.get('name') == 'Word Master'), None)
            },
            {
                'name': 'Perfect Score',
                'description': 'Get 100% on any quiz',
                'icon': 'fas fa-star',
                'unlocked': len([a for a in achievements if a.get('name') == 'Perfect Score']) > 0,
                'date': next((a.get('date') for a in achievements if a.get('name') == 'Perfect Score'), None)
            },
            {
                'name': 'Week Warrior',
                'description': '7-day learning streak',
                'icon': 'fas fa-fire',
                'unlocked': len([a for a in achievements if a.get('name') == 'Week Warrior']) > 0,
                'progress': user_data.get('current_streak', 0) / 7 * 100
            },
            {
                'name': 'Sentence Builder',
                'description': 'Master 50+ sentences',
                'icon': 'fas fa-comments',
                'unlocked': len([a for a in achievements if a.get('name') == 'Sentence Builder']) > 0,
                'date': next((a.get('date') for a in achievements if a.get('name') == 'Sentence Builder'), None)
            }
        ]
        
        return jsonify({
            'success': True,
            'achievements': all_achievements
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to load achievements: {str(e)}'
        }), 500

@leaderboard_bp.route('/api/leaderboard/stats', methods=['GET'])
def get_user_stats_route():
    """Get current user's detailed statistics"""
    try:
        current_user_id = session.get('user_id')
        if not current_user_id:
            return jsonify({
                'success': False,
                'error': 'User not authenticated'
            }), 401
        
        user_stats = get_user_stats(current_user_id)
        
        return jsonify({
            'success': True,
            'stats': {
                'words_mastered': user_stats['words_mastered'],
                'sentences_mastered': user_stats['sentences_mastered'],
                'current_streak': user_stats['current_streak'],
                'accuracy_rate': user_stats['accuracy_rate'],
                'total_score': user_stats['score'],
                'level': user_stats['level']
            },
            'progress': {
                'words': {
                    'current': user_stats['words_mastered'],
                    'total': 150,
                    'percentage': round((user_stats['words_mastered'] / 150) * 100)
                },
                'sentences': {
                    'current': user_stats['sentences_mastered'],
                    'total': 100,
                    'percentage': round((user_stats['sentences_mastered'] / 100) * 100)
                },
                'streak': {
                    'current': user_stats['current_streak'],
                    'total': 7,
                    'percentage': round((user_stats['current_streak'] / 7) * 100)
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to load user stats: {str(e)}'
        }), 500

# Mock data initialization (for development)
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
        }
    }
    
    # Only save if file doesn't exist
    if not os.path.exists(USERS_DATA_FILE):
        save_users_data(users_data)

# Initialize mock data when the module is imported
initialize_mock_data()