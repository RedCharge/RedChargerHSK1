from flask import Blueprint, render_template, jsonify
import random

# Create blueprint
learn_bp = Blueprint('learn', __name__)

@learn_bp.route('/learn')
def learn_page():
    """Serve the learn.html page"""
    return render_template('learn.html')

@learn_bp.route('/words/api/all-words')
def get_all_words():
    """API endpoint to get all HSK1 words for learning"""
    try:
        # Import your actual words data
        from .words_routes import HSK1_WORDS
        
        # Format the words for the learn page
        formatted_words = []
        for word in HSK1_WORDS:
            formatted_word = {
                'word': word.get('word', ''),
                'pinyin': word.get('pinyin', ''),
                'meaning': word.get('meaning', word.get('translation', '')),
                'example': word.get('example', '')
            }
            formatted_words.append(formatted_word)
        
        return jsonify({
            'success': True,
            'words': formatted_words
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving words: {str(e)}'
        }), 500

@learn_bp.route('/sentences/api/all-sentences')
def get_all_sentences():
    """API endpoint to get all HSK1 sentences for learning"""
    try:
        # Import your actual sentences data
        from .sentence_routes import HSK1_SENTENCES
        
        # Format the sentences for the learn page
        formatted_sentences = []
        for sentence in HSK1_SENTENCES:
            formatted_sentence = {
                'sentence': sentence.get('sentence', ''),
                'pinyin': sentence.get('pinyin', ''),
                'translation': sentence.get('translation', sentence.get('meaning', '')),
                'meaning': sentence.get('meaning', sentence.get('translation', '')),
                'notes': sentence.get('notes', '')
            }
            formatted_sentences.append(formatted_sentence)
        
        return jsonify({
            'success': True,
            'sentences': formatted_sentences
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving sentences: {str(e)}'
        }), 500