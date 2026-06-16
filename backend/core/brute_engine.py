"""
CipherGuard — Brute Force Engine Core Logic
Hash cracking ke liye wordlist aur incremental attack modes
ETHICAL USE ONLY — CONTROLLED LAB ENVIRONMENT ONLY
Engineered & Crafted by Raj
"""

import hashlib
import itertools
import string
import struct
import time


def _md4_pure(data):
    """
    Pure-Python MD4 implementation — fallback jab OpenSSL md4 support nahi karta
    Naye Python (3.12+) aur OpenSSL 3.x mein md4 deprecated/removed hai
    Yeh function raw bytes leke hex digest string return karta hai
    """
    # MD4 constants aur helper functions
    def _left_rotate(n, b):
        return ((n << b) | (n >> (32 - b))) & 0xFFFFFFFF

    def _f(x, y, z):
        return (x & y) | (~x & z)

    def _g(x, y, z):
        return (x & y) | (x & z) | (y & z)

    def _h(x, y, z):
        return x ^ y ^ z

    # Pre-processing: message padding
    msg = bytearray(data)
    msg_len = len(data)
    msg.append(0x80)
    while len(msg) % 64 != 56:
        msg.append(0)
    msg += struct.pack('<Q', msg_len * 8)

    # Initial hash values
    a0, b0, c0, d0 = 0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476

    # Har 512-bit (64 byte) block process karo
    for i in range(0, len(msg), 64):
        block = msg[i:i+64]
        x = list(struct.unpack('<16I', block))

        a, b, c, d = a0, b0, c0, d0

        # Round 1 — F function ke saath
        for k in [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]:
            if k % 4 == 0:
                a = _left_rotate((a + _f(b, c, d) + x[k]) & 0xFFFFFFFF, 3)
            elif k % 4 == 1:
                d = _left_rotate((d + _f(a, b, c) + x[k]) & 0xFFFFFFFF, 7)
            elif k % 4 == 2:
                c = _left_rotate((c + _f(d, a, b) + x[k]) & 0xFFFFFFFF, 11)
            else:
                b = _left_rotate((b + _f(c, d, a) + x[k]) & 0xFFFFFFFF, 19)

        # Round 2 — G function ke saath
        for k in [0,4,8,12,1,5,9,13,2,6,10,14,3,7,11,15]:
            if [0,4,8,12,1,5,9,13,2,6,10,14,3,7,11,15].index(k) % 4 == 0:
                a = _left_rotate((a + _g(b, c, d) + x[k] + 0x5A827999) & 0xFFFFFFFF, 3)
            elif [0,4,8,12,1,5,9,13,2,6,10,14,3,7,11,15].index(k) % 4 == 1:
                d = _left_rotate((d + _g(a, b, c) + x[k] + 0x5A827999) & 0xFFFFFFFF, 5)
            elif [0,4,8,12,1,5,9,13,2,6,10,14,3,7,11,15].index(k) % 4 == 2:
                c = _left_rotate((c + _g(d, a, b) + x[k] + 0x5A827999) & 0xFFFFFFFF, 9)
            else:
                b = _left_rotate((b + _g(c, d, a) + x[k] + 0x5A827999) & 0xFFFFFFFF, 13)

        # Round 3 — H function ke saath
        for k in [0,8,4,12,2,10,6,14,1,9,5,13,3,11,7,15]:
            if [0,8,4,12,2,10,6,14,1,9,5,13,3,11,7,15].index(k) % 4 == 0:
                a = _left_rotate((a + _h(b, c, d) + x[k] + 0x6ED9EBA1) & 0xFFFFFFFF, 3)
            elif [0,8,4,12,2,10,6,14,1,9,5,13,3,11,7,15].index(k) % 4 == 1:
                d = _left_rotate((d + _h(a, b, c) + x[k] + 0x6ED9EBA1) & 0xFFFFFFFF, 9)
            elif [0,8,4,12,2,10,6,14,1,9,5,13,3,11,7,15].index(k) % 4 == 2:
                c = _left_rotate((c + _h(d, a, b) + x[k] + 0x6ED9EBA1) & 0xFFFFFFFF, 11)
            else:
                b = _left_rotate((b + _h(c, d, a) + x[k] + 0x6ED9EBA1) & 0xFFFFFFFF, 15)

        a0 = (a0 + a) & 0xFFFFFFFF
        b0 = (b0 + b) & 0xFFFFFFFF
        c0 = (c0 + c) & 0xFFFFFFFF
        d0 = (d0 + d) & 0xFFFFFFFF

    return struct.pack('<4I', a0, b0, c0, d0).hex()


def _compute_ntlm(candidate):
    """
    NTLM hash calculate karta hai — pehle hashlib.md4 try karta hai,
    agar nahi chala toh pure-Python MD4 fallback use karta hai
    Naye Python versions mein OpenSSL md4 support nahi karta
    """
    data = candidate.encode('utf-16-le')
    try:
        # Pehle native hashlib try karo — purane Python/OpenSSL mein kaam karega
        return hashlib.new('md4', data).hexdigest()
    except (ValueError, TypeError):
        # Agar md4 supported nahi hai toh pure-Python fallback use karo
        return _md4_pure(data)


def hash_candidate(candidate, hash_type):
    """
    Ek candidate password ko specified hash type mein convert karta hai
    Supported types: md5, sha1, sha256, sha512, ntlm
    
    candidate: plaintext password string
    hash_type: hash algorithm ka naam (lowercase)
    Returns: hex digest string
    """
    hash_type = hash_type.lower()

    if hash_type == 'md5':
        return hashlib.md5(candidate.encode('utf-8')).hexdigest()
    elif hash_type == 'sha1':
        return hashlib.sha1(candidate.encode('utf-8')).hexdigest()
    elif hash_type == 'sha256':
        return hashlib.sha256(candidate.encode('utf-8')).hexdigest()
    elif hash_type == 'sha512':
        return hashlib.sha512(candidate.encode('utf-8')).hexdigest()
    elif hash_type == 'ntlm':
        # NTLM hashing — MD4 with UTF-16LE, fallback included
        return _compute_ntlm(candidate)
    else:
        # Agar unknown hash type hai toh md5 fallback karo
        return hashlib.md5(candidate.encode('utf-8')).hexdigest()


def wordlist_attack(target_hash, hash_type, wordlist_path):
    """
    Wordlist based dictionary attack — file mein se ek ek word try karta hai
    ETHICAL USE ONLY — CONTROLLED LAB ENVIRONMENT ONLY
    
    target_hash: jo hash crack karna hai
    hash_type: hash algorithm (md5, sha1, sha256, sha512, ntlm)
    wordlist_path: wordlist file ka path
    
    Yields progress dicts har 100 attempts pe aur final result
    """
    # Target hash ko lowercase mein normalize karo — comparison ke liye
    target_hash = target_hash.strip().lower()
    
    # Tracking variables initialize karo
    attempt_count = 0
    start_time = time.time()

    try:
        # Wordlist file open karo — line by line padho memory bachane ke liye
        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                candidate = line.strip()
                if not candidate:
                    continue

                attempt_count += 1

                # Candidate ka hash calculate karo
                candidate_hash = hash_candidate(candidate, hash_type)

                # Target se compare karo — case insensitive
                if candidate_hash.lower() == target_hash:
                    # PASSWORD MIL GAYA! Celebrate karo!
                    elapsed = time.time() - start_time
                    yield {
                        "found": True,
                        "password": candidate,
                        "count": attempt_count,
                        "time_taken": round(elapsed, 2),
                        "per_second": round(attempt_count / max(elapsed, 0.001), 1)
                    }
                    return

                # Har 100 attempts pe progress update yield karo
                if attempt_count % 100 == 0:
                    elapsed = time.time() - start_time
                    per_second = attempt_count / max(elapsed, 0.001)
                    yield {
                        "attempt": candidate,
                        "count": attempt_count,
                        "per_second": round(per_second, 1),
                        "found": False,
                        "password": None
                    }

    except FileNotFoundError:
        # File nahi mili — error yield karo
        yield {
            "found": False,
            "exhausted": True,
            "count": attempt_count,
            "time_taken": 0,
            "error": f"Wordlist file nahi mili: {wordlist_path}"
        }
        return

    # Saari words try ho gayi lekin password nahi mila
    elapsed = time.time() - start_time
    yield {
        "found": False,
        "exhausted": True,
        "count": attempt_count,
        "time_taken": round(elapsed, 2)
    }


def incremental_attack(target_hash, hash_type, max_length=4):
    """
    Incremental brute force attack — systematically har possible combination try karta hai
    Character sets progressively add hote hain — pehle lowercase, phir uppercase, digits, symbols
    ETHICAL USE ONLY — CONTROLLED LAB ENVIRONMENT ONLY
    
    target_hash: jo hash crack karna hai
    hash_type: hash algorithm
    max_length: maximum password length try karna hai (default 4, zyada dena risky hai time-wise)
    
    Yields progress dicts har 100 attempts pe aur final result
    """
    # Target hash normalize karo
    target_hash = target_hash.strip().lower()
    
    # Character sets — ek ek karke add honge
    charsets = [
        string.ascii_lowercase,                                          # a-z
        string.ascii_lowercase + string.ascii_uppercase,                 # a-z + A-Z
        string.ascii_lowercase + string.ascii_uppercase + string.digits, # + 0-9
        string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation  # + symbols
    ]

    attempt_count = 0
    start_time = time.time()

    # Har length ke liye try karo — 1 se max_length tak
    for length in range(1, max_length + 1):
        # Har character set ke liye combinations generate karo
        for charset in charsets:
            for combo in itertools.product(charset, repeat=length):
                candidate = ''.join(combo)
                attempt_count += 1

                # Candidate ka hash banao aur compare karo
                candidate_hash = hash_candidate(candidate, hash_type)

                if candidate_hash.lower() == target_hash:
                    # MIL GAYA! Password found!
                    elapsed = time.time() - start_time
                    yield {
                        "found": True,
                        "password": candidate,
                        "count": attempt_count,
                        "time_taken": round(elapsed, 2),
                        "per_second": round(attempt_count / max(elapsed, 0.001), 1)
                    }
                    return

                # Har 100 attempts pe progress report karo
                if attempt_count % 100 == 0:
                    elapsed = time.time() - start_time
                    per_second = attempt_count / max(elapsed, 0.001)
                    yield {
                        "attempt": candidate,
                        "count": attempt_count,
                        "per_second": round(per_second, 1),
                        "found": False,
                        "password": None
                    }

    # Saare combinations exhaust ho gaye — password nahi mila
    elapsed = time.time() - start_time
    yield {
        "found": False,
        "exhausted": True,
        "count": attempt_count,
        "time_taken": round(elapsed, 2)
    }


def calculate_eta(attempts_done, per_second, total_estimated):
    """
    Estimated Time of Arrival calculate karta hai
    Baaki kitna time lagega yeh batata hai HH:MM:SS format mein
    
    attempts_done: ab tak kitne attempts ho chuke hain
    per_second: attempts per second speed
    total_estimated: total estimated attempts
    Returns: formatted string "HH:MM:SS" ya "Unknown"
    """
    # Agar speed zero hai toh ETA calculate nahi ho sakta
    if per_second <= 0:
        return "Unknown"

    # Remaining attempts nikalo
    remaining = max(0, total_estimated - attempts_done)
    
    # Remaining time seconds mein
    remaining_seconds = remaining / per_second

    # HH:MM:SS format mein convert karo
    hours = int(remaining_seconds // 3600)
    minutes = int((remaining_seconds % 3600) // 60)
    seconds = int(remaining_seconds % 60)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
