"""
CipherGuard — Hash Extractor API Routes
Linux shadow aur Windows SAM/SYSTEM se hash extraction endpoints
Engineered & Crafted by Raj
"""

import os
import json
import tempfile
from flask import Blueprint, request, jsonify, Response, session

# Core logic import karo
from core.hash_extractor import parse_shadow_file, extract_sam_hashes

# Blueprint banao hash extraction routes ke liye
hash_extract_bp = Blueprint('hash_extract', __name__, url_prefix='/api/hash')

# Module level variable — extracted hashes store karo
_last_results = []


@hash_extract_bp.route('/extract', methods=['POST'])
def extract():
    """
    Hash extraction endpoint — Linux shadow ya Windows SAM+SYSTEM files se hashes nikalta hai
    Multipart form data accept karta hai files ke saath
    'mode' field se pata chalta hai Linux hai ya Windows
    """
    global _last_results

    # Mode check karo — linux ya windows
    mode = request.form.get('mode', 'linux')

    if mode == 'linux':
        # Linux mode — shadow file upload se hashes nikalo
        shadow_file = request.files.get('shadow')
        if not shadow_file:
            return jsonify({"status": "error", "message": "Shadow file upload karo"}), 400

        # File content padho — text format mein
        file_content = shadow_file.read().decode('utf-8', errors='ignore')

        # Core function call karo parsing ke liye
        results = parse_shadow_file(file_content)

    elif mode == 'windows':
        # Windows mode — SAM aur SYSTEM dono files chahiye
        sam_file = request.files.get('sam')
        system_file = request.files.get('system')

        if not sam_file or not system_file:
            return jsonify({"status": "error", "message": "SAM aur SYSTEM dono files upload karo"}), 400

        # Temporary files mein save karo — impacket ko file paths chahiye
        temp_dir = tempfile.mkdtemp()
        sam_path = os.path.join(temp_dir, 'SAM')
        system_path = os.path.join(temp_dir, 'SYSTEM')

        sam_file.save(sam_path)
        system_file.save(system_path)

        # Core function call karo extraction ke liye
        results = extract_sam_hashes(sam_path, system_path)

        # Temp files cleanup karo
        try:
            os.remove(sam_path)
            os.remove(system_path)
            os.rmdir(temp_dir)
        except Exception:
            pass  # Cleanup mein error aaye toh ignore karo

        # Error dict check karo — impacket fail ho sakta hai
        if isinstance(results, dict) and 'error' in results:
            return jsonify({"status": "error", "message": results['error']}), 500

    else:
        return jsonify({"status": "error", "message": "Invalid mode — 'linux' ya 'windows' use karo"}), 400

    # Results store karo session mein aur module level pe
    _last_results = results
    session['hash_results'] = results

    # Success response bhejo
    return jsonify({
        "status": "success",
        "results": results,
        "count": len(results)
    })


@hash_extract_bp.route('/stream', methods=['GET'])
def stream():
    """
    SSE endpoint — extraction process ki log messages stream karta hai
    Real-time feedback deta hai frontend ko
    """
    def event_stream():
        """
        Extraction process ke log messages yield karta hai
        """
        # Initial message bhejo
        yield f"data: {json.dumps({'log': '[INIT] Hash extraction engine starting...'})}\n\n"
        yield f"data: {json.dumps({'log': '[INFO] File parsing in progress...'})}\n\n"

        # Agar results available hain toh unke baare mein bhejo
        if _last_results:
            yield f"data: {json.dumps({'log': f'[SUCCESS] {len(_last_results)} hashes extracted successfully.'})}\n\n"
            for result in _last_results:
                msg = f"[HASH] {result.get('username', 'N/A')} | {result.get('algorithm', 'N/A')} | {result.get('hash', 'N/A')[:40]}..."
                yield f"data: {json.dumps({'log': msg})}\n\n"
        else:
            yield f"data: {json.dumps({'log': '[WARN] Koi hash extract nahi hua — file check karo.'})}\n\n"

        yield f"data: {json.dumps({'log': '[DONE] Extraction process complete.', 'done': True})}\n\n"

    # SSE response return karo correct headers ke saath
    return Response(
        event_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )
