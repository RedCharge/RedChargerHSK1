from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import uuid
from flask_socketio import SocketIO

db = SQLAlchemy()
socketio = SocketIO()

class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_type = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    incorrect_answers = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    time_taken = db.Column(db.Integer, default=0)
    user_answers = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_user_answers(self):
        if self.user_answers:
            return json.loads(self.user_answers)
        return []
    
    def set_user_answers(self, answers_list):
        self.user_answers = json.dumps(answers_list)

class ChatUser(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    level = db.Column(db.String(20), default='HSK1')
    avatar_color = db.Column(db.String(20), default='primary-blue')
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatMessage(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    channel = db.Column(db.String(50), nullable=False)
    sender_id = db.Column(db.String(36), db.ForeignKey('chat_user.id'), nullable=False)
    sender_username = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    pinyin = db.Column(db.String(500))
    message_type = db.Column(db.String(20), default='text')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    sender = db.relationship('ChatUser', backref=db.backref('messages', lazy=True))

class ChatChannel(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    icon = db.Column(db.String(50))
    color = db.Column(db.String(20))
    member_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# REMOVE ALL SOCKETIO EVENT HANDLERS FROM THIS FILE
# They should be in main_routes.py only