from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import uuid
import secrets
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# Initialize SQLAlchemy
db = SQLAlchemy()

# Helper functions (moved to top to avoid circular imports)
def generate_session_token():
    """Generate a unique session token"""
    return secrets.token_hex(32)

def get_device_fingerprint(request):
    """Generate a fingerprint for the current device"""
    user_agent = request.headers.get('User-Agent', '')
    accept = request.headers.get('Accept', '')
    accept_language = request.headers.get('Accept-Language', '')
    accept_encoding = request.headers.get('Accept-Encoding', '')
    
    fingerprint_string = f"{user_agent}{accept}{accept_language}{accept_encoding}"
    return hashlib.sha256(fingerprint_string.encode()).hexdigest()

class UserAuth(db.Model):
    """Authentication user model"""
    __tablename__ = 'user_auth'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(256))
    firebase_uid = db.Column(db.String(128), unique=True, nullable=True, index=True)
    account_type = db.Column(db.String(20), default='regular')  # regular, premium
    is_premium = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    last_logout = db.Column(db.DateTime)
    
    # Link to your existing User model
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), unique=True, nullable=True, index=True)
    
    # Relationships
    sessions = db.relationship('UserSession', backref='user_auth', lazy=True, cascade='all, delete-orphan')
    used_codes = db.relationship('UsedVerificationCode', backref='user_auth', lazy=True)
    
    __table_args__ = (
        db.Index('idx_user_auth_email', 'email'),
        db.Index('idx_user_auth_firebase', 'firebase_uid'),
        db.Index('idx_user_auth_user_id', 'user_id'),
        db.Index('idx_user_auth_premium', 'is_premium'),
    )
    
    def set_password(self, password):
        """Set password hash for the user"""
        if password:
            self.password_hash = generate_password_hash(password)
        else:
            raise ValueError("Password cannot be empty")
    
    def check_password(self, password):
        """Check if password matches the hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def get_active_session_count(self):
        """Get number of active sessions for this user"""
        from app.models import UserSession
        return UserSession.query.filter_by(
            user_auth_id=self.id,
            is_active=True
        ).count()
    
    def get_active_sessions(self):
        """Get all active sessions for this user"""
        from app.models import UserSession
        return UserSession.query.filter_by(
            user_auth_id=self.id,
            is_active=True
        ).order_by(UserSession.login_time.desc()).all()
    
    def revoke_all_sessions(self, exclude_token=None):
        """Revoke all active sessions except the specified one"""
        from app.models import UserSession
        sessions = UserSession.query.filter_by(
            user_auth_id=self.id,
            is_active=True
        ).all()
        
        for session in sessions:
            if exclude_token and session.session_token == exclude_token:
                continue
            session.is_active = False
            session.logout_time = datetime.utcnow()
        
        db.session.commit()
        return len(sessions)
    
    def can_login(self):
        """Check if user can login"""
        return self.is_active
    
    def __repr__(self):
        return f'<UserAuth {self.email or self.firebase_uid[:8]}>'

class UserSession(db.Model):
    """User session management"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_auth_id = db.Column(db.String(36), db.ForeignKey('user_auth.id'), nullable=False, index=True)
    session_token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    device_fingerprint = db.Column(db.String(64), nullable=False, index=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    login_time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    logout_time = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    __table_args__ = (
        db.Index('idx_session_token_active', 'session_token', 'is_active'),
        db.Index('idx_user_auth_active', 'user_auth_id', 'is_active'),
        db.Index('idx_login_time', 'login_time'),
    )
    
    def to_dict(self):
        """Convert session to dictionary"""
        return {
            'id': self.id,
            'session_token': self.session_token[:8] + '...',
            'device_fingerprint': self.device_fingerprint[:8] + '...',
            'ip_address': self.ip_address,
            'user_agent': self.user_agent[:50] + '...' if self.user_agent and len(self.user_agent) > 50 else self.user_agent,
            'login_time': self.login_time.strftime('%Y-%m-%d %H:%M') if self.login_time else None,
            'logout_time': self.logout_time.strftime('%Y-%m-%d %H:%M') if self.logout_time else None,
            'is_active': self.is_active
        }
    
    def revoke(self):
        """Revoke this session"""
        self.is_active = False
        self.logout_time = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<UserSession {self.session_token[:8]}...>'

class UsedVerificationCode(db.Model):
    """Track used verification codes to prevent reuse"""
    __tablename__ = 'used_verification_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    user_auth_id = db.Column(db.String(36), db.ForeignKey('user_auth.id'), nullable=False, index=True)
    used_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        db.Index('idx_code_used_at', 'code', 'used_at'),
    )
    
    def __repr__(self):
        return f'<UsedVerificationCode {self.code} by {self.user_auth_id}>'

class QuizResult(db.Model):
    __tablename__ = 'quiz_results'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_type = db.Column(db.String(20), nullable=False, index=True)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    incorrect_answers = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    time_taken = db.Column(db.Integer, default=0)
    user_answers = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Link to user
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=True, index=True)
    
    __table_args__ = (
        db.Index('idx_quiz_user_timestamp', 'user_id', 'quiz_type', 'timestamp'),
        db.Index('idx_quiz_timestamp', 'quiz_type', 'timestamp'),
    )
    
    def get_user_answers(self):
        if self.user_answers:
            return json.loads(self.user_answers)
        return []
    
    def set_user_answers(self, answers_list):
        self.user_answers = json.dumps(answers_list)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    level = db.Column(db.String(20), default='HSK1')
    avatar_color = db.Column(db.String(20), default='primary-blue')
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Leaderboard fields
    total_score = db.Column(db.Integer, default=0, index=True)
    words_mastered = db.Column(db.Integer, default=0)
    sentences_mastered = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0, index=True)
    accuracy_rate = db.Column(db.Float, default=0.0)
    last_activity_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    quiz_results = db.relationship('QuizResult', backref='user', lazy=True)
    achievements = db.relationship('UserAchievement', backref='user', lazy=True)
    auth = db.relationship('UserAuth', backref='user', uselist=False, lazy=True)
    messages = db.relationship('ChatMessage', backref='user', lazy=True)
    
    __table_args__ = (
        db.Index('idx_user_total_score', 'total_score'),
        db.Index('idx_user_current_streak', 'current_streak'),
        db.Index('idx_user_last_activity', 'last_activity_date'),
        db.Index('idx_user_username', 'username'),
    )
    
    def update_stats(self, quiz_result):
        """Update user stats based on quiz result"""
        from app.models import db
        self.total_score += quiz_result.score
        self.accuracy_rate = ((self.accuracy_rate or 0) + quiz_result.percentage) / 2
        
        if quiz_result.quiz_type == 'words':
            self.words_mastered += quiz_result.correct_answers
        elif quiz_result.quiz_type == 'sentences':
            self.sentences_mastered += quiz_result.correct_answers
        
        # Update streak
        today = datetime.utcnow().date()
        last_activity = self.last_activity_date.date() if self.last_activity_date else None
        
        if last_activity:
            days_diff = (today - last_activity).days
            if days_diff == 1:
                self.current_streak += 1
            elif days_diff > 1:
                self.current_streak = 1
        else:
            self.current_streak = 1
        
        self.last_activity_date = datetime.utcnow()
        db.session.commit()
    
    def get_leaderboard_data(self):
        """Get data for leaderboard display"""
        return {
            'username': self.username,
            'level': self.level,
            'total_score': self.total_score,
            'words_mastered': self.words_mastered,
            'sentences_mastered': self.sentences_mastered,
            'current_streak': self.current_streak,
            'accuracy_rate': round(self.accuracy_rate, 2),
            'avatar_color': self.avatar_color,
            'is_online': self.is_online,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

class UserAchievement(db.Model):
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False, index=True)
    achievement_id = db.Column(db.String(100), nullable=False, index=True)
    achievement_name = db.Column(db.String(100), nullable=False)
    achievement_description = db.Column(db.String(200))
    achievement_icon = db.Column(db.String(50))
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        db.Index('idx_achievement_user', 'user_id', 'achievement_id'),
        db.Index('idx_achievement_unlocked', 'achievement_id', 'unlocked_at'),
    )
    
    def __repr__(self):
        return f'<UserAchievement {self.achievement_id} for {self.user_id}>'

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    channel = db.Column(db.String(50), nullable=False, index=True)
    sender_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False, index=True)
    sender_username = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    pinyin = db.Column(db.String(500))
    message_type = db.Column(db.String(20), default='text')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        db.Index('idx_channel_timestamp', 'channel', 'timestamp'),
        db.Index('idx_sender_timestamp', 'sender_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f'<ChatMessage {self.id[:8]} in {self.channel}>'

class ChatChannel(db.Model):
    __tablename__ = 'chat_channels'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    icon = db.Column(db.String(50))
    color = db.Column(db.String(20))
    member_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ChatChannel {self.name}>'