"""
CipherGuard — Standalone CLI Interface
Linux terminal ke liye interactive command-line tool
Saari core logic import hoti hai — yahan duplicate nahi hoti
Engineered & Crafted by Raj
"""

import os
import sys
import getpass

# Windows pe UTF-8 output force karo — Sanskrit text ke liye zaroori hai
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Backend module path add karo — imports sahi se kaam karein
sys.path.insert(0, os.path.dirname(__file__))

# Colorama import karo — CLI output colorful banane ke liye
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
except ImportError:
    print("[ERROR] colorama installed nahi hai. Install karo: pip install colorama")
    sys.exit(1)

# tqdm import karo — progress bars ke liye
try:
    from tqdm import tqdm
except ImportError:
    print(f"{Fore.RED}[ERROR] tqdm installed nahi hai. Install karo: pip install tqdm{Style.RESET_ALL}")
    sys.exit(1)

# .env load karo root level se
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

# Core modules import karo — saari logic yahan se aati hai
from core.dict_generator import generate_wordlist, estimate_wordlist_count
from core.hash_extractor import parse_shadow_file, extract_sam_hashes
from core.brute_engine import wordlist_attack, incremental_attack, calculate_eta
from core.strength_analyzer import analyze_password
from core.report_builder import build_report

# ASCII Banner — har startup pe dikhega
BANNER = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════╗
║{Fore.YELLOW}           C I P H E R G U A R D                 {Fore.CYAN}║
║{Fore.YELLOW}       Password Credential Audit Suite            {Fore.CYAN}║
║{Fore.YELLOW}  "यद्भावं तद्भवति" — As you think, so you become {Fore.CYAN}║
║{Fore.YELLOW}         Engineered & Crafted by Raj              {Fore.CYAN}║
╚══════════════════════════════════════════════════╝{Style.RESET_ALL}
"""

# Session data — CLI session mein results store karo report ke liye
cli_session = {
    'dictionary_results': {},
    'hash_results': [],
    'brute_results': {},
    'strength_results': {}
}

# Mutation options ka mapping — user number select karega
MUTATION_OPTIONS = {
    '1': 'leet',
    '2': 'upper',
    '3': 'title',
    '4': 'numbers',
    '5': 'symbols',
    '6': 'keyboard',
    '7': 'common'
}


def menu_dictionary():
    """
    Menu Option 1 — Dictionary Generator
    User se base words aur mutations leke wordlist generate karta hai
    tqdm progress bar dikhata hai aur file mein save karta hai
    """
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  DICTIONARY GENERATOR{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    # Base words input lo
    base_input = input(f"\n{Fore.YELLOW}  Enter base words (comma-separated): {Style.RESET_ALL}")
    base_words = [w.strip() for w in base_input.split(',') if w.strip()]

    if not base_words:
        print(f"{Fore.RED}  [ERROR] Kam se kam ek base word dena zaroori hai!{Style.RESET_ALL}")
        return

    # Mutations select karo
    print(f"\n{Fore.GREEN}  Select mutations (enter numbers separated by comma):{Style.RESET_ALL}")
    print(f"{Fore.WHITE}   1. Leet Speak       2. UPPERCASE      3. Title Case{Style.RESET_ALL}")
    print(f"{Fore.WHITE}   4. Append Numbers   5. Append Symbols  6. Keyboard Patterns{Style.RESET_ALL}")
    print(f"{Fore.WHITE}   7. Common Bases{Style.RESET_ALL}")

    mut_input = input(f"\n{Fore.YELLOW}  Your choice: {Style.RESET_ALL}")
    selected_mutations = []
    for num in mut_input.split(','):
        num = num.strip()
        if num in MUTATION_OPTIONS:
            selected_mutations.append(MUTATION_OPTIONS[num])

    # Estimated count dikhao
    estimated = estimate_wordlist_count(base_words, selected_mutations)
    print(f"\n{Fore.CYAN}  [INFO] Estimated words: ~{estimated}{Style.RESET_ALL}")

    # Generator start karo tqdm progress bar ke saath
    words = []
    generator = generate_wordlist(base_words, selected_mutations)
    
    print()
    for word in tqdm(generator, desc=f"  {Fore.GREEN}Generating{Style.RESET_ALL}", unit="word", colour="green", total=estimated):
        words.append(word)

    # Pehle 20 words preview dikhao
    print(f"\n{Fore.CYAN}  ── Preview (first 20 words) ──{Style.RESET_ALL}")
    for i, word in enumerate(words[:20]):
        print(f"  {Fore.WHITE}{i+1:4d}. {word}{Style.RESET_ALL}")
    if len(words) > 20:
        print(f"  {Fore.YELLOW}  ... and {len(words) - 20} more words{Style.RESET_ALL}")

    # File mein save karo
    output_path = os.environ.get('WORDLIST_OUTPUT_PATH', 'backend/output/wordlist.txt')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(words))

    print(f"\n{Fore.GREEN}  [SUCCESS] Total words generated: {len(words)}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}  [SAVED] Wordlist saved to: {output_path}{Style.RESET_ALL}")

    # Session mein store karo report ke liye
    cli_session['dictionary_results'] = {
        'total_words': len(words),
        'mutations_used': selected_mutations,
        'file_path': output_path
    }


def menu_hash_extractor():
    """
    Menu Option 2 — Hash Extractor
    Linux shadow ya Windows SAM+SYSTEM files se hashes extract karta hai
    Results colorama formatted table mein dikhata hai
    """
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  HASH EXTRACTOR{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    # Mode select karo
    print(f"\n{Fore.GREEN}  Select mode:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}   1. Linux Shadow File{Style.RESET_ALL}")
    print(f"{Fore.WHITE}   2. Windows SAM + SYSTEM{Style.RESET_ALL}")

    choice = input(f"\n{Fore.YELLOW}  Choice: {Style.RESET_ALL}").strip()

    results = []

    if choice == '1':
        # Linux mode — shadow file path lo
        shadow_path = input(f"{Fore.YELLOW}  Enter shadow file path: {Style.RESET_ALL}").strip()

        if not os.path.exists(shadow_path):
            print(f"{Fore.RED}  [ERROR] File nahi mili: {shadow_path}{Style.RESET_ALL}")
            return

        # File padho aur parse karo
        with open(shadow_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        results = parse_shadow_file(content)

    elif choice == '2':
        # Windows mode — SAM aur SYSTEM paths lo
        sam_path = input(f"{Fore.YELLOW}  Enter SAM file path: {Style.RESET_ALL}").strip()
        sys_path = input(f"{Fore.YELLOW}  Enter SYSTEM file path: {Style.RESET_ALL}").strip()

        if not os.path.exists(sam_path):
            print(f"{Fore.RED}  [ERROR] SAM file nahi mili: {sam_path}{Style.RESET_ALL}")
            return
        if not os.path.exists(sys_path):
            print(f"{Fore.RED}  [ERROR] SYSTEM file nahi mili: {sys_path}{Style.RESET_ALL}")
            return

        results = extract_sam_hashes(sam_path, sys_path)

        # Error check karo
        if isinstance(results, dict) and 'error' in results:
            print(f"{Fore.RED}  [ERROR] {results['error']}{Style.RESET_ALL}")
            return
    else:
        print(f"{Fore.RED}  [ERROR] Invalid choice!{Style.RESET_ALL}")
        return

    # Results table print karo — colorama formatting ke saath
    if results:
        print(f"\n{Fore.CYAN}  {'─'*60}{Style.RESET_ALL}")
        print(f"  {Fore.CYAN}{'Username':<15}{Fore.YELLOW}{'Algorithm':<12}{Fore.WHITE}{'Hash Value':<40}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  {'─'*60}{Style.RESET_ALL}")

        for r in results:
            username = r.get('username', 'N/A')
            algo = r.get('algorithm', 'N/A')
            hash_val = r.get('hash', 'N/A')
            # Hash ko 40 chars tak truncate karo display ke liye
            hash_display = hash_val[:40] + '...' if len(hash_val) > 40 else hash_val
            print(f"  {Fore.CYAN}{username:<15}{Fore.YELLOW}{algo:<12}{Fore.WHITE}{hash_display}{Style.RESET_ALL}")

        print(f"{Fore.CYAN}  {'─'*60}{Style.RESET_ALL}")
        print(f"\n{Fore.GREEN}  [SUCCESS] {len(results)} hashes extracted.{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}  [INFO] Koi valid hash nahi mila.{Style.RESET_ALL}")

    # Session mein store karo
    cli_session['hash_results'] = results


def menu_brute_force():
    """
    Menu Option 3 — Brute Force Engine
    Hash cracking — wordlist ya incremental mode mein
    tqdm progress bar aur live speed display ke saath
    ETHICAL USE ONLY — CONTROLLED LAB ENVIRONMENT ONLY
    """
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  BRUTE FORCE ENGINE{Style.RESET_ALL}")
    print(f"{Fore.RED}  ⚠ ETHICAL USE ONLY — LAB ENVIRONMENT ONLY{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    # Target hash input lo
    target_hash = input(f"\n{Fore.YELLOW}  Enter target hash: {Style.RESET_ALL}").strip()
    if not target_hash:
        print(f"{Fore.RED}  [ERROR] Hash dena zaroori hai!{Style.RESET_ALL}")
        return

    # Hash type select karo
    print(f"\n{Fore.GREEN}  Select hash type:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}   1. MD5     2. SHA-1     3. SHA-256{Style.RESET_ALL}")
    print(f"{Fore.WHITE}   4. SHA-512  5. NTLM{Style.RESET_ALL}")

    type_map = {'1': 'md5', '2': 'sha1', '3': 'sha256', '4': 'sha512', '5': 'ntlm'}
    type_choice = input(f"{Fore.YELLOW}  Choice: {Style.RESET_ALL}").strip()
    hash_type = type_map.get(type_choice, 'md5')

    # Attack mode select karo
    print(f"\n{Fore.GREEN}  Select attack mode:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}   1. Wordlist Attack{Style.RESET_ALL}")
    print(f"{Fore.WHITE}   2. Incremental Attack{Style.RESET_ALL}")

    mode_choice = input(f"{Fore.YELLOW}  Choice: {Style.RESET_ALL}").strip()

    found_password = None

    if mode_choice == '1':
        # Wordlist mode — file path lo
        wl_path = input(f"{Fore.YELLOW}  Enter wordlist file path: {Style.RESET_ALL}").strip()
        if not wl_path:
            wl_path = os.environ.get('WORDLIST_OUTPUT_PATH', 'backend/output/wordlist.txt')

        if not os.path.exists(wl_path):
            print(f"{Fore.RED}  [ERROR] Wordlist file nahi mili: {wl_path}{Style.RESET_ALL}")
            return

        # Total lines count karo progress bar ke liye
        with open(wl_path, 'r', encoding='utf-8', errors='ignore') as f:
            total_lines = sum(1 for _ in f)

        print(f"\n{Fore.CYAN}  [INFO] Wordlist size: {total_lines} words{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  [INFO] Starting wordlist attack...{Style.RESET_ALL}\n")

        # Attack start karo tqdm ke saath
        pbar = tqdm(total=total_lines, desc=f"  {Fore.GREEN}Cracking{Style.RESET_ALL}", unit="hash", colour="green")

        for progress in wordlist_attack(target_hash, hash_type, wl_path):
            if progress.get('found'):
                found_password = progress['password']
                pbar.update(progress['count'] - pbar.n)
                pbar.close()

                # SUCCESS — password box mein dikhao
                print(f"\n{Fore.GREEN}  ╔══════════════════════════════════════╗{Style.RESET_ALL}")
                print(f"{Fore.GREEN}  ║  PASSWORD FOUND!                     ║{Style.RESET_ALL}")
                print(f"{Fore.GREEN}  ║  {Style.BRIGHT}{found_password:<37}║{Style.RESET_ALL}")
                print(f"{Fore.GREEN}  ║  Attempts: {progress['count']:<26}║{Style.RESET_ALL}")
                time_str = f"{progress['time_taken']:.2f}s"
                time_pad = ' ' * (29 - len(time_str))
                print(f"{Fore.GREEN}  ║  Time: {time_str}{time_pad}║{Style.RESET_ALL}")
                print(f"{Fore.GREEN}  ╚══════════════════════════════════════╝{Style.RESET_ALL}")

                cli_session['brute_results'] = {
                    'found': True, 'password': found_password,
                    'count': progress['count'], 'time_taken': progress['time_taken'],
                    'target_hash': target_hash, 'method': 'wordlist'
                }
                return

            elif progress.get('exhausted'):
                pbar.update(progress['count'] - pbar.n)
                pbar.close()
                print(f"\n{Fore.RED}  [FAILED] Password nahi mila — wordlist exhaust ho gayi.{Style.RESET_ALL}")
                print(f"{Fore.RED}  Attempts: {progress['count']} | Time: {progress.get('time_taken', 0):.2f}s{Style.RESET_ALL}")

                cli_session['brute_results'] = {
                    'found': False, 'count': progress['count'],
                    'time_taken': progress.get('time_taken', 0),
                    'target_hash': target_hash, 'method': 'wordlist'
                }
                return
            else:
                # Progress update — bar advance karo
                new_count = progress.get('count', 0)
                pbar.update(new_count - pbar.n)
                pbar.set_postfix({
                    'speed': f"{progress.get('per_second', 0):.0f}/s",
                    'trying': progress.get('attempt', '')[:20]
                })

        pbar.close()

    elif mode_choice == '2':
        # Incremental mode — max length .env se lao
        max_len = int(os.environ.get('MAX_BRUTE_FORCE_LENGTH', '4'))
        print(f"\n{Fore.CYAN}  [INFO] Incremental attack — max length: {max_len}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  [INFO] Character set: a-z, A-Z, 0-9, symbols{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  [WARNING] Yeh bahut time le sakta hai!{Style.RESET_ALL}\n")

        # Approximate total calculate karo
        total_approx = sum(95 ** l for l in range(1, max_len + 1))
        pbar = tqdm(total=total_approx, desc=f"  {Fore.GREEN}Cracking{Style.RESET_ALL}", unit="hash", colour="green")

        for progress in incremental_attack(target_hash, hash_type, max_len):
            if progress.get('found'):
                found_password = progress['password']
                pbar.close()

                print(f"\n{Fore.GREEN}  ╔══════════════════════════════════════╗{Style.RESET_ALL}")
                print(f"{Fore.GREEN}  ║  PASSWORD FOUND!                     ║{Style.RESET_ALL}")
                print(f"{Fore.GREEN}  ║  {Style.BRIGHT}{found_password:<37}║{Style.RESET_ALL}")
                print(f"{Fore.GREEN}  ║  Attempts: {progress['count']:<26}║{Style.RESET_ALL}")
                time_str = f"{progress['time_taken']:.2f}s"
                time_pad = ' ' * (29 - len(time_str))
                print(f"{Fore.GREEN}  ║  Time: {time_str}{time_pad}║{Style.RESET_ALL}")
                print(f"{Fore.GREEN}  ╚══════════════════════════════════════╝{Style.RESET_ALL}")

                cli_session['brute_results'] = {
                    'found': True, 'password': found_password,
                    'count': progress['count'], 'time_taken': progress['time_taken'],
                    'target_hash': target_hash, 'method': 'incremental'
                }
                return

            elif progress.get('exhausted'):
                pbar.close()
                print(f"\n{Fore.RED}  [FAILED] Password nahi mila — keyspace exhaust ho gayi.{Style.RESET_ALL}")
                print(f"{Fore.RED}  Attempts: {progress['count']} | Time: {progress.get('time_taken', 0):.2f}s{Style.RESET_ALL}")

                cli_session['brute_results'] = {
                    'found': False, 'count': progress['count'],
                    'time_taken': progress.get('time_taken', 0),
                    'target_hash': target_hash, 'method': 'incremental'
                }
                return
            else:
                new_count = progress.get('count', 0)
                pbar.update(new_count - pbar.n)
                pbar.set_postfix({
                    'speed': f"{progress.get('per_second', 0):.0f}/s",
                    'trying': progress.get('attempt', '')[:15]
                })

        pbar.close()
    else:
        print(f"{Fore.RED}  [ERROR] Invalid mode choice!{Style.RESET_ALL}")


def menu_strength():
    """
    Menu Option 4 — Password Strength Analyzer
    getpass se secure input leta hai aur detailed analysis dikhata hai
    Color coded rating aur tick/cross marks ke saath
    """
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  PASSWORD STRENGTH ANALYZER{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    # Secure password input — screen pe nahi dikhega
    password = getpass.getpass(f"\n{Fore.YELLOW}  Enter password (hidden): {Style.RESET_ALL}")

    if not password:
        print(f"{Fore.RED}  [ERROR] Password dena zaroori hai!{Style.RESET_ALL}")
        return

    # Core analyzer function call karo
    result = analyze_password(password)

    # Rating color decide karo
    rating = result['rating']
    rating_colors = {
        'Weak': Fore.RED,
        'Fair': Fore.YELLOW,
        'Strong': Fore.GREEN,
        'Fortress': Fore.CYAN
    }
    rating_color = rating_colors.get(rating, Fore.WHITE)

    # Rating dikhao
    print(f"\n{Fore.CYAN}  ── Analysis Results ──{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}Rating:  {rating_color}{Style.BRIGHT}{rating}{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}Score:   {Fore.YELLOW}{result['score']}/12{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}Entropy: {Fore.CYAN}{result['entropy']} bits{Style.RESET_ALL}")

    # Checks table — tick ya cross ke saath
    print(f"\n{Fore.CYAN}  ── Security Checks ──{Style.RESET_ALL}")
    check_labels = {
        'length': 'Minimum Length (8+)',
        'has_uppercase': 'Uppercase Letters',
        'has_lowercase': 'Lowercase Letters',
        'has_digits': 'Numbers',
        'has_symbols': 'Special Symbols',
        'no_repeats': 'No Repeated Chars',
        'no_sequential': 'No Sequential Patterns',
        'not_common': 'Not Common Password'
    }

    for key, label in check_labels.items():
        passed = result['checks'].get(key, False)
        if passed:
            print(f"  {Fore.GREEN}  ✓ {label}{Style.RESET_ALL}")
        else:
            print(f"  {Fore.RED}  ✗ {label}{Style.RESET_ALL}")

    # Improvement tips dikhao
    if result['tips']:
        print(f"\n{Fore.CYAN}  ── Improvement Tips ──{Style.RESET_ALL}")
        for tip in result['tips']:
            print(f"  {Fore.YELLOW}  → {tip}{Style.RESET_ALL}")

    # Session mein store karo
    cli_session['strength_results'] = result


def menu_report():
    """
    Menu Option 5 — Report Generator
    CLI session ke saare results collect karke formatted report print karta hai
    File mein bhi save karta hai
    """
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  SECURITY AUDIT REPORT{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    # Report build karo session data se
    report = build_report(cli_session)

    # Report sections print karo — colorama formatting ke saath
    print(f"\n{Fore.CYAN}  ── Executive Summary ──{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}{report['executive_summary']}{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}  ── Dictionary Results ──{Style.RESET_ALL}")
    dr = report['dictionary_results']
    print(f"  {Fore.WHITE}Total Words: {Fore.GREEN}{dr.get('total_words', 0)}{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}Mutations: {Fore.YELLOW}{', '.join(dr.get('mutations_used', []))}{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}File: {Fore.CYAN}{dr.get('file_path', 'N/A')}{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}  ── Hash Findings ──{Style.RESET_ALL}")
    for h in report.get('hash_findings', []):
        print(f"  {Fore.CYAN}{h.get('username', 'N/A'):<15}{Fore.YELLOW}{h.get('algorithm', 'N/A'):<12}{Fore.WHITE}{h.get('hash', 'N/A')[:40]}{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}  ── Brute Force Results ──{Style.RESET_ALL}")
    br = report['brute_force_results']
    print(f"  {Fore.WHITE}Found: {Fore.GREEN if br.get('found') else Fore.RED}{br.get('found', False)}{Style.RESET_ALL}")
    if br.get('found'):
        print(f"  {Fore.WHITE}Password: {Fore.GREEN}{Style.BRIGHT}{br.get('password', 'N/A')}{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}Attempts: {Fore.YELLOW}{br.get('attempts', 0)}{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}Time: {Fore.YELLOW}{br.get('time_taken', 0)}s{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}  ── Strength Summary ──{Style.RESET_ALL}")
    for s in report.get('strength_summary', []):
        print(f"  {Fore.WHITE}Rating: {Fore.YELLOW}{s.get('rating', 'N/A')} | Entropy: {s.get('entropy', 0)} | Score: {s.get('score', 0)}{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}  ── Risk Matrix ──{Style.RESET_ALL}")
    for r in report.get('risk_matrix', []):
        risk_color = Fore.RED if r.get('risk_level') == 'CRITICAL' else Fore.YELLOW if r.get('risk_level') == 'HIGH' else Fore.GREEN
        print(f"  {Fore.WHITE}{r.get('password_sample', 'N/A'):<15}{Fore.YELLOW}{r.get('rating', 'N/A'):<10}{Fore.CYAN}{r.get('estimated_crack_time', 'N/A'):<25}{risk_color}{r.get('risk_level', 'N/A')}{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}  ── Recommendations ──{Style.RESET_ALL}")
    for rec in report.get('recommendations', []):
        print(f"  {Fore.YELLOW}  • {rec}{Style.RESET_ALL}")

    # Credits dikhao
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  {report.get('credits', 'Engineered & Crafted by Raj')}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

    # File mein save karo
    output_path = os.environ.get('REPORT_OUTPUT_PATH', 'backend/output/report.txt')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("CIPHERGUARD — SECURITY AUDIT REPORT\n")
        f.write("=" * 50 + "\n")
        f.write(f"\nExecutive Summary:\n{report['executive_summary']}\n")
        f.write(f"\nDictionary Results:\nTotal: {dr.get('total_words', 0)}\n")
        f.write(f"\nHash Findings:\n")
        for h in report.get('hash_findings', []):
            f.write(f"  {h.get('username', 'N/A')} | {h.get('algorithm', 'N/A')} | {h.get('hash', 'N/A')[:50]}\n")
        f.write(f"\nBrute Force:\nFound: {br.get('found', False)}\n")
        f.write(f"\nRecommendations:\n")
        for rec in report.get('recommendations', []):
            f.write(f"  • {rec}\n")
        f.write(f"\n{'='*50}\n{report.get('credits', '')}\n")

    print(f"\n{Fore.GREEN}  [SAVED] Report saved to: {output_path}{Style.RESET_ALL}")


def main():
    """
    Main CLI loop — menu dikhata hai aur user ka choice process karta hai
    Jab tak user exit nahi karta, loop chalti rahegi
    """
    # Banner print karo — har startup pe
    print(BANNER)

    # Menu loop — infinite jab tak user 0 nahi daale
    while True:
        print(f"{Fore.GREEN}\n  [1] Dictionary Generator{Style.RESET_ALL}")
        print(f"{Fore.GREEN}  [2] Hash Extractor{Style.RESET_ALL}")
        print(f"{Fore.GREEN}  [3] Brute Force Engine{Style.RESET_ALL}")
        print(f"{Fore.GREEN}  [4] Password Strength Analyzer{Style.RESET_ALL}")
        print(f"{Fore.GREEN}  [5] Generate Report{Style.RESET_ALL}")
        print(f"{Fore.GREEN}  [0] Exit{Style.RESET_ALL}")

        choice = input(f"{Fore.YELLOW}\n  Enter your choice: {Style.RESET_ALL}").strip()

        if choice == '1':
            menu_dictionary()
        elif choice == '2':
            menu_hash_extractor()
        elif choice == '3':
            menu_brute_force()
        elif choice == '4':
            menu_strength()
        elif choice == '5':
            menu_report()
        elif choice == '0':
            print(f"\n{Fore.YELLOW}  Goodbye! Engineered & Crafted by Raj{Style.RESET_ALL}")
            print(f"{Fore.CYAN}  यद्भावं तद्भवति — As you think, so you become.{Style.RESET_ALL}\n")
            sys.exit(0)
        else:
            print(f"{Fore.RED}  [ERROR] Invalid choice — 0-5 mein se select karo.{Style.RESET_ALL}")


# Direct run karne pe main() call hoga
if __name__ == '__main__':
    main()
