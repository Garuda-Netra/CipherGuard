"""
CipherGuard — Main Flask Application Entry Point
Yeh file poora Flask server start karti hai — saare blueprints register hote hain yahan
Engineered & Crafted by Raj
"""

import os
import sys
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Windows pe UTF-8 output force karo — Sanskrit text ke liye zaroori hai
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Colorama import karo banner ke liye
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    # Agar colorama nahi hai toh dummy classes banao
    class Fore:
        CYAN = ''; YELLOW = ''; GREEN = ''; RED = ''; WHITE = ''; RESET = ''
    class Style:
        RESET_ALL = ''; BRIGHT = ''

# ASCII Banner — har startup pe print hoga
BANNER = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════╗
║{Fore.YELLOW}           C I P H E R G U A R D                 {Fore.CYAN}║
║{Fore.YELLOW}       Password Credential Audit Suite            {Fore.CYAN}║
║{Fore.YELLOW}  "यद्भावं तद्भवति" — As you think, so you become {Fore.CYAN}║
║{Fore.YELLOW}         Engineered & Crafted by Raj              {Fore.CYAN}║
╚══════════════════════════════════════════════════╝{Style.RESET_ALL}
"""

# .env file root level se load karo — backend/ ke parent directory mein hai
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)


def create_app():
    """
    Flask app factory function — app create karke configure karta hai
    Saare blueprints register karta hai aur CORS enable karta hai
    """
    # Flask app initialize karo
    app = Flask(__name__)

    # Secret key .env se lao — session ke liye zaroori hai
    app.secret_key = os.environ.get('SECRET_KEY', 'cipherguard-default-secret-key-change-in-production')

    # Session configuration — server-side sessions ke liye
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file upload

    # CORS enable karo — frontend se API calls allow karne ke liye
    CORS(app, supports_credentials=True)

    # Output directory create karo agar exist nahi karta
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)

    # Saare route blueprints import aur register karo
    from routes.dictionary import dictionary_bp
    from routes.hash_extract import hash_extract_bp
    from routes.brute_force import brute_force_bp
    from routes.strength import strength_bp
    from routes.report import report_bp

    app.register_blueprint(dictionary_bp)
    app.register_blueprint(hash_extract_bp)
    app.register_blueprint(brute_force_bp)
    app.register_blueprint(strength_bp)
    app.register_blueprint(report_bp)

    # Health check route — basic API status endpoint
    @app.route('/api/health', methods=['GET'])
    def health():
        return {"status": "ok", "service": "CipherGuard", "credits": "Engineered & Crafted by Raj"}

    return app


# Main execution block — direct run karne pe server start hoga
if __name__ == '__main__':
    # Banner print karo — har startup pe dikhna chahiye
    print(BANNER)

    # App create karo factory function se
    app = create_app()

    # Port aur debug mode .env se lao
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'

    # Server start karo — sab ready hai
    print(f"{Fore.GREEN}[SERVER] CipherGuard Flask server starting on port {port}...{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[SERVER] Debug mode: {debug}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[SERVER] CORS: Enabled for all origins{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[INFO] API Base URL: http://localhost:{port}/api/{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[INFO] Health Check: http://localhost:{port}/api/health{Style.RESET_ALL}")
    print()

    app.run(host='0.0.0.0', port=port, debug=debug)
