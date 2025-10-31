from flask import Blueprint, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import json
import uuid
from flask import request as flask_request

# Import db and models from your models.py
from .models import db, QuizResult, ChatUser, ChatMessage, ChatChannel

# Create Blueprint
main_bp = Blueprint('main', __name__)

# Initialize SocketIO (you'll need to import this in your main app file)
socketio = SocketIO()

# In-memory storage for active users (in production, use Redis)
active_users = {}
typing_users = {}
chat_messages = []  # Store recent messages

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

# ... [Keep all your existing API routes: /api/quiz-results, /api/stats, etc.] ...

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
        
        # Generate user ID for Socket.IO
        user_id = str(uuid.uuid4())
        
        # Create user data (you can also save to database if needed)
        user_data = {
            'id': user_id,
            'username': username,
            'level': level,
            'avatar_color': get_avatar_color(username),
            'joined_at': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'user': user_data,
            'socket_url': '/socket.io/'  # Socket.IO endpoint
        })
        
    except Exception as e:
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

@main_bp.route('/api/chat/messages/history')
def get_chat_history():
    """API endpoint to get chat message history"""
    try:
        channel = request.args.get('channel', 'general')
        
        # Get messages from in-memory storage (or database)
        channel_messages = [msg for msg in chat_messages if msg.get('channel') == channel]
        
        return jsonify({
            'success': True,
            'messages': channel_messages[-100:],  # Last 100 messages
            'channel': channel
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving chat history: {str(e)}'
        }), 500

# Utility functions
def get_avatar_color(username):
    """Generate consistent avatar color based on username"""
    colors = ['primary-blue', 'green-500', 'purple-500', 'yellow-500', 'red-500', 'pink-500', 'indigo-500']
    hash_value = sum(ord(char) for char in username)
    return colors[hash_value % len(colors)]

# Socket.IO Event Handlers
def register_socket_handlers():
    """Register all Socket.IO event handlers"""
    
    @socketio.on('connect')
    def handle_connect():
        print(f'Client connected: {flask_request.sid}')
        emit('connected', {'status': 'connected', 'message': 'Welcome to RedCharger Chat!'})

    @socketio.on('disconnect')
    def handle_disconnect():
        print(f'Client disconnected: {flask_request.sid}')
        
        # Remove user from active users
        user_to_remove = None
        for user_id, user_data in active_users.items():
            if user_data.get('socket_id') == flask_request.sid:
                user_to_remove = user_id
                break
        
        if user_to_remove:
            username = active_users[user_to_remove]['username']
            del active_users[user_to_remove]
            
            # Notify all clients
            emit('user_left', {
                'username': username,
                'userCount': len(active_users),
                'onlineUsers': list(active_users.values())
            }, broadcast=True)

    @socketio.on('join_chat')
    def handle_join_chat(data):
        """Handle user joining the chat"""
        try:
            user_data = data['user']
            user_data['socket_id'] = flask_request.sid
            
            # Add to active users
            active_users[user_data['id']] = user_data
            
            # Join the general room
            join_room('general')
            
            # Send chat history
            general_messages = [msg for msg in chat_messages if msg.get('channel') == 'general']
            emit('chat_history', {
                'channel': 'general',
                'messages': general_messages[-50:]  # Last 50 messages
            })
            
            # Notify all clients
            emit('user_joined', {
                'username': user_data['username'],
                'userCount': len(active_users),
                'onlineUsers': list(active_users.values())
            }, broadcast=True)
            
            print(f"User {user_data['username']} joined the chat. Online: {len(active_users)}")
            
        except Exception as e:
            print(f"Error in join_chat: {e}")
            emit('error', {'message': 'Failed to join chat'})

    @socketio.on('send_message')
    def handle_send_message(data):
        """Handle sending a new message"""
        try:
            message_data = {
                'id': str(uuid.uuid4()),
                'sender': data['sender'],
                'sender_id': data['sender_id'],
                'text': data['text'],
                'timestamp': datetime.utcnow().isoformat(),
                'channel': data.get('channel', 'general'),
                'type': 'received'
            }
            
            # Store message
            chat_messages.append(message_data)
            
            # Keep only last 200 messages to prevent memory issues
            if len(chat_messages) > 200:
                chat_messages.pop(0)
            
            # Broadcast to room
            emit('new_message', message_data, room='general')
            
            # Send delivery confirmation to sender
            emit('message_sent', {
                'messageId': message_data['id'],
                'timestamp': message_data['timestamp']
            })
            
            print(f"Message from {data['sender']}: {data['text']}")
            
        except Exception as e:
            print(f"Error in send_message: {e}")
            emit('error', {'message': 'Failed to send message'})

    @socketio.on('typing_start')
    def handle_typing_start(data):
        """Handle typing indicator start"""
        try:
            user_data = data['user']
            typing_users[user_data['id']] = {
                'user': user_data,
                'timestamp': datetime.utcnow()
            }
            
            emit('user_typing', {
                'user': user_data,
                'typingUsers': list(typing_users.values())
            }, broadcast=True, include_self=False)
            
        except Exception as e:
            print(f"Error in typing_start: {e}")

    @socketio.on('typing_stop')
    def handle_typing_stop(data):
        """Handle typing indicator stop"""
        try:
            user_data = data['user']
            if user_data['id'] in typing_users:
                del typing_users[user_data['id']]
            
            emit('user_stop_typing', {
                'user': user_data,
                'typingUsers': list(typing_users.values())
            }, broadcast=True, include_self=False)
            
        except Exception as e:
            print(f"Error in typing_stop: {e}")

    @socketio.on('join_channel')
    def handle_join_channel(data):
        """Handle joining a specific channel"""
        try:
            channel = data['channel']
            user = data['user']
            
            join_room(channel)
            
            # Send channel-specific history
            channel_messages = [msg for msg in chat_messages if msg.get('channel') == channel]
            emit('channel_history', {
                'channel': channel,
                'messages': channel_messages[-50:]
            })
            
            print(f"User {user['username']} joined channel {channel}")
            
        except Exception as e:
            print(f"Error in join_channel: {e}")

    @socketio.on('leave_channel')
    def handle_leave_channel(data):
        """Handle leaving a specific channel"""
        try:
            channel = data['channel']
            user = data['user']
            
            leave_room(channel)
            print(f"User {user['username']} left channel {channel}")
            
        except Exception as e:
            print(f"Error in leave_channel: {e}")

    @socketio.on('get_online_users')
    def handle_get_online_users():
        """Send current online users to requesting client"""
        emit('online_users', {
            'users': list(active_users.values()),
            'count': len(active_users)
        })

# Initialize Socket.IO with the app
def init_socketio(app):
    """Initialize Socket.IO with the Flask app"""
    socketio.init_app(app, cors_allowed_origins="*")
    register_socket_handlers()