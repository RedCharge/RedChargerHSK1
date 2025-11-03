from flask import Blueprint, render_template, jsonify, request

# Create blueprint
profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
def profile_page():
    """Serve the profile.html page"""
    return render_template('profile.html')

@profile_bp.route('/api/profile/save', methods=['POST'])
def save_profile():
    """API endpoint to save profile data"""
    try:
        profile_data = request.get_json()
        
        if not profile_data:
            return jsonify({
                'success': False,
                'message': 'No profile data provided'
            }), 400
        
        # Here you would typically save to a database
        # For now, we'll just return success
        print("Profile data received:", profile_data)
        
        return jsonify({
            'success': True,
            'message': 'Profile saved successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error saving profile: {str(e)}'
        }), 500

@profile_bp.route('/api/profile/stats')
def get_profile_stats():
    """API endpoint to get user statistics"""
    try:
        # Mock data - replace with actual user statistics from your database
        stats = {
            'totalWords': 150,
            'totalSentences': 75,
            'streakDays': 12,
            'accuracyRate': 85,
            'quizzesCompleted': 8,
            'totalStudyTime': 360  # in minutes
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
    """API endpoint to get user achievements"""
    try:
        # Mock achievements data
        achievements = [
            {
                'id': 1,
                'name': 'First Steps',
                'description': 'Complete your first quiz',
                'icon': 'fas fa-footsteps',
                'unlocked': True,
                'dateUnlocked': '2024-01-15'
            },
            {
                'id': 2,
                'name': 'Word Master',
                'description': 'Learn 100 words',
                'icon': 'fas fa-book',
                'unlocked': True,
                'dateUnlocked': '2024-01-20'
            },
            {
                'id': 3,
                'name': 'Sentence Builder',
                'description': 'Master 50 sentences',
                'icon': 'fas fa-comments',
                'unlocked': False,
                'progress': 75  # 75 out of 50? This should be percentage
            },
            {
                'id': 4,
                'name': 'Perfect Score',
                'description': 'Get 100% on any quiz',
                'icon': 'fas fa-star',
                'unlocked': True,
                'dateUnlocked': '2024-01-18'
            },
            {
                'id': 5,
                'name': 'Week Warrior',
                'description': 'Maintain a 7-day streak',
                'icon': 'fas fa-fire',
                'unlocked': False,
                'progress': 85  # 6 out of 7 days
            }
        ]
        
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
    """API endpoint to get user learning history"""
    try:
        # Mock learning history data
        learning_history = [
            {
                'date': '2024-01-20',
                'activity': 'Words Quiz',
                'score': 90,
                'timeSpent': 15,
                'itemsLearned': 20
            },
            {
                'date': '2024-01-19',
                'activity': 'Sentences Quiz',
                'score': 85,
                'timeSpent': 20,
                'itemsLearned': 15
            },
            {
                'date': '2024-01-18',
                'activity': 'Reading Practice',
                'score': None,
                'timeSpent': 25,
                'itemsLearned': 5
            },
            {
                'date': '2024-01-17',
                'activity': 'Words Quiz',
                'score': 95,
                'timeSpent': 18,
                'itemsLearned': 20
            },
            {
                'date': '2024-01-16',
                'activity': 'Learning Session',
                'score': None,
                'timeSpent': 30,
                'itemsLearned': 25
            }
        ]
        
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
    """API endpoint to export all user data"""
    try:
        # Mock comprehensive user data
        user_data = {
            'profile': {
                'username': 'current_user',
                'email': 'user@example.com',
                'firstName': 'John',
                'lastName': 'Doe',
                'memberSince': '2024-01-01',
                'learningPreferences': {
                    'dailyGoal': 20,
                    'learningMode': 'both',
                    'enableSpeech': True,
                    'showPinyin': True
                }
            },
            'statistics': {
                'totalWords': 150,
                'totalSentences': 75,
                'streakDays': 12,
                'accuracyRate': 85,
                'totalQuizzes': 8,
                'totalStudyTime': 360
            },
            'achievements': [
                {'name': 'First Steps', 'unlocked': True},
                {'name': 'Word Master', 'unlocked': True},
                {'name': 'Perfect Score', 'unlocked': True}
            ],
            'learningHistory': [
                {'date': '2024-01-20', 'activity': 'Words Quiz', 'score': 90},
                {'date': '2024-01-19', 'activity': 'Sentences Quiz', 'score': 85}
            ]
        }
        
        return jsonify({
            'success': True,
            'data': user_data,
            'exportDate': '2024-01-21'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error exporting data: {str(e)}'
        }), 500

@profile_bp.route('/api/profile/upload-avatar', methods=['POST'])
def upload_avatar():
    """API endpoint to handle avatar uploads"""
    try:
        # This would typically handle file uploads
        # For now, we'll just return success
        avatar_data = request.get_json()
        
        if not avatar_data or 'avatar' not in avatar_data:
            return jsonify({
                'success': False,
                'message': 'No avatar data provided'
            }), 400
        
        print("Avatar data received (base64 encoded)")
        
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
        # This would typically delete user data from the database
        confirmation = request.get_json()
        
        if not confirmation or not confirmation.get('confirm'):
            return jsonify({
                'success': False,
                'message': 'Account deletion not confirmed'
            }), 400
        
        print("Account deletion requested")
        
        return jsonify({
            'success': True,
            'message': 'Account deleted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting account: {str(e)}'
        }), 500