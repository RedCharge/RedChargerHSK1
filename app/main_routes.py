from flask import Blueprint, render_template, request, jsonify, session
from datetime import datetime
import json
import uuid

# Import db and models from your models.py
from .models import db, QuizResult

# Create Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Render the main landing page"""
    return render_template('index.html')

@main_bp.route('/result')
def result():
    """Render the result page"""
    return render_template('result.html')

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