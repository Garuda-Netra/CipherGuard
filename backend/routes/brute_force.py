"""
CipherGuard — Brute Force Engine API Routes
Hash cracking ke endpoints — wordlist aur incremental modes mein SSE streaming
ETHICAL USE ONLY — CONTROLLED LAB ENVIRONMENT ONLY
Engineered & Crafted by Raj
"""

import os
import json
import tempfile
from flask import Blueprint, request, jsonify, Response, session

# Core logic import karo — saari heavy lifting core module mein hoti hai
from core.brute_engine import wordlist_attack, incremental_attack, calculate_eta

# Blueprint banao brute force routes ke liye
brute_force_bp = Blueprint('brute_force', __name__, url_prefix='/api/bruteforce')

# Module level variables — crack params aur results store karo
_crack_params = {}
_crack_results = {}

# Supported hash types ki list
VALID_HASH_TYPES = ['md5', 'sha1', 'sha256', 'sha512', 'ntlm']


@brute_force_bp.route('/crack', methods=['POST'])
def crack():
    """
    Brute force attack initiate karta hai
    JSON body ya multipart form data accept karta hai
    Params validate karke session mein store karta hai stream endpoint ke liye
    """
    global _crack_params

    # JSON ya form data — dono support karo
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    if not data:
        return jsonify({"status": "error", "message": "Request data chahiye"}), 400

    # Target hash nikalo — yeh required field hai
    target_hash = data.get('hash', '').strip()
    if not target_hash:
        return jsonify({"status": "error", "message": "Target hash dena zaroori hai"}), 400

    # Hash type validate karo
    hash_type = data.get('hash_type', 'md5').lower()
    if hash_type not in VALID_HASH_TYPES:
        return jsonify({
            "status": "error",
            "message": f"Invalid hash type. Allowed: {', '.join(VALID_HASH_TYPES)}"
        }), 400

    # Attack mode check karo — wordlist ya incremental
    mode = data.get('mode', 'wordlist')

    # Wordlist mode mein file handle karo
    wordlist_path = None
    if mode == 'wordlist':
        # File upload check karo
        if 'wordlist' in request.files:
            wl_file = request.files['wordlist']
            # Temporary location pe save karo
            temp_dir = tempfile.mkdtemp()
            wordlist_path = os.path.join(temp_dir, 'wordlist.txt')
            wl_file.save(wordlist_path)
        else:
            # Path directly diya ho toh woh use karo
            wordlist_path = data.get('wordlist_path', '')
            if not wordlist_path:
                # Default wordlist path .env se lao
                wordlist_path = os.environ.get('WORDLIST_OUTPUT_PATH', 'backend/output/wordlist.txt')

        if not os.path.exists(wordlist_path):
            return jsonify({
                "status": "error",
                "message": f"Wordlist file nahi mili: {wordlist_path}"
            }), 400

    # Params store karo — stream endpoint inhe access karega
    _crack_params = {
        'target_hash': target_hash,
        'hash_type': hash_type,
        'mode': mode,
        'wordlist_path': wordlist_path
    }

    return jsonify({
        "status": "started",
        "stream_url": "/api/bruteforce/stream"
    })


@brute_force_bp.route('/stream', methods=['GET'])
def stream():
    """
    SSE endpoint — brute force progress real-time mein stream karta hai
    Har 100 attempts pe progress update bhejta hai with ETA
    Found/exhausted pe final result bhejta hai
    """
    def event_stream():
        """
        Attack generator se progress events yield karta hai SSE format mein
        """
        global _crack_params, _crack_results

        target_hash = _crack_params.get('target_hash', '')
        hash_type = _crack_params.get('hash_type', 'md5')
        mode = _crack_params.get('mode', 'wordlist')
        wordlist_path = _crack_params.get('wordlist_path', '')

        if not target_hash:
            yield f"data: {json.dumps({'error': 'Pehle /crack endpoint call karo params set karne ke liye'})}\n\n"
            return

        # Starting message bhejo
        yield f"data: {json.dumps({'log': f'[INIT] {mode.upper()} attack starting for {hash_type.upper()}...'})}\n\n"

        # Total estimated attempts — ETA calculation ke liye
        total_estimated = 0
        if mode == 'wordlist' and wordlist_path:
            # Wordlist file ki lines count karo
            try:
                with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                    total_estimated = sum(1 for _ in f)
            except Exception:
                total_estimated = 10000  # Fallback estimate

            # Wordlist attack generator start karo
            attack_gen = wordlist_attack(target_hash, hash_type, wordlist_path)
        else:
            # Incremental attack — max length .env se lao
            max_length = int(os.environ.get('MAX_BRUTE_FORCE_LENGTH', '4'))
            total_estimated = sum(95 ** l for l in range(1, max_length + 1))  # Approximate
            attack_gen = incremental_attack(target_hash, hash_type, max_length)

        # Generator se progress events process karo
        for progress in attack_gen:
            if progress.get('found'):
                # PASSWORD MIL GAYA! Success event bhejo
                _crack_results = {
                    'found': True,
                    'password': progress['password'],
                    'count': progress['count'],
                    'time_taken': progress['time_taken'],
                    'target_hash': target_hash,
                    'method': mode
                }
                # Session mein bhi store karo
                yield f"data: {json.dumps({'found': True, 'password': progress['password'], 'time_taken': progress['time_taken'], 'count': progress['count']})}\n\n"
                return

            elif progress.get('exhausted'):
                # Saare options khatam — failure event bhejo
                _crack_results = {
                    'found': False,
                    'count': progress['count'],
                    'time_taken': progress.get('time_taken', 0),
                    'target_hash': target_hash,
                    'method': mode
                }
                error_msg = progress.get('error', '')
                yield f"data: {json.dumps({'found': False, 'exhausted': True, 'count': progress['count'], 'error': error_msg})}\n\n"
                return

            else:
                # Progress update — ETA calculate karke bhejo
                per_second = progress.get('per_second', 0)
                count = progress.get('count', 0)
                eta = calculate_eta(count, per_second, total_estimated)

                # Percentage calculate karo
                percent = min(99, int((count / max(total_estimated, 1)) * 100))

                # Log message alag se banao — nested f-string issues se bachne ke liye
                current_attempt = progress.get('attempt', '')
                log_msg = f"[CRACK] Attempt #{count}: {current_attempt} @ {per_second}/s"
                event_data = {
                    'type': 'progress',
                    'attempt': current_attempt,
                    'count': count,
                    'per_second': per_second,
                    'eta': eta,
                    'percent': percent,
                    'log': log_msg
                }
                yield f"data: {json.dumps(event_data)}\n\n"

    # SSE response return karo
    return Response(
        event_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )
