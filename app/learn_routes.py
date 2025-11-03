from flask import Blueprint, render_template, jsonify
import random
import request

# Create blueprint
learn_bp = Blueprint('learn', __name__)

# Import your existing data (adjust these imports based on your actual data structure)
try:
    from words_routes import HSK1_WORDS
except ImportError:
    # Fallback empty list if import fails
    HSK1_WORDS = []

try:
    from sentence_routes import HSK1_SENTENCES
except ImportError:
    # Fallback empty list if import fails
    HSK1_SENTENCES = []

@learn_bp.route('/learn')
def learn_page():
    """Serve the learn.html page"""
    return render_template('learn.html')

@learn_bp.route('/words/api/all-words')
def get_all_words():
    """API endpoint to get all HSK1 words for learning"""
    try:
        # If we can't import from words_routes, use the data directly
        if not HSK1_WORDS:
            # You would replace this with your actual data structure
            words = [
                {
                    'word': '你好',
                    'pinyin': 'nǐ hǎo',
                    'meaning': 'Hello',
                    'translation': 'Hello',
                    'example': '你好，我是小明。'
                },
                {
                    'word': '谢谢',
                    'pinyin': 'xiè xiè', 
                    'meaning': 'Thank you',
                    'translation': 'Thank you',
                    'example': '谢谢你的帮助。'
                }
                # Add more words as needed
            ]
        else:
            words = HSK1_WORDS
        
        # Format the words for the learn page
        formatted_words = []
        for word in words:
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
        # If we can't import from sentences_routes, use the data directly
        if not HSK1_SENTENCES:
            # You would replace this with your actual data structure
            sentences = [
                {
                    'sentence': '你好吗？',
                    'pinyin': 'nǐ hǎo ma?',
                    'translation': 'How are you?',
                    'meaning': 'How are you?'
                },
                {
                    'sentence': '我是学生。',
                    'pinyin': 'wǒ shì xué shēng',
                    'translation': 'I am a student.',
                    'meaning': 'I am a student.'
                }
                # Add more sentences as needed
            ]
        else:
            sentences = HSK1_SENTENCES
        
        # Format the sentences for the learn page
        formatted_sentences = []
        for sentence in sentences:
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

@learn_bp.route('/api/learn-stats')
def get_learn_stats():
    """API endpoint to get learning statistics"""
    try:
        total_words = len(HSK1_WORDS) if HSK1_WORDS else 0
        total_sentences = len(HSK1_SENTENCES) if HSK1_SENTENCES else 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total_words': total_words,
                'total_sentences': total_sentences,
                'total_content': total_words + total_sentences
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving learning stats: {str(e)}'
        }), 500

@learn_bp.route('/api/search-content')
def search_learn_content():
    """API endpoint to search both words and sentences"""
    try:
        query = request.args.get('q', '').lower().strip()
        
        if not query:
            return jsonify({
                'success': True,
                'words': [],
                'sentences': []
            })
        
        # Search words
        matching_words = []
        if HSK1_WORDS:
            for word in HSK1_WORDS:
                if (query in word.get('word', '').lower() or 
                    query in word.get('pinyin', '').lower() or 
                    query in word.get('meaning', '').lower() or
                    query in word.get('translation', '').lower()):
                    matching_words.append(word)
        
        # Search sentences
        matching_sentences = []
        if HSK1_SENTENCES:
            for sentence in HSK1_SENTENCES:
                if (query in sentence.get('sentence', '').lower() or 
                    query in sentence.get('pinyin', '').lower() or 
                    query in sentence.get('translation', '').lower() or
                    query in sentence.get('meaning', '').lower()):
                    matching_sentences.append(sentence)
        
        return jsonify({
            'success': True,
            'words': matching_words[:10],  # Limit results
            'sentences': matching_sentences[:10]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error searching content: {str(e)}'
        }), 500