from flask import Blueprint, jsonify, request, session
from flask_login import login_required, current_user
from datetime import datetime
import json
from .models import db, QuizResult, User
import uuid

results_bp = Blueprint('results', __name__)


@results_bp.route('/api/save-quiz-result', methods=['POST'])
@login_required
def save_quiz_result():
    """
    Save quiz result to database
    Expects JSON with: {
        quiz_type: 'words' or 'sentences',
        score: number,
        total_questions: number,
        correct_answers: number,
        incorrect_answers: number,
        percentage: number,
        time_taken: number (in seconds),
        user_answers: array
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['quiz_type', 'score', 'total_questions', 'correct_answers', 
                         'incorrect_answers', 'percentage']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        # Create quiz result
        quiz_result = QuizResult(
            quiz_type=data['quiz_type'],
            score=int(data['score']),
            total_questions=int(data['total_questions']),
            correct_answers=int(data['correct_answers']),
            incorrect_answers=int(data['incorrect_answers']),
            percentage=float(data['percentage']),
            time_taken=int(data.get('time_taken', 0)),
            user_id=current_user.id,
            timestamp=datetime.utcnow()
        )
        
        # Store user answers if provided
        if 'user_answers' in data:
            quiz_result.set_user_answers(data['user_answers'])
        
        # Add to database
        db.session.add(quiz_result)
        db.session.commit()
        
        # Update user stats
        if hasattr(current_user, 'update_stats'):
            current_user.update_stats(quiz_result)
        
        return jsonify({
            'success': True,
            'message': 'Quiz result saved successfully',
            'quiz_id': quiz_result.id,
            'timestamp': quiz_result.timestamp.isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error saving quiz result: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@results_bp.route('/api/quiz-results', methods=['GET'])
@login_required
def get_quiz_results():
    """
    Get all quiz results for current user
    Optional query params:
    - quiz_type: filter by 'words' or 'sentences'
    - limit: number of results to return (default 50)
    - offset: pagination offset (default 0)
    """
    try:
        quiz_type = request.args.get('quiz_type', None)
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query
        query = QuizResult.query.filter_by(user_id=current_user.id)
        
        if quiz_type:
            query = query.filter_by(quiz_type=quiz_type)
        
        # Get total count before pagination
        total = query.count()
        
        # Get paginated results sorted by most recent first
        results = query.order_by(QuizResult.timestamp.desc()).limit(limit).offset(offset).all()
        
        # Convert to JSON-serializable format
        results_data = []
        for result in results:
            results_data.append({
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
                'date': result.timestamp.strftime('%Y-%m-%d'),
                'time': result.timestamp.strftime('%H:%M:%S')
            })
        
        return jsonify({
            'success': True,
            'data': results_data,
            'total': total,
            'limit': limit,
            'offset': offset,
            'returned': len(results_data)
        }), 200
        
    except Exception as e:
        print(f"Error fetching quiz results: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@results_bp.route('/api/quiz-results/<int:result_id>', methods=['GET'])
@login_required
def get_quiz_result(result_id):
    """
    Get a specific quiz result
    """
    try:
        result = QuizResult.query.filter_by(id=result_id, user_id=current_user.id).first()
        
        if not result:
            return jsonify({'success': False, 'error': 'Quiz result not found'}), 404
        
        return jsonify({
            'success': True,
            'data': {
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
                'date': result.timestamp.strftime('%Y-%m-%d'),
                'time': result.timestamp.strftime('%H:%M:%S')
            }
        }), 200
        
    except Exception as e:
        print(f"Error fetching quiz result: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@results_bp.route('/api/quiz-stats', methods=['GET'])
@login_required
def get_quiz_stats():
    """
    Get quiz statistics for current user
    Returns total quizzes, average score, total time spent, etc.
    """
    try:
        quiz_type = request.args.get('quiz_type', None)
        
        # Build query
        query = QuizResult.query.filter_by(user_id=current_user.id)
        
        if quiz_type:
            query = query.filter_by(quiz_type=quiz_type)
        
        results = query.all()
        
        if not results:
            return jsonify({
                'success': True,
                'data': {
                    'total_quizzes': 0,
                    'average_score': 0,
                    'average_percentage': 0,
                    'total_time': 0,
                    'best_score': 0,
                    'worst_score': 0,
                    'total_correct': 0,
                    'total_incorrect': 0
                }
            }), 200
        
        # Calculate statistics
        total_quizzes = len(results)
        total_score = sum(r.score for r in results)
        total_percentage = sum(r.percentage for r in results)
        total_time = sum(r.time_taken for r in results)
        best_score = max(r.score for r in results)
        worst_score = min(r.score for r in results)
        total_correct = sum(r.correct_answers for r in results)
        total_incorrect = sum(r.incorrect_answers for r in results)
        
        return jsonify({
            'success': True,
            'data': {
                'total_quizzes': total_quizzes,
                'average_score': round(total_score / total_quizzes, 2),
                'average_percentage': round(total_percentage / total_quizzes, 2),
                'total_time': total_time,
                'best_score': best_score,
                'worst_score': worst_score,
                'total_correct': total_correct,
                'total_incorrect': total_incorrect,
                'accuracy_rate': round((total_correct / (total_correct + total_incorrect) * 100), 2) if (total_correct + total_incorrect) > 0 else 0
            }
        }), 200
        
    except Exception as e:
        print(f"Error fetching quiz stats: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@results_bp.route('/api/quiz-results/by-date', methods=['GET'])
@login_required
def get_results_by_date():
    """
    Get quiz results grouped by date
    """
    try:
        results = QuizResult.query.filter_by(user_id=current_user.id).order_by(
            QuizResult.timestamp.desc()
        ).all()
        
        # Group by date
        results_by_date = {}
        for result in results:
            date_key = result.timestamp.strftime('%Y-%m-%d')
            if date_key not in results_by_date:
                results_by_date[date_key] = []
            
            results_by_date[date_key].append({
                'id': result.id,
                'quiz_type': result.quiz_type,
                'score': result.score,
                'percentage': result.percentage,
                'time': result.timestamp.strftime('%H:%M:%S'),
                'total_questions': result.total_questions,
                'correct_answers': result.correct_answers
            })
        
        return jsonify({
            'success': True,
            'data': results_by_date
        }), 200
        
    except Exception as e:
        print(f"Error fetching results by date: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
