"""
CipherGuard — Password Strength Analyzer API Routes
Password ki strength check karne ka endpoint — real-time frontend feedback ke liye
Engineered & Crafted by Raj
"""

from flask import Blueprint, request, jsonify, session

# Core logic import karo
from core.strength_analyzer import analyze_password

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
