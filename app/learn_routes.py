from flask import Blueprint, render_template, jsonify

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
        
        # Pass ALL word data to the frontend
        formatted_words = []
        for word in HSK1_WORDS:
            formatted_word = {
                'word': word.get('word', ''),
                'pinyin': word.get('pinyin', ''),
                'meaning': word.get('meaning', ''),
                'translation': word.get('translation', ''),
                'definition': word.get('definition', ''),
                'example': word.get('example', ''),
                # Include any other fields your words have
                'partOfSpeech': word.get('partOfSpeech', ''),
                'usage': word.get('usage', ''),
                'notes': word.get('notes', '')
            }
            # Remove empty fields
            formatted_word = {k: v for k, v in formatted_word.items() if v}
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
        
        # Pass ALL sentence data to the frontend
        formatted_sentences = []
        for sentence in HSK1_SENTENCES:
            formatted_sentence = {
                'sentence': sentence.get('sentence', ''),
                'pinyin': sentence.get('pinyin', ''),
                'translation': sentence.get('translation', ''),
                'meaning': sentence.get('meaning', ''),
                'definition': sentence.get('definition', ''),
                'notes': sentence.get('notes', ''),
                'example': sentence.get('example', ''),
                # Include any other fields your sentences have
                'structure': sentence.get('structure', ''),
                'grammar': sentence.get('grammar', ''),
                'usage': sentence.get('usage', '')
            }
            # Remove empty fields
            formatted_sentence = {k: v for k, v in formatted_sentence.items() if v}
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