from flask import Blueprint, jsonify, request, session
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Any

leaderboard_bp = Blueprint('leaderboard', __name__)

class LeaderboardService:
    def __init__(self):
        self.data_dir = 'user_data'
        os.makedirs(self.data_dir, exist_ok=True)
    
    def get_user_file_path(self, user_id: str) -> str:
        return os.path.join(self.data_dir, f'{user_id}.json')
    
    def save_user_data(self, user_id: str, user_data: Dict[str, Any]):
        """Save user data to file"""
        try:
            file_path = self.get_user_file_path(user_id)
            with open(file_path, 'w') as f:
                json.dump(user_data, f, indent=2)
        except Exception as e:
            print(f"Error saving user data: {e}")
    
    def load_user_data(self, user_id: str) -> Dict[str, Any]:
        """Load user data from file"""
        try:
            file_path = self.get_user_file_path(user_id)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading user data: {e}")
        return {}
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users from data directory"""
        users = []
        try:
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json'):
                    user_id = filename[:-5]  # Remove .json extension
                    user_data = self.load_user_data(user_id)
                    if user_data:
                        users.append({
                            'id': user_id,
                            **user_data
                        })
        except Exception as e:
            print(f"Error loading all users: {e}")
        return users
    
    def calculate_user_stats(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive user statistics"""
        quiz_history = user_data.get('quiz_history', [])
        performance_data = user_data.get('performance_data', {})
        
        # Initialize counters
        stats = {
            'totalWords': 0,
            'totalSentences': 0,
            'streakDays': 0,
            'accuracyRate': 0,
            'totalQuizzes': len(quiz_history),
            'wordsMastered': 0,
            'sentencesMastered': 0,
            'totalScore': 0,
            'lastActivity': None,
            'level': 1,
            'xp': 0
        }
        
        # Calculate from quiz history
        total_correct = 0
        total_questions = 0
        
        for quiz in quiz_history:
            correct = quiz.get('correct_answers', quiz.get('correct', 0))
            total = quiz.get('total_questions', quiz.get('total', 0))
            
            total_correct += correct
            total_questions += total
            
            # Count words vs sentences
            quiz_type = quiz.get('quiz_type', 'words')
            if quiz_type == 'words':
                stats['totalWords'] += correct
            elif quiz_type == 'sentences':
                stats['totalSentences'] += correct
        
        # Calculate mastered items from performance data
        words_data = performance_data.get('words', {})
        sentences_data = performance_data.get('sentences', {})
        
        # Words mastery
        for word_data in words_data.values():
            correct = word_data.get('correct', 0)
            incorrect = word_data.get('incorrect', 0)
            total_attempts = correct + incorrect
            
            if total_attempts > 0:
                accuracy = (correct / total_attempts) * 100
                if accuracy >= 70:  # Consider mastered if 70%+ accuracy
                    stats['wordsMastered'] += 1
        
        # Sentences mastery
        for sentence_data in sentences_data.values():
            correct = sentence_data.get('correct', 0)
            incorrect = sentence_data.get('incorrect', 0)
            total_attempts = correct + incorrect
            
            if total_attempts > 0:
                accuracy = (correct / total_attempts) * 100
                if accuracy >= 70:
                    stats['sentencesMastered'] += 1
        
        # Update totals
        stats['totalWords'] = max(stats['totalWords'], len(words_data))
        stats['totalSentences'] = max(stats['totalSentences'], len(sentences_data))
        
        # Calculate streak
        stats['streakDays'] = self.calculate_streak(quiz_history)
        
        # Calculate accuracy
        if total_questions > 0:
            stats['accuracyRate'] = round((total_correct / total_questions) * 100)
        
        # Calculate total score (weighted scoring system)
        stats['totalScore'] = (
            stats['wordsMastered'] * 2 +
            stats['sentencesMastered'] * 3 +
            stats['streakDays'] * 5 +
            stats['accuracyRate']
        )
        
        # Calculate XP and level
        stats['xp'] = stats['totalScore']
        stats['level'] = (stats['xp'] // 100) + 1
        
        # Get last activity
        if quiz_history:
            try:
                latest_quiz = max(quiz_history, 
                                key=lambda x: x.get('timestamp', x.get('date', '2000-01-01')))
                stats['lastActivity'] = latest_quiz.get('timestamp', latest_quiz.get('date'))
            except:
                stats['lastActivity'] = None
        
        return stats
    
    def calculate_streak(self, quiz_history: List[Dict[str, Any]]) -> int:
        """Calculate user's current study streak"""
        if not quiz_history:
            return 0
        
        # Get unique dates
        unique_dates = set()
        for quiz in quiz_history:
            date_str = quiz.get('timestamp', quiz.get('date', ''))
            try:
                # Handle different date formats
                if 'T' in date_str:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
                else:
                    date_obj = datetime.strptime(date_str.split('T')[0], '%Y-%m-%d').date()
                unique_dates.add(date_obj)
            except:
                continue
        
        if not unique_dates:
            return 0
        
        # Sort dates
        sorted_dates = sorted(unique_dates, reverse=True)
        
        streak = 0
        current_date = datetime.now().date()
        
        # Check today
        if sorted_dates[0] == current_date:
            streak = 1
            current_date -= timedelta(days=1)
        else:
            return 0
        
        # Check consecutive days
        for date in sorted_dates[1:]:
            if date == current_date:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return streak
    
    def sort_users(self, users: List[Dict[str, Any]], criteria: str) -> List[Dict[str, Any]]:
        """Sort users based on ranking criteria"""
        reverse = True  # Most rankings are descending
        
        if criteria == 'words':
            key = lambda u: u['stats']['wordsMastered']
        elif criteria == 'sentences':
            key = lambda u: u['stats']['sentencesMastered']
        elif criteria == 'streak':
            key = lambda u: u['stats']['streakDays']
        elif criteria == 'accuracy':
            key = lambda u: u['stats']['accuracyRate']
        elif criteria == 'activity':
            # Sort by last activity date
            key = lambda u: u['stats'].get('lastActivity') or '2000-01-01'
            reverse = False  # Most recent first
        elif criteria == 'level':
            key = lambda u: u['stats']['level']
        else:  # overall
            key = lambda u: u['stats']['totalScore']
        
        return sorted(users, key=key, reverse=reverse)
    
    def get_user_achievements(self, stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate user achievements based on stats"""
        achievements = []
        
        # Streak achievements
        if stats['streakDays'] >= 7:
            achievements.append({
                'id': 'weekly_warrior',
                'title': 'Weekly Warrior',
                'description': 'Maintained a 7-day study streak',
                'icon': 'fa-fire',
                'unlocked': True,
                'progress': 100
            })
        elif stats['streakDays'] > 0:
            achievements.append({
                'id': 'weekly_warrior',
                'title': 'Weekly Warrior',
                'description': 'Maintain a 7-day study streak',
                'icon': 'fa-fire',
                'unlocked': False,
                'progress': min((stats['streakDays'] / 7) * 100, 100)
            })
        
        # Word achievements
        if stats['wordsMastered'] >= 50:
            achievements.append({
                'id': 'word_master',
                'title': 'Word Master',
                'description': 'Mastered 50+ vocabulary words',
                'icon': 'fa-font',
                'unlocked': True,
                'progress': 100
            })
        elif stats['wordsMastered'] > 0:
            achievements.append({
                'id': 'word_master',
                'title': 'Word Master',
                'description': 'Master 50+ vocabulary words',
                'icon': 'fa-font',
                'unlocked': False,
                'progress': min((stats['wordsMastered'] / 50) * 100, 100)
            })
        
        # Sentence achievements
        if stats['sentencesMastered'] >= 30:
            achievements.append({
                'id': 'sentence_builder',
                'title': 'Sentence Builder',
                'description': 'Mastered 30+ sentences',
                'icon': 'fa-comment-alt',
                'unlocked': True,
                'progress': 100
            })
        elif stats['sentencesMastered'] > 0:
            achievements.append({
                'id': 'sentence_builder',
                'title': 'Sentence Builder',
                'description': 'Master 30+ sentences',
                'icon': 'fa-comment-alt',
                'unlocked': False,
                'progress': min((stats['sentencesMastered'] / 30) * 100, 100)
            })
        
        # Accuracy achievements
        if stats['accuracyRate'] >= 80:
            achievements.append({
                'id': 'accuracy_expert',
                'title': 'Accuracy Expert',
                'description': 'Maintained 80%+ accuracy rate',
                'icon': 'fa-bullseye',
                'unlocked': True,
                'progress': 100
            })
        elif stats['accuracyRate'] > 0:
            achievements.append({
                'id': 'accuracy_expert',
                'title': 'Accuracy Expert',
                'description': 'Maintain 80%+ accuracy rate',
                'icon': 'fa-bullseye',
                'unlocked': False,
                'progress': min((stats['accuracyRate'] / 80) * 100, 100)
            })
        
        # Quiz count achievements
        if stats['totalQuizzes'] >= 10:
            achievements.append({
                'id': 'quiz_champion',
                'title': 'Quiz Champion',
                'description': 'Completed 10+ quizzes',
                'icon': 'fa-trophy',
                'unlocked': True,
                'progress': 100
            })
        elif stats['totalQuizzes'] > 0:
            achievements.append({
                'id': 'quiz_champion',
                'title': 'Quiz Champion',
                'description': 'Complete 10+ quizzes',
                'icon': 'fa-trophy',
                'unlocked': False,
                'progress': min((stats['totalQuizzes'] / 10) * 100, 100)
            })
        
        # Level achievements
        if stats['level'] >= 5:
            achievements.append({
                'id': 'level_master',
                'title': 'Level Master',
                'description': 'Reached level 5',
                'icon': 'fa-star',
                'unlocked': True,
                'progress': 100
            })
        elif stats['level'] > 1:
            achievements.append({
                'id': 'level_master',
                'title': 'Level Master',
                'description': 'Reach level 5',
                'icon': 'fa-star',
                'unlocked': False,
                'progress': min((stats['level'] / 5) * 100, 100)
            })
        
        return achievements

# Initialize service
leaderboard_service = LeaderboardService()

@leaderboard_bp.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get leaderboard data with various ranking options"""
    try:
        # Get query parameters
        criteria = request.args.get('criteria', 'overall')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        include_current_user = request.args.get('include_current_user', 'true').lower() == 'true'
        
        # Validate criteria
        valid_criteria = ['overall', 'words', 'sentences', 'streak', 'accuracy', 'activity', 'level']
        if criteria not in valid_criteria:
            return jsonify({'error': 'Invalid criteria'}), 400
        
        # Get all users
        users = leaderboard_service.get_all_users()
        
        # Calculate stats for each user
        ranked_users = []
        current_user_id = session.get('user_id')
        
        for user in users:
            stats = leaderboard_service.calculate_user_stats(user)
            user_data = {
                'id': user['id'],
                'username': user.get('username', 'Anonymous'),
                'avatar': user.get('avatar'),
                'stats': stats,
                'isCurrentUser': user['id'] == current_user_id
            }
            ranked_users.append(user_data)
        
        # Sort users based on criteria
        sorted_users = leaderboard_service.sort_users(ranked_users, criteria)
        
        # Filter out current user if needed (for pagination testing)
        if not include_current_user:
            sorted_users = [u for u in sorted_users if not u['isCurrentUser']]
        
        # Apply pagination
        paginated_users = sorted_users[offset:offset + limit]
        
        # Calculate global stats
        global_stats = calculate_global_stats(ranked_users)
        
        # Get current user rank if available
        current_user_rank = None
        if current_user_id:
            for i, user in enumerate(sorted_users):
                if user['id'] == current_user_id:
                    current_user_rank = i + 1
                    break
        
        response = {
            'success': True,
            'leaderboard': paginated_users,
            'globalStats': global_stats,
            'currentUserRank': current_user_rank,
            'pagination': {
                'total': len(sorted_users),
                'limit': limit,
                'offset': offset,
                'hasMore': offset + limit < len(sorted_users)
            },
            'criteria': criteria,
            'lastUpdated': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leaderboard_bp.route('/api/leaderboard/user/<user_id>', methods=['GET'])
def get_user_rank(user_id):
    """Get specific user's rank and stats"""
    try:
        users = leaderboard_service.get_all_users()
        ranked_users = []
        
        for user in users:
            stats = leaderboard_service.calculate_user_stats(user)
            ranked_users.append({
                'id': user['id'],
                'username': user.get('username', 'Anonymous'),
                'avatar': user.get('avatar'),
                'stats': stats,
                'isCurrentUser': user['id'] == user_id
            })
        
        # Sort by overall score
        sorted_users = leaderboard_service.sort_users(ranked_users, 'overall')
        
        # Find user rank and data
        user_rank = None
        user_data = None
        
        for i, user in enumerate(sorted_users):
            if user['id'] == user_id:
                user_rank = i + 1
                user_data = user
                break
        
        if not user_data:
            return jsonify({'error': 'User not found'}), 404
        
        # Get achievements with progress
        achievements = leaderboard_service.get_user_achievements(user_data['stats'])
        
        response = {
            'success': True,
            'user': user_data,
            'rank': user_rank,
            'totalUsers': len(sorted_users),
            'achievements': achievements
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leaderboard_bp.route('/api/leaderboard/current-user', methods=['GET'])
def get_current_user_rank():
    """Get current user's rank and stats"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        return get_user_rank(user_id)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leaderboard_bp.route('/api/leaderboard/achievements', methods=['GET'])
def get_achievements():
    """Get achievements for current user"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        user_data = leaderboard_service.load_user_data(user_id)
        stats = leaderboard_service.calculate_user_stats(user_data)
        achievements = leaderboard_service.get_user_achievements(stats)
        
        return jsonify({
            'success': True,
            'achievements': achievements
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leaderboard_bp.route('/api/leaderboard/global-stats', methods=['GET'])
def get_global_stats():
    """Get global learning statistics"""
    try:
        users = leaderboard_service.get_all_users()
        global_stats = calculate_global_stats(users)
        
        return jsonify({
            'success': True,
            'globalStats': global_stats,
            'lastUpdated': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leaderboard_bp.route('/api/leaderboard/update', methods=['POST'])
def update_leaderboard():
    """Update user data from frontend (called when user completes quiz)"""
    try:
        data = request.get_json()
        user_id = data.get('user_id') or session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        # Load existing user data
        user_data = leaderboard_service.load_user_data(user_id)
        
        # Initialize user data if doesn't exist
        if not user_data:
            user_data = {
                'username': data.get('username', f'User{user_id[-6:]}'),
                'quiz_history': [],
                'performance_data': {
                    'words': {},
                    'sentences': {}
                },
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
        
        # Update with new data
        if 'quiz_results' in data:
            if 'quiz_history' not in user_data:
                user_data['quiz_history'] = []
            
            # Add timestamp if not present
            quiz_result = data['quiz_results']
            if 'timestamp' not in quiz_result:
                quiz_result['timestamp'] = datetime.now().isoformat()
            
            user_data['quiz_history'].append(quiz_result)
        
        if 'performance_data' in data:
            # Merge performance data
            if 'words' in data['performance_data']:
                user_data['performance_data']['words'].update(data['performance_data']['words'])
            if 'sentences' in data['performance_data']:
                user_data['performance_data']['sentences'].update(data['performance_data']['sentences'])
        
        if 'profile' in data:
            user_data.update(data['profile'])
        
        # Update timestamp
        user_data['last_updated'] = datetime.now().isoformat()
        
        # Save updated data
        leaderboard_service.save_user_data(user_id, user_data)
        
        # Return updated stats
        updated_stats = leaderboard_service.calculate_user_stats(user_data)
        
        return jsonify({
            'success': True,
            'message': 'Leaderboard data updated successfully',
            'stats': updated_stats,
            'user_id': user_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leaderboard_bp.route('/api/leaderboard/recent-activity', methods=['GET'])
def get_recent_activity():
    """Get recent user activity for the activity feed"""
    try:
        users = leaderboard_service.get_all_users()
        recent_activities = []
        
        for user in users:
            quiz_history = user.get('quiz_history', [])
            if quiz_history:
                # Get latest quiz
                latest_quiz = max(quiz_history, 
                                key=lambda x: x.get('timestamp', x.get('date', '')))
                
                recent_activities.append({
                    'user_id': user['id'],
                    'username': user.get('username', 'Anonymous'),
                    'avatar': user.get('avatar'),
                    'activity_type': 'quiz_completed',
                    'quiz_type': latest_quiz.get('quiz_type', 'words'),
                    'score': latest_quiz.get('percentage', 0),
                    'timestamp': latest_quiz.get('timestamp', latest_quiz.get('date')),
                    'details': f"Scored {latest_quiz.get('percentage', 0)}% on {latest_quiz.get('quiz_type', 'words')} quiz"
                })
        
        # Sort by timestamp
        recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Limit to 20 most recent
        recent_activities = recent_activities[:20]
        
        return jsonify({
            'success': True,
            'recentActivity': recent_activities
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_global_stats(users: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate global statistics across all users"""
    if not users:
        return {
            'totalUsers': 0,
            'totalQuizzes': 0,
            'totalWords': 0,
            'totalSentences': 0,
            'averageAccuracy': 0,
            'averageStreak': 0,
            'averageLevel': 1,
            'totalXP': 0
        }
    
    total_quizzes = 0
    total_words = 0
    total_sentences = 0
    total_accuracy = 0
    total_streak = 0
    total_level = 0
    total_xp = 0
    
    for user in users:
        stats = user.get('stats', {})
        total_quizzes += stats.get('totalQuizzes', 0)
        total_words += stats.get('wordsMastered', 0)
        total_sentences += stats.get('sentencesMastered', 0)
        total_accuracy += stats.get('accuracyRate', 0)
        total_streak += stats.get('streakDays', 0)
        total_level += stats.get('level', 1)
        total_xp += stats.get('xp', 0)
    
    return {
        'totalUsers': len(users),
        'totalQuizzes': total_quizzes,
        'totalWords': total_words,
        'totalSentences': total_sentences,
        'averageAccuracy': round(total_accuracy / len(users), 1),
        'averageStreak': round(total_streak / len(users), 1),
        'averageLevel': round(total_level / len(users), 1),
        'totalXP': total_xp
    }

# Utility function to initialize user data
def initialize_user_data(user_id: str, username: str = None):
    """Initialize user data when they first register"""
    user_data = {
        'username': username or f'User{user_id[-6:]}',
        'quiz_history': [],
        'performance_data': {
            'words': {},
            'sentences': {}
        },
        'created_at': datetime.now().isoformat(),
        'last_updated': datetime.now().isoformat()
    }
    
    leaderboard_service.save_user_data(user_id, user_data)
    return user_data

# Admin routes (optional)
@leaderboard_bp.route('/admin/leaderboard/reset', methods=['POST'])
def admin_reset_leaderboard():
    """Admin route to reset leaderboard (use with caution)"""
    try:
        # Add authentication check here in production
        # if not is_admin(): return jsonify({'error': 'Unauthorized'}), 403
        
        # Clear all user data
        for filename in os.listdir(leaderboard_service.data_dir):
            if filename.endswith('.json'):
                os.remove(os.path.join(leaderboard_service.data_dir, filename))
        
        return jsonify({'success': True, 'message': 'Leaderboard reset successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leaderboard_bp.route('/admin/leaderboard/users', methods=['GET'])
def admin_get_all_users():
    """Admin route to get all users (for moderation)"""
    try:
        # Add authentication check here in production
        # if not is_admin(): return jsonify({'error': 'Unauthorized'}), 403
        
        users = leaderboard_service.get_all_users()
        return jsonify({
            'success': True,
            'users': users,
            'total': len(users)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
def initialize_sample_data():
    """Initialize sample leaderboard data for demonstration"""
    sample_users = [
        {
            'id': 'user1',
            'username': 'LanguageMaster',
            'avatar': '',
            'quiz_history': [
                {'quiz_type': 'words', 'correct_answers': 8, 'total_questions': 10, 'percentage': 80, 'timestamp': '2024-01-15T10:30:00'},
                {'quiz_type': 'sentences', 'correct_answers': 9, 'total_questions': 10, 'percentage': 90, 'timestamp': '2024-01-14T14:20:00'}
            ],
            'performance_data': {
                'words': {
                    '你好': {'correct': 3, 'incorrect': 0, 'pinyin': 'nǐ hǎo', 'meaning': 'hello'},
                    '谢谢': {'correct': 2, 'incorrect': 1, 'pinyin': 'xiè xiè', 'meaning': 'thank you'}
                },
                'sentences': {
                    '你好吗？': {'correct': 2, 'incorrect': 0, 'pinyin': 'nǐ hǎo ma?', 'meaning': 'How are you?'}
                }
            }
        },
        {
            'id': 'user2', 
            'username': 'HSKPro',
            'avatar': '',
            'quiz_history': [
                {'quiz_type': 'words', 'correct_answers': 9, 'total_questions': 10, 'percentage': 90, 'timestamp': '2024-01-15T09:15:00'},
                {'quiz_type': 'sentences', 'correct_answers': 8, 'total_questions': 10, 'percentage': 80, 'timestamp': '2024-01-13T16:45:00'}
            ],
            'performance_data': {
                'words': {
                    '我': {'correct': 4, 'incorrect': 0, 'pinyin': 'wǒ', 'meaning': 'I/me'},
                    '你': {'correct': 3, 'incorrect': 1, 'pinyin': 'nǐ', 'meaning': 'you'}
                },
                'sentences': {
                    '我叫小明': {'correct': 3, 'incorrect': 0, 'pinyin': 'wǒ jiào xiǎo míng', 'meaning': 'My name is Xiaoming'}
                }
            }
        },
        {
            'id': 'user3',
            'username': 'MandarinLearner', 
            'avatar': '',
            'quiz_history': [
                {'quiz_type': 'words', 'correct_answers': 7, 'total_questions': 10, 'percentage': 70, 'timestamp': '2024-01-14T11:20:00'}
            ],
            'performance_data': {
                'words': {
                    '是': {'correct': 2, 'incorrect': 1, 'pinyin': 'shì', 'meaning': 'to be'},
                    '不': {'correct': 1, 'incorrect': 1, 'pinyin': 'bù', 'meaning': 'no/not'}
                }
            }
        }
    ]
    
    # Save sample users
    for user_data in sample_users:
        leaderboard_service.save_user_data(user_data['id'], user_data)
    
    # Return users with calculated stats
    users_with_stats = []
    for user_data in sample_users:
        stats = leaderboard_service.calculate_user_stats(user_data)
        users_with_stats.append({
            'id': user_data['id'],
            'username': user_data['username'],
            'stats': stats
        })
    
    return users_with_stats    