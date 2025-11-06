from flask import Blueprint, request, jsonify, session, render_template
import time
from datetime import datetime
import uuid
from typing import Dict, List, Set
import threading
from collections import defaultdict

# Create Blueprint for chat routes
chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# In-memory storage (in production, use Redis or database)
chat_messages: List[Dict] = []
online_users: Dict[str, Dict] = {}  # {user_id: {username, avatar, last_seen}}
typing_users: Set[str] = set()

# Cleanup thread for removing inactive users
def cleanup_inactive_users():
    while True:
        time.sleep(60)  # Check every minute
        current_time = time.time()
        inactive_users = []
        
        for user_id, user_data in online_users.items():
            if current_time - user_data.get('last_seen', 0) > 300:  # 5 minutes inactivity
                inactive_users.append(user_id)
        
        for user_id in inactive_users:
            if user_id in online_users:
                del online_users[user_id]
            if user_id in typing_users:
                typing_users.remove(user_id)

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_inactive_users, daemon=True)
cleanup_thread.start()

# Chat page route
@chat_bp.route('/chat')
def chat_page():
    """Serve the chat.html page"""
    return render_template('chat.html')

@chat_bp.before_request
def check_user_profile():
    """Check if user has completed their profile before accessing chat"""
    if request.endpoint and 'chat.' in request.endpoint:
        # Skip for specific endpoints that don't require profile
        if request.endpoint in ['chat.health', 'chat.get_messages', 'chat.chat_page']:
            return
            
        # Check if user has profile data in session or request
        user_data = session.get('user_profile') or request.json.get('user_profile') if request.json else None
        
        if not user_data or not user_data.get('username'):
            return jsonify({
                'error': 'Profile incomplete',
                'message': 'Please complete your profile before using chat',
                'redirect': '/profile'
            }), 403

@chat_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'online_users': len(online_users),
        'total_messages': len(chat_messages)
    })

@chat_bp.route('/messages', methods=['GET'])
def get_messages():
    """Get all chat messages with pagination"""
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        # Filter out deleted messages
        visible_messages = [msg for msg in chat_messages if not msg.get('is_deleted', False)]
        
        # Apply pagination
        paginated_messages = visible_messages[offset:offset + limit]
        
        return jsonify({
            'messages': paginated_messages,
            'total': len(visible_messages),
            'has_more': offset + limit < len(visible_messages)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/send', methods=['POST'])
def send_message():
    """Send a new message to the chat"""
    try:
        data = request.json
        user_profile = session.get('user_profile') or data.get('user_profile')
        
        if not user_profile or not user_profile.get('username'):
            return jsonify({
                'error': 'Authentication required',
                'message': 'User profile not found'
            }), 401
        
        message_text = data.get('text', '').strip()
        reply_to_id = data.get('reply_to')
        
        if not message_text:
            return jsonify({'error': 'Message text is required'}), 400
        
        # Validate message length
        if len(message_text) > 1000:
            return jsonify({'error': 'Message too long (max 1000 characters)'}), 400
        
        # Create message object
        message_id = str(uuid.uuid4())
        new_message = {
            'id': message_id,
            'user_id': user_profile['username'],  # Using username as user_id for simplicity
            'username': user_profile['username'],
            'avatar': user_profile.get('avatar', ''),
            'text': message_text,
            'timestamp': datetime.utcnow().isoformat(),
            'reply_to': None
        }
        
        # Add reply data if replying to another message
        if reply_to_id:
            replied_message = next((msg for msg in chat_messages if msg['id'] == reply_to_id), None)
            if replied_message:
                new_message['reply_to'] = {
                    'id': replied_message['id'],
                    'username': replied_message['username'],
                    'text': replied_message['text'][:100] + ('...' if len(replied_message['text']) > 100 else '')
                }
        
        # Add message to storage
        chat_messages.append(new_message)
        
        # Limit messages history (keep last 1000 messages)
        if len(chat_messages) > 1000:
            chat_messages.pop(0)
        
        # Update user's last activity
        if user_profile['username'] in online_users:
            online_users[user_profile['username']]['last_seen'] = time.time()
        
        # Remove user from typing set
        if user_profile['username'] in typing_users:
            typing_users.remove(user_profile['username'])
        
        return jsonify({
            'success': True,
            'message': new_message
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/delete/<message_id>', methods=['DELETE'])
def delete_message(message_id):
    """Delete a message (only allowed for message owner)"""
    try:
        user_profile = session.get('user_profile') or request.json.get('user_profile') if request.json else None
        
        if not user_profile or not user_profile.get('username'):
            return jsonify({'error': 'Authentication required'}), 401
        
        # Find the message
        message_index = next((i for i, msg in enumerate(chat_messages) if msg['id'] == message_id), None)
        
        if message_index is None:
            return jsonify({'error': 'Message not found'}), 404
        
        message = chat_messages[message_index]
        
        # Check if user owns the message
        if message['user_id'] != user_profile['username']:
            return jsonify({'error': 'You can only delete your own messages'}), 403
        
        # Mark message as deleted (soft delete)
        chat_messages[message_index]['is_deleted'] = True
        chat_messages[message_index]['deleted_at'] = datetime.utcnow().isoformat()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/typing', methods=['POST'])
def update_typing_status():
    """Update user's typing status"""
    try:
        data = request.json
        user_profile = session.get('user_profile') or data.get('user_profile')
        
        if not user_profile or not user_profile.get('username'):
            return jsonify({'error': 'Authentication required'}), 401
        
        is_typing = data.get('is_typing', False)
        username = user_profile['username']
        
        if is_typing:
            typing_users.add(username)
        else:
            typing_users.discard(username)
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/online', methods=['POST'])
def update_online_status():
    """Update user's online status"""
    try:
        data = request.json
        user_profile = session.get('user_profile') or data.get('user_profile')
        
        if not user_profile or not user_profile.get('username'):
            return jsonify({'error': 'Authentication required'}), 401
        
        username = user_profile['username']
        is_online = data.get('is_online', True)
        
        if is_online:
            online_users[username] = {
                'username': username,
                'avatar': user_profile.get('avatar', ''),
                'last_seen': time.time()
            }
        else:
            online_users.pop(username, None)
            typing_users.discard(username)
        
        return jsonify({
            'success': True,
            'online_users': list(online_users.keys())
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/poll', methods=['GET'])
def poll_messages():
    """Long polling endpoint for real-time updates"""
    try:
        timeout = 30  # seconds
        start_time = time.time()
        last_message_id = request.args.get('last_message_id', '')
        
        # Find the index of the last message the client has
        if last_message_id:
            last_index = next((i for i, msg in enumerate(chat_messages) if msg['id'] == last_message_id), -1)
        else:
            last_index = -1
        
        # Wait for new messages or timeout
        while time.time() - start_time < timeout:
            # Check if there are new messages
            if len(chat_messages) > last_index + 1:
                new_messages = chat_messages[last_index + 1:]
                return jsonify({
                    'new_messages': new_messages,
                    'typing_users': list(typing_users),
                    'online_users': list(online_users.keys())
                })
            
            time.sleep(0.5)  # Sleep to prevent busy waiting
        
        # Timeout - return empty response
        return jsonify({
            'new_messages': [],
            'typing_users': list(typing_users),
            'online_users': list(online_users.keys())
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/search', methods=['GET'])
def search_messages():
    """Search messages by text"""
    try:
        query = request.args.get('q', '').strip().lower()
        
        if not query or len(query) < 2:
            return jsonify({'error': 'Search query must be at least 2 characters'}), 400
        
        # Search in non-deleted messages
        results = [
            msg for msg in chat_messages 
            if not msg.get('is_deleted', False) and query in msg['text'].lower()
        ]
        
        return jsonify({
            'results': results,
            'count': len(results),
            'query': query
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/users/online', methods=['GET'])
def get_online_users():
    """Get list of currently online users"""
    try:
        # Clean up inactive users before returning list
        current_time = time.time()
        inactive_users = [
            username for username, data in online_users.items()
            if current_time - data.get('last_seen', 0) > 300  # 5 minutes
        ]
        
        for username in inactive_users:
            online_users.pop(username, None)
            typing_users.discard(username)
        
        return jsonify({
            'online_users': list(online_users.keys()),
            'count': len(online_users)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error handlers
@chat_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@chat_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Utility function to get chat statistics (for admin purposes)
@chat_bp.route('/stats', methods=['GET'])
def get_chat_stats():
    """Get chat statistics (admin only)"""
    try:
        total_messages = len(chat_messages)
        active_messages = len([msg for msg in chat_messages if not msg.get('is_deleted', False)])
        deleted_messages = total_messages - active_messages
        
        # Calculate messages per user
        user_message_count = defaultdict(int)
        for msg in chat_messages:
            if not msg.get('is_deleted', False):
                user_message_count[msg['user_id']] += 1
        
        top_users = dict(sorted(user_message_count.items(), key=lambda x: x[1], reverse=True)[:5])
        
        return jsonify({
            'total_messages': total_messages,
            'active_messages': active_messages,
            'deleted_messages': deleted_messages,
            'online_users_count': len(online_users),
            'top_users': top_users,
            'typing_users_count': len(typing_users)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500