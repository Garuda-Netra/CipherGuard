"""
CipherGuard — Dictionary Generator API Routes
Wordlist generate karne ke endpoints — SSE streaming support ke saath
Engineered & Crafted by Raj
"""

import os
import json
from flask import Blueprint, request, jsonify, Response, session

# Core logic import karo — duplicate code nahi likhenge
from core.dict_generator import generate_wordlist, estimate_wordlist_count

# Blueprint banao dictionary routes ke liye
dictionary_bp = Blueprint('dictionary', __name__, url_prefix='/api/dictionary')

# Module level variable — stream ke liye base_words aur mutations store karo
_current_params = {}
_generated_words = []


@dictionary_bp.route('/generate', methods=['POST'])
def generate():
    """
    Wordlist generation start karta hai
    JSON body accept karta hai: {"base_words": "raj,admin", "mutations": ["leet","upper"]}
    Generation ke params session mein store karta hai stream endpoint ke liye
    """
    # Request se data nikalo
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "JSON body chahiye"}), 400

    # Base words ko comma se split karo aur whitespace hatao
    base_words_raw = data.get('base_words', '')
    base_words = [w.strip() for w in base_words_raw.split(',') if w.strip()]

    if not base_words:
        return jsonify({"status": "error", "message": "Base words dena zaroori hai"}), 400

    # Mutations list nikalo
    mutations = data.get('mutations', [])

    # Estimated count calculate karo
    estimated = estimate_wordlist_count(base_words, mutations)

    # Params module level pe store karo — stream endpoint access karega
    global _current_params
    _current_params = {
        'base_words': base_words,
        'mutations': mutations
    }

    # Session mein bhi store karo report ke liye
    session['dict_params'] = {
        'base_words': base_words,
        'mutations': mutations,
        'estimated_count': estimated
    }

    return jsonify({
        "status": "started",
        "estimated_count": estimated,
        "stream_url": "/api/dictionary/stream"
    })


@dictionary_bp.route('/stream', methods=['GET'])
def stream():
    """
    SSE endpoint — real-time mein generated words stream karta hai frontend ko
    Content-Type text/event-stream set karna zaroori hai SSE ke liye
    """
    def event_stream():
        """
        Generator function jo SSE events yield karta hai
        Har word ke liye ek SSE event bhejta hai
        """
        global _current_params, _generated_words

        base_words = _current_params.get('base_words', [])
        mutations = _current_params.get('mutations', [])

        if not base_words:
            # Agar params nahi hain toh error bhejo
            yield f"data: {json.dumps({'error': 'Pehle /generate endpoint call karo'})}\n\n"
            return

        count = 0
        _generated_words = []

        # Core generator se ek ek word stream karo
        for word in generate_wordlist(base_words, mutations):
            count += 1
            _generated_words.append(word)

            # Har word ka SSE event bhejo
            yield f"data: {json.dumps({'word': word, 'count': count})}\n\n"

        # Output file mein save karo
        output_path = os.environ.get('WORDLIST_OUTPUT_PATH', 'backend/output/wordlist.txt')
        # Path create karo agar exist nahi karta
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(_generated_words))

        # Session mein dictionary results store karo report ke liye
        # Note: session yahan directly accessible nahi hai SSE generator mein
        # isliye module level variable use karte hain

        # Done event bhejo
        yield f"data: {json.dumps({'done': True, 'total': count, 'file_path': output_path})}\n\n"

    # SSE response return karo — correct headers ke saath
    return Response(
        event_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )


@dictionary_bp.route('/save', methods=['POST'])
def save():
    """
    Generated wordlist ko file mein save karta hai
    .env se output path utha hai
    """
    global _generated_words

    if not _generated_words:
        return jsonify({"status": "error", "message": "Pehle wordlist generate karo"}), 400

    # Output path .env se lao
    output_path = os.environ.get('WORDLIST_OUTPUT_PATH', 'backend/output/wordlist.txt')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # File mein likh do
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(_generated_words))

    return jsonify({
        "status": "success",
        "file_path": output_path,
        "total_words": len(_generated_words)
    })
