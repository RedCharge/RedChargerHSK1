from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session, current_app, make_response
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
import requests
import json
import uuid
import re
import random
import hashlib
import secrets
from sqlalchemy import or_, and_

# Import db from models
from app.models import db

auth_bp = Blueprint('auth', __name__)

# ==================== HELPER FUNCTIONS ====================

def verify_firebase_token(id_token):
    """Verify Firebase ID token"""
    try:
        firebase_api_key = current_app.config.get('FIREBASE_API_KEY')
        if not firebase_api_key:
            current_app.logger.warning("⚠️ FIREBASE_API_KEY not configured")
            return None
            
        firebase_verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={firebase_api_key}"
        
        response = requests.post(firebase_verify_url, json={'idToken': id_token}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('users'):
                return data['users'][0]
        current_app.logger.error(f"❌ Firebase verification failed: {response.status_code} - {response.text}")
        return None
            
    except requests.exceptions.Timeout:
        current_app.logger.error("🔥 Firebase verification timeout")
        return None
    except Exception as e:
        current_app.logger.error(f"🔥 Firebase verification error: {str(e)}")
        return None

def is_code_already_used(code):
    """Check if verification code has already been used"""
    try:
        from app.models import UsedVerificationCode
        return db.session.query(UsedVerificationCode).filter_by(code=code).first() is not None
    except Exception as e:
        current_app.logger.error(f"Database error checking code: {str(e)}")
        return False

def mark_code_as_used(code, user_auth_id):
    """Mark a verification code as used"""
    try:
        from app.models import UsedVerificationCode
        used_code = UsedVerificationCode(
            code=code,
            user_auth_id=user_auth_id
        )
        db.session.add(used_code)
        return True
    except Exception as e:
        current_app.logger.error(f"Error marking code as used: {str(e)}")
        return False

def random_avatar_color():
    """Generate a random avatar color"""
    colors = ['primary-blue', 'green', 'purple', 'orange', 'red', 'teal', 'pink', 'yellow']
    return random.choice(colors)

def ensure_user_record(user_auth, name=None):
    """Ensure a User record exists for UserAuth"""
    from app.models import User
    
    if user_auth.user_id and user_auth.user:
        return user_auth.user
    
    email = user_auth.email
    username = ""
    
    if name and name.strip():
        username = name.strip()
    elif email:
        username = email.split('@')[0]
    else:
        username = f"user_{uuid.uuid4().hex[:8]}"
    
    username = re.sub(r'[^a-zA-Z0-9_]', '', username)[:45]
    if not username:
        username = f"user_{uuid.uuid4().hex[:8]}"
    
    base_username = username
    counter = 1
    while db.session.query(User).filter_by(username=username).first():
        username = f"{base_username}_{counter}"
        counter += 1
        if counter > 100:
            username = f"user_{uuid.uuid4().hex[:12]}"
            break
    
    user = User(
        id=str(uuid.uuid4()),
        username=username,
        email=email,
        avatar_color=random_avatar_color()
    )
    
    user_auth.user_id = user.id
    db.session.add(user)
    current_app.logger.info(f"✅ Created User record: {username} (ID: {user.id})")
    return user

def create_or_update_user(firebase_user, name=None):
    """Create or update user from Firebase data"""
    from app.models import UserAuth
    
    firebase_uid = firebase_user['localId']
    email = firebase_user.get('email', '')
    
    user_auth = db.session.query(UserAuth).filter_by(firebase_uid=firebase_uid).first()
    
    if not user_auth and email:
        user_auth = db.session.query(UserAuth).filter_by(email=email).first()
    
    if not user_auth:
        user_auth = UserAuth(
            email=email,
            firebase_uid=firebase_uid,
            account_type='regular',
            is_premium=False
        )
        db.session.add(user_auth)
        current_app.logger.info(f"✅ Created new UserAuth: {email or firebase_uid[:8]}")
    else:
        if email and user_auth.email != email:
            user_auth.email = email
        if not user_auth.firebase_uid:
            user_auth.firebase_uid = firebase_uid
        current_app.logger.info(f"✅ Updated UserAuth: {email or firebase_uid[:8]}")
    
    user_auth.last_login = datetime.utcnow()
    user = ensure_user_record(user_auth, name)
    
    return user_auth, user

# ==================== SESSION MANAGEMENT (FROM YOUR OTHER APP) ====================

def generate_session_token():
    """Generate a unique session token"""
    return secrets.token_urlsafe(32)

def get_device_fingerprint(request):
    """Create a unique device fingerprint"""
    user_agent = request.headers.get('User-Agent', '')
    ip_address = request.remote_addr or '127.0.0.1'
    
    # Create a hash from user agent and IP
    fingerprint_str = f"{user_agent}:{ip_address}"
    return hashlib.sha256(fingerprint_str.encode()).hexdigest()

def create_user_session(user_auth, request):
    """Create a new session for user using database - WITH SESSION TOKEN"""
    from app.models import UserSession, generate_session_token as gen_token, get_device_fingerprint as get_fingerprint
    
    # Generate session token
    session_token = generate_session_token()
    device_fingerprint = get_device_fingerprint(request)
    
    # 🔥 CRITICAL: Invalidate all existing sessions FIRST (single device per user)
    active_sessions = db.session.query(UserSession).filter_by(
        user_auth_id=user_auth.id,
        is_active=True
    ).all()
    
    for old_session in active_sessions:
        old_session.is_active = False
        old_session.logout_time = datetime.utcnow()
        current_app.logger.info(f"🔒 Invalidated old session: {old_session.session_token[:8]}")
    
    # Create new session
    user_session = UserSession(
        user_auth_id=user_auth.id,
        session_token=session_token,
        device_fingerprint=device_fingerprint,
        ip_address=request.remote_addr or '127.0.0.1',
        user_agent=request.headers.get('User-Agent', ''),
        login_time=datetime.utcnow(),
        is_active=True
    )
    
    db.session.add(user_session)
    
    # Store in Flask session
    session['user'] = {
        'uid': str(user_auth.id),
        'email': user_auth.email,
        'username': user_auth.user.username if user_auth.user else '',
        'session_id': session_token,
        'device_fingerprint': device_fingerprint,
        'login_time': datetime.utcnow().isoformat(),
        'is_premium': user_auth.is_premium
    }
    
    session['session_token'] = session_token
    session['user_auth_id'] = user_auth.id
    
    return session_token

def validate_session():
    """Validate if the current session is still active - FROM YOUR OTHER APP"""
    from app.models import UserSession
    
    user_session_data = session.get('user')
    if not user_session_data:
        return False, "No active session"
    
    session_token = user_session_data.get('session_id')
    user_auth_id = user_session_data.get('uid')
    
    if not session_token or not user_auth_id:
        return False, "Invalid session data"
    
    # Check session in database
    user_session = UserSession.query.filter_by(
        session_token=session_token,
        user_auth_id=user_auth_id,
        is_active=True
    ).first()
    
    if not user_session:
        return False, "Session not found or inactive"
    
    # Check session expiration (24 hours)
    if user_session.login_time < datetime.utcnow() - timedelta(hours=24):
        # Mark as expired
        user_session.is_active = False
        user_session.logout_time = datetime.utcnow()
        db.session.commit()
        return False, "Session expired"
    
    return True, "Session valid"

# ==================== ROUTES ====================

@auth_bp.route('/')
def index():
    """Main entry point"""
    return redirect('/login')

@auth_bp.route('/login', methods=['GET'])
def login_page():
    """Serve the login page"""
    if current_user.is_authenticated:
        # Check if session is still valid
        is_valid, message = validate_session()
        if is_valid:
            return redirect('/home')
        else:
            # Session invalid, logout
            logout_user_internal()
            flash('Your session has expired. Please login again.', 'info')
    
    return render_template('login.html')

@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for Firebase login"""
    try:
        data = request.get_json()
        id_token = data.get('id_token')
        name = data.get('name', '')
        
        if not id_token:
            return jsonify({'success': False, 'error': 'No ID token provided'}), 400
        
        firebase_user = verify_firebase_token(id_token)
        if not firebase_user:
            return jsonify({'success': False, 'error': 'Invalid Firebase token'}), 401
        
        # CHECK: Email must be verified before login
        if not firebase_user.get('emailVerified', False):
            return jsonify({
                'success': False, 
                'error': 'Please verify your email address before logging in.',
                'requires_verification': True,
                'email': firebase_user.get('email', '')
            }), 403
        
        try:
            user_auth, user = create_or_update_user(firebase_user, name)
            
            # Check if user has used a verification code
            from app.models import UsedVerificationCode
            used_code = UsedVerificationCode.query.filter_by(user_auth_id=user_auth.id).first()
            
            if used_code:
                user_auth.account_type = 'premium'
                user_auth.is_premium = True
                current_app.logger.info(f"✅ Upgraded user to premium: {user.username}")
            
            # Create session with token (invalidates old sessions)
            session_token = create_user_session(user_auth, request)
            
            db.session.commit()
            login_user(user, remember=True)
            
            current_app.logger.info(f"✅ Login successful: {user.username}")
            
            return jsonify({
                'success': True,
                'message': 'Login successful!',
                'redirect': '/home',
                'user': {
                    'username': user.username,
                    'email': user_auth.email,
                    'is_premium': user_auth.is_premium,
                    'avatar_color': user.avatar_color,
                    'session_id': session_token
                }
            })
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"❌ Database error during login: {str(e)}")
            return jsonify({'success': False, 'error': 'Database error during login'}), 500
        
    except Exception as e:
        current_app.logger.error(f"❌ Login error: {str(e)}")
        return jsonify({'success': False, 'error': 'Login failed. Please try again.'}), 500

@auth_bp.route('/signup', methods=['GET'])
def signup_page():
    """Serve the signup page"""
    return render_template('signup.html')

@auth_bp.route('/api/signup', methods=['POST'])
def api_signup():
    """API endpoint for Firebase signup"""
    try:
        data = request.get_json()
        id_token = data.get('id_token')
        name = data.get('name', '').strip()
        verification_code = data.get('verification_code', '').strip().upper()
        
        current_app.logger.info(f"🚀 Signup attempt: name={name}, code={verification_code}")
        
        if not id_token:
            return jsonify({'success': False, 'error': 'No ID token provided'}), 400
        
        if not verification_code:
            return jsonify({'success': False, 'error': 'Verification code is required'}), 400
        
        firebase_user = verify_firebase_token(id_token)
        if not firebase_user:
            return jsonify({'success': False, 'error': 'Invalid Firebase token'}), 401
        
        if not re.match(r'^RC-[A-Z0-9]{4}-[A-Z0-9]{4}$', verification_code):
            return jsonify({
                'success': False, 
                'error': 'Invalid code format. Use: RC-XXXX-XXXX'
            }), 400
        
        valid_codes = current_app.config.get('VERIFICATION_CODES', [])
        
        if verification_code not in valid_codes:
            return jsonify({
                'success': False, 
                'error': 'Invalid verification code.'
            }), 400
        
        if is_code_already_used(verification_code):
            return jsonify({
                'success': False, 
                'error': 'This code has already been used.'
            }), 400
        
        firebase_uid = firebase_user['localId']
        email = firebase_user.get('email', '')
        
        from app.models import UserAuth
        existing_user = db.session.query(UserAuth).filter(
            or_(
                UserAuth.firebase_uid == firebase_uid,
                UserAuth.email == email
            )
        ).first()
        
        if existing_user:
            return jsonify({'success': False, 'error': 'User already exists. Please login.'}), 400
        
        try:
            db.session.begin_nested()
            
            user_auth = UserAuth(
                email=email,
                firebase_uid=firebase_uid,
                account_type='premium',
                is_premium=True
            )
            db.session.add(user_auth)
            db.session.flush()
            
            if not mark_code_as_used(verification_code, user_auth.id):
                db.session.rollback()
                return jsonify({'success': False, 'error': 'Failed to mark code as used'}), 500
            
            user = ensure_user_record(user_auth, name)
            db.session.flush()
            
            db.session.commit()
            
            current_app.logger.info(f"🎉 SIGNUP SUCCESS (PENDING EMAIL VERIFICATION): {user.username} ({email})")
            
            return jsonify({
                'success': True,
                'message': 'Registration successful! Please check your email to verify your account.',
                'redirect': '/login',
                'requires_verification': True,
                'email': email,
                'user': {
                    'username': user.username,
                    'email': email,
                    'is_premium': True,
                    'avatar_color': user.avatar_color
                }
            })
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"❌ Transaction error during signup: {str(e)}")
            return jsonify({'success': False, 'error': 'Registration failed due to database error.'}), 500
        
    except Exception as e:
        current_app.logger.error(f"❌ Signup error: {str(e)}")
        return jsonify({'success': False, 'error': 'Registration failed. Please try again.'}), 500

def logout_user_internal(session_token=None, user_auth_id=None):
    """Internal logout function"""
    from app.models import UserSession
    
    # Clear session from database
    try:
        if user_auth_id:
            # Clear ALL sessions for this user
            user_sessions = UserSession.query.filter_by(
                user_auth_id=user_auth_id,
                is_active=True
            ).all()
            
            for user_session in user_sessions:
                user_session.is_active = False
                user_session.logout_time = datetime.utcnow()
                current_app.logger.info(f"🔒 Logged out session: {user_session.session_token[:8]}")
        
        elif session_token and user_auth_id:
            # Clear specific session
            user_session = UserSession.query.filter_by(
                session_token=session_token,
                user_auth_id=user_auth_id
            ).first()
            
            if user_session:
                user_session.is_active = False
                user_session.logout_time = datetime.utcnow()
                current_app.logger.info(f"🔒 Logged out session: {session_token[:8]}")
    
    except Exception as e:
        current_app.logger.error(f"❌ Error clearing sessions: {str(e)}")
    
    # Clear Flask session
    session.clear()
    logout_user()
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"❌ Database commit error during logout: {str(e)}")

@auth_bp.route('/logout')
def logout():
    """Logout user - CLEARS EVERYTHING"""
    user_session_data = session.get('user')
    session_token = user_session_data.get('session_id') if user_session_data else None
    user_auth_id = user_session_data.get('uid') if user_session_data else None
    
    # Logout from database and Flask
    logout_user_internal(session_token, user_auth_id)
    
    # Clear cookies
    resp = make_response(redirect('/login'))
    resp.delete_cookie('session', path='/')
    
    flash('Logged out successfully.', 'info')
    return resp

@auth_bp.route('/api/logout', methods=['POST'])
def api_logout():
    """API endpoint for logout"""
    user_session_data = session.get('user')
    session_token = user_session_data.get('session_id') if user_session_data else None
    user_auth_id = user_session_data.get('uid') if user_session_data else None
    
    logout_user_internal(session_token, user_auth_id)
    
    return jsonify({
        'success': True,
        'message': 'Logged out successfully.',
        'redirect': '/login'
    })

@auth_bp.route('/check-session')
@login_required
def check_session():
    """Check if current session is valid"""
    is_valid, message = validate_session()
    
    if is_valid:
        return jsonify({'valid': True})
    
    logout_user_internal()
    return jsonify({'valid': False, 'message': message}), 401

# ==================== MIDDLEWARE (FROM YOUR OTHER APP) ====================

@auth_bp.before_app_request
def check_session_globally():
    """Check session validity for all routes - FROM YOUR OTHER APP"""
    # Skip session check for these endpoints
    excluded_endpoints = [
        'auth.login_page',
        'auth.signup_page', 
        'auth.api_login',
        'auth.api_signup',
        'auth.api_logout',
        'auth.logout',
        'auth.index',
        'auth.firebase_config',
        'auth.health_check',
        'static'
    ]
    
    # Get the endpoint name
    endpoint = request.endpoint
    
    # Skip if endpoint is in excluded list or doesn't exist
    if not endpoint or endpoint in excluded_endpoints:
        return
    
    # Skip API endpoints
    if '/api/' in request.path:
        return
    
    # Use Flask-Login's current_user for authentication check
    if not current_user.is_authenticated:
        if endpoint != 'auth.login_page':
            flash("Please log in to continue", "warning")
            return redirect('/login')
        return
    
    # Validate the session against database
    is_valid, message = validate_session()
    
    if not is_valid:
        logout_user_internal()
        session.clear()
        
        if "another login" in message.lower():
            flash("You have been logged out because you logged in from another device", "warning")
        else:
            flash("Your session has expired. Please log in again.", "info")
        
        return redirect('/login')

# ==================== UTILITY ROUTES ====================

@auth_bp.route('/api/firebase-config')
def firebase_config():
    """Serve Firebase config to frontend"""
    config = {
        'apiKey': current_app.config.get('FIREBASE_API_KEY'),
        'authDomain': current_app.config.get('FIREBASE_AUTH_DOMAIN'),
        'projectId': current_app.config.get('FIREBASE_PROJECT_ID'),
        'storageBucket': current_app.config.get('FIREBASE_STORAGE_BUCKET'),
        'messagingSenderId': current_app.config.get('FIREBASE_MESSAGING_SENDER_ID'),
        'appId': current_app.config.get('FIREBASE_APP_ID'),
        'measurementId': current_app.config.get('FIREBASE_MEASUREMENT_ID')
    }
    return jsonify(config)

@auth_bp.route('/api/health')
def health_check():
    """Health check endpoint"""
    from app.models import UserSession, User, UserAuth
    
    try:
        db.session.execute('SELECT 1')
        db_status = 'ok'
        
        session_count = UserSession.query.filter_by(is_active=True).count()
        user_count = User.query.count()
        user_auth_count = UserAuth.query.count()
        
    except Exception as e:
        db_status = 'error'
        session_count = 0
        user_count = 0
        user_auth_count = 0
        current_app.logger.error(f"Health check error: {str(e)}")
    
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'auth',
        'database': db_status,
        'session_count': session_count,
        'user_count': user_count,
        'user_auth_count': user_auth_count
    })