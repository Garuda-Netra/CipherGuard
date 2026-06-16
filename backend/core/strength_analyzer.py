"""
CipherGuard — Password Strength Analyzer Core Logic
Password ki strength check karta hai — entropy, patterns, common passwords sab dekhta hai
Sirf core logic — koi Flask dependency nahi
Engineered & Crafted by Raj
"""

import math
import re
import hashlib
import requests
import os

# Common passwords import karo — duplicate logic se bachne ke liye
from .dict_generator import COMMON_PASSWORDS

def check_pwned_password(password):
    """
    HaveIBeenPwned API (k-Anonymity) se check karta hai ki password breach hua hai ya nahi.
    Returns: (is_pwned: bool, count: int)
    """
    try:
        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix, suffix = sha1_hash[:5], sha1_hash[5:]
        base_url = os.environ.get('HIBP_API_URL', 'https://api.pwnedpasswords.com/range/')
        if not base_url.endswith('/'):
            base_url += '/'
        response = requests.get(f"{base_url}{prefix}", timeout=5)
        if response.status_code != 200:
            return False, 0
        hashes = (line.split(':') for line in response.text.splitlines())
        for h, count in hashes:
            if h == suffix:
                return True, int(count)
        return False, 0
    except Exception:
        return False, 0


def analyze_password(password):
    """
    Ek password ki poori analysis karta hai — strength rating, entropy, checks sab
    
    password: analyze karne wala password string
    Returns: dict with rating, score, entropy, checks, tips
    """
    # Score tracking — har check pass hone pe score badhega
    score = 0
    checks = {}
    tips = []

    # ---- LENGTH CHECK ----
    # Password ki length se score decide karo
    pwd_len = len(password)
    if pwd_len < 6:
        score += 0
        checks['length'] = False
        tips.append("Password bahut chhota hai — kam se kam 8 characters rakhein, ideal hai 12+.")
    elif pwd_len <= 7:
        score += 1
        checks['length'] = False
        tips.append("Password thoda chhota hai — 8+ characters rakhein better security ke liye.")
    elif pwd_len <= 11:
        score += 2
        checks['length'] = True
    elif pwd_len <= 15:
        score += 3
        checks['length'] = True
    else:
        score += 4
        checks['length'] = True

    # ---- UPPERCASE CHECK ----
    # Kya password mein capital letters hain?
    has_upper = bool(re.search(r'[A-Z]', password))
    checks['has_uppercase'] = has_upper
    if has_upper:
        score += 1
    else:
        tips.append("Kam se kam ek uppercase letter (A-Z) add karein.")

    # ---- LOWERCASE CHECK ----
    # Kya chhote letters hain?
    has_lower = bool(re.search(r'[a-z]', password))
    checks['has_lowercase'] = has_lower
    if has_lower:
        score += 1
    else:
        tips.append("Kam se kam ek lowercase letter (a-z) add karein.")

    # ---- DIGITS CHECK ----
    # Kya numbers hain password mein?
    has_digits = bool(re.search(r'[0-9]', password))
    checks['has_digits'] = has_digits
    if has_digits:
        score += 1
    else:
        tips.append("Kam se kam ek number (0-9) add karein.")

    # ---- SYMBOLS CHECK ----
    # Kya special characters hain?
    has_symbols = bool(re.search(r'[^A-Za-z0-9]', password))
    checks['has_symbols'] = has_symbols
    if has_symbols:
        score += 1
    else:
        tips.append("Special symbols jaise @, #, $, ! add karein strength badhane ke liye.")

    # ---- NO REPEATS CHECK ----
    # Kya 3 ya zyada same characters consecutively nahi hain? (e.g., aaa, 111)
    no_repeats = not bool(re.search(r'(.)\1{2,}', password))
    checks['no_repeats'] = no_repeats
    if no_repeats:
        score += 1
    else:
        tips.append("3 ya zyada baar same character repeat mat karein (jaise 'aaa' ya '111').")

    # ---- NO SEQUENTIAL CHECK ----
    # Sequential patterns detect karo — abc, xyz, 123, 321 etc.
    sequential_patterns = [
        'abc', 'bcd', 'cde', 'def', 'efg', 'fgh', 'ghi', 'hij',
        'ijk', 'jkl', 'klm', 'lmn', 'mno', 'nop', 'opq', 'pqr',
        'qrs', 'rst', 'stu', 'tuv', 'uvw', 'vwx', 'wxy', 'xyz',
        '012', '123', '234', '345', '456', '567', '678', '789',
        '987', '876', '765', '654', '543', '432', '321', '210',
        'zyx', 'yxw', 'xwv', 'wvu'
    ]
    has_sequential = any(seq in password.lower() for seq in sequential_patterns)
    no_sequential = not has_sequential
    checks['no_sequential'] = no_sequential
    if no_sequential:
        score += 1
    else:
        tips.append("Sequential patterns (abc, 123, xyz) avoid karein — easily guessable hain.")

    # ---- COMMON PASSWORD CHECK ----
    # Kya yeh koi common password toh nahi?
    not_common = password.lower() not in [p.lower() for p in COMMON_PASSWORDS]
    checks['not_common'] = not_common
    if not_common:
        score += 2  # Agar common nahi hai toh +2 bonus score
    else:
        tips.append("Yeh ek common password hai! Bilkul change karein — hackers sabse pehle yahi try karte hain.")

    # ---- SHANNON ENTROPY CALCULATION ----
    # Information entropy calculate karo — randomness ka measure hai
    entropy = 0.0
    if len(password) > 0:
        chars = set(password)
        entropy = -sum(
            (password.count(c) / len(password)) * math.log2(password.count(c) / len(password))
            for c in chars
        )
        # Per-character entropy ko total length se multiply karo zyada meaningful number ke liye
        entropy = entropy * len(password)

    # ---- RATING MAPPING ----
    # Total score se rating decide karo
    if score >= 8:
        rating = "Fortress"
    elif score >= 6:
        rating = "Strong"
    elif score >= 4:
        rating = "Fair"
    else:
        rating = "Weak"

    # Agar rating already Fortress hai toh congrats message add karo
    if rating == "Fortress":
        tips = ["Excellent! Yeh password bahut strong hai. Isse aise hi rakhein."]

    # Final result dict banao aur return karo
    return {
        "rating": rating,
        "score": score,
        "entropy": round(entropy, 1),
        "checks": checks,
        "tips": tips
    }
