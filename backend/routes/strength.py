"""
CipherGuard — Password Strength Analyzer API Routes
Password ki strength check karne ka endpoint — real-time frontend feedback ke liye
Engineered & Crafted by Raj
"""

import json
import time
from flask import Blueprint, request, jsonify, session, Response

# Core logic import karo
from core.strength_analyzer import analyze_password, check_pwned_password

# Blueprint banao strength analysis routes ke liye
strength_bp = Blueprint('strength', __name__, url_prefix='/api/strength')


@strength_bp.route('/analyze', methods=['POST'])
def analyze():
    """
    Password strength analyze karta hai
    JSON body accept karta hai: {"password": str}
    Full analysis result return karta hai — rating, entropy, checks, tips sab
    Frontend pe har keystroke pe debounce ke saath call hota hai
    """
    # Request se password nikalo
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "JSON body chahiye"}), 400

    password = data.get('password', '')
    if not password:
        return jsonify({"status": "error", "message": "Password dena zaroori hai"}), 400

    # Core analyzer function call karo — saari heavy lifting wahan hoti hai
    result = analyze_password(password)

    # Session mein store karo — report generation ke liye baad mein chahiye hoga
    session['strength_results'] = result

    # Full result return karo frontend ke liye
    return jsonify({
        "status": "success",
        "data": result
    })

@strength_bp.route('/full_scan', methods=['POST'])
def full_scan():
    """
    Real full vulnerability scan with HaveIBeenPwned API check.
    Uses Server-Sent Events (SSE) to simulate the terminal output.
    """
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "JSON body chahiye"}), 400

    password = data.get('password', '')
    if not password:
        return jsonify({"status": "error", "message": "Password dena zaroori hai"}), 400

    def event_stream():
        yield f"data: {json.dumps({'log': '[INIT] Running full vulnerability scan...'})}\n\n"
        time.sleep(0.5)
        
        yield f"data: {json.dumps({'log': '[SCAN] Checking against leaked databases (HaveIBeenPwned)...'})}\n\n"
        
        # Real API check
        is_pwned, count = check_pwned_password(password)
        
        if is_pwned:
            yield f"data: {json.dumps({'log': f'[WARNING] Password found in {count:,} known data breaches!'})}\n\n"
        else:
            yield f"data: {json.dumps({'log': '[SAFE] Password not found in known breaches.'})}\n\n"
            
        time.sleep(0.5)
        yield f"data: {json.dumps({'log': '[SCAN] Analyzing pattern predictability...'})}\n\n"
        
        result = analyze_password(password)
        time.sleep(0.5)
        
        rating = result['rating']
        yield f"data: {json.dumps({'log': f'[DONE] Analysis complete. Overall rating: {rating}.'})}\n\n"
        yield f"data: {json.dumps({'done': True, 'pwned': is_pwned, 'pwned_count': count})}\n\n"

    return Response(
        event_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )
