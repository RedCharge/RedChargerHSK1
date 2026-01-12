from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta  # Added timedelta import
from flask_login import login_required, current_user  # Added this import
import json
import uuid

# Import db and models from your models.py
from .models import db, QuizResult, User

# Create Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/home')
@login_required
def index():
    """Render the main landing page"""
    return render_template('index.html')

@main_bp.route('/result')
@login_required
def result():
    """Render the result page"""
    return render_template('result.html')

@main_bp.route('/exam')
@login_required
def exam():
    """Render the exam page"""
    return render_template('exam.html')



@main_bp.route('/api/quiz-results', methods=['POST'])
@login_required
def save_quiz_result():
    """API endpoint to save quiz results to database"""
    try:
        data = request.get_json()
        user_id = current_user.id  # Changed from session to current_user
        
        print(f"💾 Saving quiz result for user_id: {user_id}")
        
        # Create new quiz result
        quiz_result = QuizResult(
            quiz_type=data.get('quiz_type', 'words'),
            score=data.get('score', 0),
            total_questions=data.get('total_questions', 0),
            correct_answers=data.get('correct_answers', 0),
            incorrect_answers=data.get('incorrect_answers', 0),
            percentage=data.get('percentage', 0),
            time_taken=data.get('time_taken', 0),
            timestamp=datetime.utcnow(),
            user_id=user_id  # Associate with user
        )
        
        # Set user answers using the model method
        quiz_result.set_user_answers(data.get('user_answers', []))
        
        db.session.add(quiz_result)
        db.session.commit()
        
        # Update user's progress in the database
        if user_id:
            update_user_progress(user_id, data)
        
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

def update_user_progress(user_id, quiz_data):
    """Update user's progress after quiz completion"""
    try:
        user = User.query.get(user_id)
        if not user:
            print(f"❌ User {user_id} not found for progress update")
            return
        
        quiz_type = quiz_data.get('quiz_type', 'words')
        correct_answers = quiz_data.get('correct_answers', 0)
        percentage = quiz_data.get('percentage', 0)
        
        print(f"📈 Updating progress for user {user.username}: {quiz_type} quiz, {correct_answers} correct, {percentage}%")
        
        # Update words/sentences mastered based on quiz type
        if quiz_type == 'words' and percentage >= 80:  # Consider mastered if 80%+ correct
            new_words_mastered = max(user.words_mastered or 0, correct_answers)
            user.words_mastered = new_words_mastered
            print(f"   📝 Words mastered updated to: {new_words_mastered}")
        
        elif quiz_type == 'sentences' and percentage >= 80:
            new_sentences_mastered = max(user.sentences_mastered or 0, correct_answers)
            user.sentences_mastered = new_sentences_mastered
            print(f"   📝 Sentences mastered updated to: {new_sentences_mastered}")
        
        # Update accuracy rate (average of all quizzes)
        user_quizzes = QuizResult.query.filter_by(user_id=user_id).all()
        total_correct = sum(quiz.correct_answers for quiz in user_quizzes)
        total_questions = sum(quiz.total_questions for quiz in user_quizzes)
        
        if total_questions > 0:
            user.accuracy_rate = round((total_correct / total_questions) * 100, 1)
            print(f"   🎯 Accuracy rate updated to: {user.accuracy_rate}%")
        
        # Update streak
        today = datetime.utcnow().date()
        last_activity = user.last_activity_date.date() if user.last_activity_date else None
        
        if last_activity == today - timedelta(days=1):
            user.current_streak += 1
            print(f"   🔥 Streak increased to: {user.current_streak} days")
        elif last_activity != today:
            user.current_streak = 1
            print(f"   🔥 New streak started: 1 day")
        
        user.last_activity_date = datetime.utcnow()
        
        # Calculate total score
        user.total_score = calculate_user_score(user)
        print(f"   🏆 Total score updated to: {user.total_score}")
        
        db.session.commit()
        print(f"✅ Successfully updated progress for {user.username}")
        
    except Exception as e:
        print(f"❌ Error updating user progress: {str(e)}")
        db.session.rollback()

def calculate_user_score(user):
    """Calculate user score based on their progress"""
    words_mastered = user.words_mastered or 0
    sentences_mastered = user.sentences_mastered or 0
    current_streak = user.current_streak or 0
    accuracy_rate = user.accuracy_rate or 0
    
    word_score = words_mastered * 10
    sentence_score = sentences_mastered * 15
    streak_bonus = current_streak * 5
    accuracy_bonus = accuracy_rate * 2
    
    total_score = word_score + sentence_score + streak_bonus + accuracy_bonus
    
    print(f"   🧮 Score calculation for {user.username}:")
    print(f"     {words_mastered} words × 10 = {word_score}")
    print(f"     {sentences_mastered} sentences × 15 = {sentence_score}")
    print(f"     {current_streak} streak × 5 = {streak_bonus}")
    print(f"     {accuracy_rate}% accuracy × 2 = {accuracy_bonus}")
    print(f"     TOTAL: {total_score}")
    
    return total_score

@main_bp.route('/api/quiz-results/<int:result_id>')
@login_required
def get_quiz_result(result_id):
    """API endpoint to get specific quiz result"""
    try:
        result = QuizResult.query.get_or_404(result_id)
        
        # Check if the result belongs to the current user
        if result.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'Unauthorized access to quiz result'
            }), 403
        
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
                'timestamp': result.timestamp.isoformat(),
                'user_id': result.user_id
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving quiz result: {str(e)}'
        }), 500

@main_bp.route('/api/stats')
@login_required
def get_quiz_stats():
    """API endpoint to get overall quiz statistics"""
    try:
        user_id = current_user.id  # Changed from session to current_user
        
        # Get user-specific stats
        user_quizzes = QuizResult.query.filter_by(user_id=user_id).all()
        total_quizzes = len(user_quizzes)
        words_quizzes = len([q for q in user_quizzes if q.quiz_type == 'words'])
        sentence_quizzes = len([q for q in user_quizzes if q.quiz_type == 'sentences'])
        
        # Calculate user averages
        words_avg = db.session.query(db.func.avg(QuizResult.percentage))\
            .filter_by(quiz_type='words', user_id=user_id).scalar() or 0
        sentence_avg = db.session.query(db.func.avg(QuizResult.percentage))\
            .filter_by(quiz_type='sentences', user_id=user_id).scalar() or 0
        
        # Get user best scores
        words_best = db.session.query(db.func.max(QuizResult.percentage))\
            .filter_by(quiz_type='words', user_id=user_id).scalar() or 0
        sentence_best = db.session.query(db.func.max(QuizResult.percentage))\
            .filter_by(quiz_type='sentences', user_id=user_id).scalar() or 0
        
        # Get recent activity for current user
        recent_quizzes = QuizResult.query.filter_by(user_id=user_id)\
            .order_by(QuizResult.timestamp.desc()).limit(5).all()
        
        recent_activity = [{
            'id': quiz.id,
            'quiz_type': quiz.quiz_type,
            'score': quiz.score,
            'percentage': quiz.percentage,
            'timestamp': quiz.timestamp.isoformat()
        } for quiz in recent_quizzes]
        
        # Get current user's rank on leaderboard
        user_rank = get_user_rank(user_id)
        
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
                'recent_activity': recent_activity,
                'user_specific': True,
                'user_rank': user_rank,
                'username': current_user.username,
                'user_score': current_user.total_score if hasattr(current_user, 'total_score') else 0,
                'user_level': current_user.level if hasattr(current_user, 'level') else 1
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving stats: {str(e)}'
        }), 500

def get_user_rank(user_id):
    """Calculate user's rank based on total_score"""
    try:
        # Get all users ordered by total_score descending
        users = User.query.order_by(User.total_score.desc()).all()
        
        # Find the user's position
        for i, user in enumerate(users, start=1):
            if user.id == user_id:
                return i
        
        return None
    except Exception as e:
        print(f"Error calculating user rank: {e}")
        return None

@main_bp.route('/api/debug/user-progress')
@login_required
def debug_user_progress():
    """Debug endpoint to check user progress"""
    try:
        user_id = current_user.id  # Changed from session to current_user
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        user_quizzes = QuizResult.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'words_mastered': user.words_mastered,
                'sentences_mastered': user.sentences_mastered,
                'current_streak': user.current_streak,
                'accuracy_rate': user.accuracy_rate,
                'total_score': user.total_score,
                'level': user.level,
                'is_premium': user.is_premium if hasattr(user, 'is_premium') else False,
                'account_type': user.account_type if hasattr(user, 'account_type') else 'regular'
            },
            'quiz_count': len(user_quizzes),
            'quizzes': [{
                'id': q.id,
                'type': q.quiz_type,
                'correct': q.correct_answers,
                'total': q.total_questions,
                'percentage': q.percentage,
                'timestamp': q.timestamp.isoformat()
            } for q in user_quizzes]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving user progress: {str(e)}'
        }), 500

# Optional: Add a global leaderboard API
@main_bp.route('/api/leaderboard')
@login_required
def get_leaderboard():
    """Get global leaderboard data"""
    try:
        # Get top 50 users by total_score
        top_users = User.query.order_by(User.total_score.desc()).limit(50).all()
        
        leaderboard_data = []
        for i, user in enumerate(top_users, start=1):
            leaderboard_data.append({
                'rank': i,
                'username': user.username,
                'score': user.total_score,
                'level': user.level if hasattr(user, 'level') else 1,
                'words_mastered': user.words_mastered,
                'sentences_mastered': user.sentences_mastered,
                'streak': user.current_streak,
                'is_current_user': user.id == current_user.id
            })
        
        # Find current user's rank if not in top 50
        current_user_rank = get_user_rank(current_user.id)
        current_user_data = None
        
        if current_user_rank and current_user_rank > 50:
            user = User.query.get(current_user.id)
            current_user_data = {
                'rank': current_user_rank,
                'username': user.username,
                'score': user.total_score,
                'level': user.level if hasattr(user, 'level') else 1,
                'words_mastered': user.words_mastered,
                'sentences_mastered': user.sentences_mastered,
                'streak': user.current_streak,
                'is_current_user': True
            }
        
        return jsonify({
            'success': True,
            'leaderboard': leaderboard_data,
            'current_user_rank': current_user_rank,
            'current_user_data': current_user_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving leaderboard: {str(e)}'
        }), 500