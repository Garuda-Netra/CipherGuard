"""
CipherGuard — Dictionary Generator Core Logic
Yeh module wordlist generate karta hai different mutations ke saath
Sirf core logic hai yahan — koi Flask import nahi
Engineered & Crafted by Raj
"""


# Common passwords ki list — duniya bhar mein sabse zyada use hone wale passwords
COMMON_PASSWORDS = [
    "password", "admin", "letmein", "welcome", "monkey", "dragon",
    "master", "sunshine", "princess", "football", "abc123", "111111",
    "iloveyou", "trustno1", "superman", "batman", "shadow", "michael",
    "jessica", "passw0rd", "hello123", "changeme", "login", "root",
    "test", "guest", "default", "server", "database", "backup"
]

# Keyboard patterns — common keyboard sequences jo log password mein use karte hain
KEYBOARD_PATTERNS = ["qwerty", "123456", "asdfgh", "zxcvbn", "1q2w3e", "qwerty123"]

# Leet speak mapping — characters ko numbers se replace karne ka tarika
LEET_MAP = {
    'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7'
}

# Symbols jo password ke end mein lagaye jaate hain
APPEND_SYMBOLS = ['@', '#', '!', '$', '%']


def _apply_leet(word):
    """
    Ek word ka leet speak version banata hai
    Har replaceable character ko uske leet equivalent se replace karta hai
    """
    result = list(word.lower())
    for i, char in enumerate(result):
        if char in LEET_MAP:
            result[i] = LEET_MAP[char]
    return ''.join(result)


def generate_wordlist(base_words, mutations):
    """
    Main wordlist generator function — yeh Python generator hai jo ek ek word yield karta hai
    base_words: list of strings (user ke diye hue base words)
    mutations: list of strings jaise ['leet', 'upper', 'title', 'numbers', 'symbols', 'keyboard', 'common']
    Duplicate words ko skip karta hai seen set se
    """
    # Seen set — duplicate words track karne ke liye
    seen = set()

    # Pehle base words ko hi yield karo agar woh pehle se nahi diye gaye
    all_bases = list(base_words)

    # Agar 'common' mutation selected hai toh common passwords bhi base mein add karo
    if 'common' in mutations:
        all_bases.extend(COMMON_PASSWORDS)

    # Agar 'keyboard' mutation hai toh keyboard patterns bhi add karo
    if 'keyboard' in mutations:
        all_bases.extend(KEYBOARD_PATTERNS)

    # Har base word ke liye mutations apply karo
    for word in all_bases:
        word = word.strip()
        if not word:
            continue

        # Original word pehle yield karo
        if word not in seen:
            seen.add(word)
            yield word

        # Lowercase version bhi try karo
        lower_word = word.lower()
        if lower_word not in seen:
            seen.add(lower_word)
            yield lower_word

        # UPPERCASE mutation — poora word uppercase mein
        if 'upper' in mutations:
            upper_word = word.upper()
            if upper_word not in seen:
                seen.add(upper_word)
                yield upper_word

        # Title Case mutation — pehla letter capital
        if 'title' in mutations:
            title_word = word.capitalize()
            if title_word not in seen:
                seen.add(title_word)
                yield title_word

        # Leet Speak mutation — special character replacement
        if 'leet' in mutations:
            leet_word = _apply_leet(word)
            if leet_word not in seen:
                seen.add(leet_word)
                yield leet_word

            # Leet ka uppercase version bhi
            leet_upper = leet_word.upper()
            if leet_upper not in seen:
                seen.add(leet_upper)
                yield leet_upper

        # Numbers mutation — 0 se 99 tak aur years 2000-2025
        if 'numbers' in mutations:
            for num in range(100):
                num_word = f"{word}{num}"
                if num_word not in seen:
                    seen.add(num_word)
                    yield num_word

            # Year append karo — 2000 se 2025 tak
            for year in range(2000, 2026):
                year_word = f"{word}{year}"
                if year_word not in seen:
                    seen.add(year_word)
                    yield year_word

        # Symbols mutation — special characters append karo
        if 'symbols' in mutations:
            for sym in APPEND_SYMBOLS:
                sym_word = f"{word}{sym}"
                if sym_word not in seen:
                    seen.add(sym_word)
                    yield sym_word

                # Symbol ke saath numbers bhi combine karo — zyada permutations
                if 'numbers' in mutations:
                    for num in [1, 123, 2024, 2025]:
                        combo = f"{word}{sym}{num}"
                        if combo not in seen:
                            seen.add(combo)
                            yield combo


def estimate_wordlist_count(base_words, mutations):
    """
    Generation shuru hone se pehle estimated word count return karta hai
    Exact nahi hoga kyunki deduplication runtime pe hoti hai, lekin rough idea deta hai
    """
    # Base count — har word ka ek original entry
    base_count = len(base_words)
    multiplier = 1  # Original word toh hamesha hoga

    # Har mutation ke liye multiplier badhao
    if 'upper' in mutations:
        multiplier += 1
    if 'title' in mutations:
        multiplier += 1
    if 'leet' in mutations:
        multiplier += 2  # Leet + leet upper
    if 'numbers' in mutations:
        multiplier += 126  # 0-99 (100) + 2000-2025 (26)
    if 'symbols' in mutations:
        multiplier += len(APPEND_SYMBOLS)  # 5 symbols
        if 'numbers' in mutations:
            multiplier += len(APPEND_SYMBOLS) * 4  # 4 combos per symbol
    if 'common' in mutations:
        base_count += len(COMMON_PASSWORDS)
    if 'keyboard' in mutations:
        base_count += len(KEYBOARD_PATTERNS)

    # Lowercase version bhi count karo
    multiplier += 1

    return base_count * multiplier
