from flask import Blueprint, render_template, request, jsonify, session
from flask_socketio import emit, join_room, leave_room
from datetime import datetime
import json
import uuid
from flask import request as flask_request

# Import db and models from your models.py
from .models import db, QuizResult, ChatUser, ChatMessage, ChatChannel

# Create Blueprint
main_bp = Blueprint('main', __name__)

# In-memory storage for active users (in production, use Redis)
active_users = {}
typing_users = {}

@main_bp.route('/')
def index():
    """Render the main landing page"""
    return render_template('index.html')

@main_bp.route('/result')
def result():
    """Render the result page"""
    return render_template('result.html')

@main_bp.route('/chat')
def chat():
    """Render the community chat page"""
    return render_template('chat.html')


@main_bp.route('/api/quiz-results', methods=['POST'])
def save_quiz_result():
    """API endpoint to save quiz results to database"""
    try:
        data = request.get_json()
        
        # Create new quiz result
        quiz_result = QuizResult(
            quiz_type=data.get('quiz_type', 'words'),
            score=data.get('score', 0),
            total_questions=data.get('total_questions', 0),
            correct_answers=data.get('correct_answers', 0),
            incorrect_answers=data.get('incorrect_answers', 0),
            percentage=data.get('percentage', 0),
            time_taken=data.get('time_taken', 0),
            timestamp=datetime.utcnow()
        )
        
        # Set user answers using the model method
        quiz_result.set_user_answers(data.get('user_answers', []))
        
        db.session.add(quiz_result)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Quiz result saved successfully',
            'result_id': quiz_result.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error saving quiz result: {str(e)}'
        }), 500

@main_bp.route('/api/quiz-results/<int:result_id>')
def get_quiz_result(result_id):
    """API endpoint to get specific quiz result"""
    try:
        result = QuizResult.query.get_or_404(result_id)
        
        return jsonify({
            'success': True,
            'result': {
                'id': result.id,
                'quiz_type': result.quiz_type,
                'score': result.score,
                'total_questions': result.total_questions,
                'correct_answers': result.correct_answers,
                'incorrect_answers': result.incorrect_answers,
                'percentage': result.percentage,
                'time_taken': result.time_taken,
                'user_answers': result.get_user_answers(),
                'timestamp': result.timestamp.isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving quiz result: {str(e)}'
        }), 500

@main_bp.route('/api/stats')
def get_quiz_stats():
    """API endpoint to get overall quiz statistics"""
    try:
        total_quizzes = QuizResult.query.count()
        words_quizzes = QuizResult.query.filter_by(quiz_type='words').count()
        sentence_quizzes = QuizResult.query.filter_by(quiz_type='sentences').count()
        
        # Get average scores
        words_avg = db.session.query(db.func.avg(QuizResult.percentage)).filter_by(quiz_type='words').scalar() or 0
        sentence_avg = db.session.query(db.func.avg(QuizResult.percentage)).filter_by(quiz_type='sentences').scalar() or 0
        
        # Get best scores
        words_best = db.session.query(db.func.max(QuizResult.percentage)).filter_by(quiz_type='words').scalar() or 0
        sentence_best = db.session.query(db.func.max(QuizResult.percentage)).filter_by(quiz_type='sentences').scalar() or 0
        
        # Get recent activity
        recent_quizzes = QuizResult.query.order_by(QuizResult.timestamp.desc()).limit(5).all()
        recent_activity = [{
            'id': quiz.id,
            'quiz_type': quiz.quiz_type,
            'score': quiz.score,
            'percentage': quiz.percentage,
            'timestamp': quiz.timestamp.isoformat()
        } for quiz in recent_quizzes]
        
        return jsonify({
            'success': True,
            'stats': {
                'total_quizzes': total_quizzes,
                'words_quizzes': words_quizzes,
                'sentence_quizzes': sentence_quizzes,
                'words_average_score': round(float(words_avg), 1),
                'sentence_average_score': round(float(sentence_avg), 1),
                'words_best_score': round(float(words_best), 1),
                'sentence_best_score': round(float(sentence_best), 1),
                'recent_activity': recent_activity
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving stats: {str(e)}'
        }), 500

# Chat API Endpoints
@main_bp.route('/api/chat/register', methods=['POST'])
def register_chat_user():
    """Register or login user for chat"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        level = data.get('level', 'HSK1')
        
        if not username:
            return jsonify({
                'success': False,
                'message': 'Username is required'
            }), 400
        
        if len(username) < 2 or len(username) > 20:
            return jsonify({
                'success': False,
                'message': 'Username must be between 2 and 20 characters'
            }), 400
        
        # Check if username exists
        existing_user = ChatUser.query.filter_by(username=username).first()
        
        if existing_user:
            user = existing_user
            user.is_online = True
            user.last_seen = datetime.utcnow()
        else:
            # Create new user
            user = ChatUser(
                username=username,
                level=level,
                avatar_color=get_avatar_color(username),
                is_online=True
            )
            db.session.add(user)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'level': user.level,
                'avatar_color': user.avatar_color
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error registering user: {str(e)}'
        }), 500

@main_bp.route('/api/chat/channels')
def get_chat_channels():
    """API endpoint to get available chat channels"""
    try:
        channels_data = [
            {
                'id': 'general',
                'name': 'General Chat',
                'description': 'Practice Chinese with everyone',
                'icon': 'users',
                'color': 'primary-blue',
                'member_count': len([u for u in active_users.values()]),
                'unread_count': 0
            },
            {
                'id': 'beginners',
                'name': 'Beginners',
                'description': 'New to Chinese? Start here!',
                'icon': 'seedling',
                'color': 'green-500',
                'member_count': len([u for u in active_users.values() if u.get('level', 'HSK1') in ['HSK1', 'Beginner']]),
                'unread_count': 0
            },
            {
                'id': 'grammar',
                'name': 'Grammar Help',
                'description': 'Ask grammar questions',
                'icon': 'language',
                'color': 'purple-500',
                'member_count': len(active_users) // 2,
                'unread_count': 0
            },
            {
                'id': 'pronunciation',
                'name': 'Pronunciation',
                'description': 'Practice speaking & tones',
                'icon': 'volume-up',
                'color': 'yellow-500',
                'member_count': len(active_users) // 3,
                'unread_count': 0
            },
            {
                'id': 'resources',
                'name': 'Learning Resources',
                'description': 'Share helpful resources',
                'icon': 'link',
                'color': 'red-500',
                'member_count': len(active_users) // 4,
                'unread_count': 0
            }
        ]
        
        return jsonify({
            'success': True,
            'channels': channels_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving channels: {str(e)}'
        }), 500

@main_bp.route('/api/chat/users/online')
def get_online_users():
    """API endpoint to get online users"""
    try:
        online_users_list = list(active_users.values())
        
        return jsonify({
            'success': True,
            'users': online_users_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving online users: {str(e)}'
        }), 500

@main_bp.route('/api/chat/messages', methods=['GET'])
def get_chat_messages():
    """API endpoint to get chat messages"""
    try:
        channel = request.args.get('channel', 'general')
        
        # Get messages from database
        messages = ChatMessage.query.filter_by(channel=channel)\
            .order_by(ChatMessage.timestamp.asc())\
            .limit(100)\
            .all()
        
        messages_data = [{
            'id': msg.id,
            'channel': msg.channel,
            'sender': msg.sender_username,
            'sender_id': msg.sender_id,
            'text': msg.message,
            'pinyin': msg.pinyin,
            'timestamp': msg.timestamp.isoformat(),
            'type': 'received'
        } for msg in messages]
        
        return jsonify({
            'success': True,
            'messages': messages_data,
            'channel': channel
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving chat messages: {str(e)}'
        }), 500

@main_bp.route('/api/chat/send', methods=['POST'])
def send_chat_message():
    """API endpoint to send a chat message"""
    try:
        data = request.get_json()
        message_text = data.get('message', '').strip()
        channel = data.get('channel', 'general')
        sender = data.get('sender', 'You')
        sender_id = data.get('sender_id', '')
        
        if not message_text:
            return jsonify({
                'success': False,
                'message': 'Message cannot be empty'
            }), 400
        
        # Save message to database
        new_message = ChatMessage(
            channel=channel,
            sender_id=sender_id,
            sender_username=sender,
            message=message_text,
            timestamp=datetime.utcnow()
        )
        
        db.session.add(new_message)
        db.session.commit()
        
        # Create response message
        message_data = {
            'id': new_message.id,
            'sender': sender,
            'sender_id': sender_id,
            'text': message_text,
            'timestamp': new_message.timestamp.isoformat(),
            'type': 'sent',
            'channel': channel
        }
        
        return jsonify({
            'success': True,
            'message': 'Message sent successfully',
            'message_data': message_data
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error sending message: {str(e)}'
        }), 500

# Utility functions
def get_avatar_color(username):
    """Generate consistent avatar color based on username"""
    colors = ['primary-blue', 'green-500', 'purple-500', 'yellow-500', 'red-500', 'pink-500', 'indigo-500']
    hash_value = sum(ord(char) for char in username)
    return colors[hash_value % len(colors)]

# Socket.IO Event Handlers
def register_socket_events(socketio):
    """Register all Socket.IO event handlers"""
    
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
        emit('connected', {'message': 'Connected to chat server'})

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')
        # Remove user from active users
        for user_id, user_data in active_users.items():
            if user_data.get('socket_id') == flask_request.sid:
                username = user_data['username']
                del active_users[user_id]
                emit('user_left', {
                    'username': username,
                    'onlineUsers': list(active_users.values())
                }, broadcast=True)
                break

    @socketio.on('user_joined')
    def handle_user_joined(data):
        user_data = {
            'id': data['id'],
            'username': data['username'],
            'level': data.get('level', 'HSK1'),
            'avatar_color': data.get('avatar_color', 'primary-blue'),
            'socket_id': flask_request.sid,
            'joined_at': datetime.utcnow().isoformat()
        }
        
        active_users[data['id']] = user_data
        
        emit('user_joined', {
            'username': data['username'],
            'onlineUsers': list(active_users.values())
        }, broadcast=True)
        
        emit('online_users', list(active_users.values()), broadcast=True)

    @socketio.on('join_channel')
    def handle_join_channel(data):
        channel = data['channel']
        user = data['user']
        
        join_room(channel)
        
        # Get channel message history
        messages = ChatMessage.query.filter_by(channel=channel)\
            .order_by(ChatMessage.timestamp.asc())\
            .limit(100)\
            .all()
        
        messages_data = [{
            'id': msg.id,
            'channel': msg.channel,
            'sender': msg.sender_username,
            'sender_id': msg.sender_id,
            'text': msg.message,
            'pinyin': msg.pinyin,
            'timestamp': msg.timestamp.isoformat(),
            'type': 'received' if msg.sender_id != user['id'] else 'sent'
        } for msg in messages]
        
        emit('channel_history', {
            'channel': channel,
            'messages': messages_data
        })

    @socketio.on('send_message')
    def handle_send_message(data):
        try:
            # Save message to database
            new_message = ChatMessage(
                id=data['id'],
                channel=data['channel'],
                sender_id=data['sender_id'],
                sender_username=data['sender'],
                message=data['text'],
                timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            )
            
            db.session.add(new_message)
            db.session.commit()
            
            # Broadcast to room
            emit('new_message', data, room=data['channel'])
            
            # Confirm delivery to sender
            emit('message_delivered', {
                'messageId': data['id']
            })
            
        except Exception as e:
            print(f"Error saving message: {e}")
            db.session.rollback()

    @socketio.on('typing_start')
    def handle_typing_start(data):
        channel = data['channel']
        user = data['user']
        
        typing_users[user['id']] = {
            'channel': channel,
            'user': user,
            'timestamp': datetime.utcnow()
        }
        
        emit('user_typing', {
            'channel': channel,
            'user': user
        }, room=channel)

    @socketio.on('typing_stop')
    def handle_typing_stop(data):
        channel = data['channel']
        user = data['user']
        
        if user['id'] in typing_users:
            del typing_users[user['id']]
        
        emit('user_stop_typing', {
            'channel': channel,
            'user': user
        }, room=channel)
        
        
    

    @socketio.on('user_left')
    def handle_user_left(data):
        user_id = data.get('id')
        if user_id in active_users:
            username = active_users[user_id]['username']
            del active_users[user_id]
            
            emit('user_left', {
                'username': username,
                'onlineUsers': list(active_users.values())
            }, broadcast=True)