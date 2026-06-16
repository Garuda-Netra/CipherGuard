"""
CipherGuard — Report Generator API Routes
Saare tool results combine karke final security audit report generate karta hai
Engineered & Crafted by Raj
"""

import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, session

# Core logic import karo
from core.report_builder import build_report

# Blueprint banao report routes ke liye
report_bp = Blueprint('report', __name__, url_prefix='/api/report')


@report_bp.route('/generate', methods=['GET'])
def generate():
    """
    Complete security audit report generate karta hai
    Session mein stored saare tool results collect karke report builder ko bhejta hai
    Report ko file mein bhi save karta hai
    """
    # Session se saare stored results collect karo
    session_data = {
        'dictionary_results': session.get('dictionary_results', {}),
        'hash_results': session.get('hash_results', []),
        'brute_results': session.get('brute_results', {}),
        'strength_results': session.get('strength_results', {})
    }

    # Module level variables se bhi data le lo — SSE streams session mein store nahi kar paate
    # Routes ke module level variables check karo
    try:
        from routes.dictionary import _generated_words, _current_params
        if _generated_words:
            session_data['dictionary_results'] = {
                'total_words': len(_generated_words),
                'mutations_used': _current_params.get('mutations', []),
                'file_path': os.environ.get('WORDLIST_OUTPUT_PATH', 'backend/output/wordlist.txt')
            }
    except ImportError:
        pass

    try:
        from routes.hash_extract import _last_results
        if _last_results:
            session_data['hash_results'] = _last_results
    except ImportError:
        pass

    try:
        from routes.brute_force import _crack_results
        if _crack_results:
            session_data['brute_results'] = _crack_results
    except ImportError:
        pass

    # Core report builder call karo
    report = build_report(session_data)

    # Report ko file mein save karo
    output_path = os.environ.get('REPORT_OUTPUT_PATH', 'backend/output/report.txt')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        # Plain text report file mein likh do
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("   CIPHERGUARD — SECURITY AUDIT REPORT\n")
            f.write(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")

            f.write("EXECUTIVE SUMMARY\n")
            f.write("-" * 40 + "\n")
            f.write(report['executive_summary'] + "\n\n")

            f.write("DICTIONARY RESULTS\n")
            f.write("-" * 40 + "\n")
            dict_res = report['dictionary_results']
            f.write(f"Total Words: {dict_res.get('total_words', 0)}\n")
            f.write(f"Mutations: {', '.join(dict_res.get('mutations_used', []))}\n")
            f.write(f"File: {dict_res.get('file_path', 'N/A')}\n\n")

            f.write("HASH FINDINGS\n")
            f.write("-" * 40 + "\n")
            for h in report.get('hash_findings', []):
                f.write(f"  {h.get('username', 'N/A')} | {h.get('algorithm', 'N/A')} | {h.get('hash', 'N/A')[:50]}\n")
            f.write("\n")

            f.write("BRUTE FORCE RESULTS\n")
            f.write("-" * 40 + "\n")
            brute_res = report['brute_force_results']
            f.write(f"Target: {brute_res.get('target_hash', 'N/A')[:50]}\n")
            f.write(f"Found: {brute_res.get('found', False)}\n")
            if brute_res.get('found'):
                f.write(f"Password: {brute_res.get('password', 'N/A')}\n")
            f.write(f"Attempts: {brute_res.get('attempts', 0)}\n")
            f.write(f"Time: {brute_res.get('time_taken', 0)}s\n\n")

            f.write("STRENGTH SUMMARY\n")
            f.write("-" * 40 + "\n")
            for s in report.get('strength_summary', []):
                f.write(f"  Rating: {s.get('rating', 'N/A')} | Entropy: {s.get('entropy', 0)} | Score: {s.get('score', 0)}\n")
            f.write("\n")

            f.write("RISK MATRIX\n")
            f.write("-" * 40 + "\n")
            for r in report.get('risk_matrix', []):
                f.write(f"  {r.get('password_sample', 'N/A')} | {r.get('rating', 'N/A')} | {r.get('estimated_crack_time', 'N/A')} | {r.get('risk_level', 'N/A')}\n")
            f.write("\n")

            f.write("RECOMMENDATIONS\n")
            f.write("-" * 40 + "\n")
            for rec in report.get('recommendations', []):
                f.write(f"  • {rec}\n")
            f.write("\n")

            f.write("=" * 60 + "\n")
            f.write(report.get('credits', 'Engineered & Crafted by Raj') + "\n")
            f.write("=" * 60 + "\n")

    except Exception as e:
        # File save mein error aaye toh log karo lekin response toh bhejo
        print(f"[WARN] Report file save mein error: {e}")

    # JSON response bhejo frontend ke liye
    return jsonify({
        "status": "success",
        "report": report,
        "saved_to": output_path
    })
