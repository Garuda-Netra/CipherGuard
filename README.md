# CipherGuard — Password Credential Audit Suite

> *"यद्भावं तद्भवति — As you think, so you become. Weak passwords fall, strong ones endure."*

**Engineered & Crafted by Raj**

---

## Welcome to the Fortress

Welcome to **CipherGuard**, a powerful, medieval-themed password security audit toolkit built for ethical hackers, security students, and penetration testers. 

Instead of jumping between half a dozen clunky terminal scripts, CipherGuard brings everything you need—dictionary generation, hash extraction, brute-force cracking, and password strength analysis—into one unified, beautiful platform. 

Whether you want the immersive experience of our premium web dashboard (complete with a glowing medieval aesthetic and an AI guardian) or the raw speed of a terminal interface, CipherGuard has you covered.

---

## What Do These Tools Actually Do?

CipherGuard is packed with five core tools, each designed to simulate how real hackers attack passwords. Here is a simple, human-friendly breakdown of what they do:

🗡️ **The Dictionary Generator (Wordlist Maker):**  
Hackers don't guess passwords randomly; they use massive lists of common words. This tool lets you type in a few base words (like a company name or a season) and automatically creates thousands of clever variations—like swapping 'e' for '3' or adding "2024!" at the end. It builds your custom hacking dictionary.

🛡️ **The Hash Extractor (Password Thief):**  
Computers never store your passwords in plain text; they store scrambled, unreadable versions called "hashes." This tool acts like a digital crowbar. You feed it secure operating system files (like Linux `/etc/shadow` or Windows `SAM`), and it safely pulls out those scrambled hashes so you can try to crack them.

🔥 **The Brute Force Engine (The Password Cracker):**  
This is the heavy hitter. You give it the scrambled hashes you extracted and the dictionary you generated. The engine will rapidly guess thousands of passwords per second, scrambling each guess to see if it perfectly matches the stolen hash. If it finds a match, it reveals the hidden password in plain text.

👁️ **Password Strength Analyzer (The Defender):**  
Instead of attacking, this tool helps you defend. You type in a password, and it acts like a security consultant. It tells you exactly how strong your password is, checks if it follows best practices, and gives you simple, professional tips on how to make it unbreakable.

📜 **The Warden (Your AI Guide):**  
A wise, medieval AI chatbot powered by Google Gemini. If you ever get confused about how a tool works or what a cybersecurity term means, just ask The Warden! It will explain everything to you in very simple language, mixing English and Hinglish to make learning easy.

🏆 **Audit Reports:**  
When your testing session is done, CipherGuard neatly packages all your findings—the words you generated, the hashes you extracted, and the passwords you cracked—into a professional, printable security report.

---

## 🛠️ Getting Setup

Before you breach the gates, make sure you have your tools ready:
- **Python 3.10+**
- **Node.js 18+**
- **pip** and **npm** installed

### 1. Install Dependencies
Open your terminal inside the main `CipherGuard` folder and run:
```bash
# Install Python backend requirements
pip install -r requirements.txt

# Install Node.js helper server requirements
cd backend/node_server
npm install
cd ../..
```

### 2. Configure The Warden (Gemini API)
To bring the AI chatbot to life:
1. Open the `.env` file in the main folder.
2. Get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
3. Paste your key: `GEMINI_API_KEY=AIzaSy...` (No quotes needed).
4. Change the `SECRET_KEY` if you plan to use this in production!

---

## 🚀 How to Launch

CipherGuard gives you two ways to work: the beautiful Web Interface, or the lightning-fast Terminal CLI.

### Option 1: Launch the Web Interface (Recommended)
Want the full immersive experience with the animated dashboard, real-time stats, and The Warden chatbot? 

The easiest way to start the Flask backend, the Node server, and the web UI all at once is:
```bash
bash run.sh
```
*(If you are on Windows, you can use Git Bash to run this, or manually start the servers by running `python backend/app.py` in one terminal and `npm start` inside `backend/node_server` in another).*

### Option 2: Launch the Terminal CLI
Prefer staying in the terminal? No problem. Every single feature of CipherGuard is available via a slick, color-coded interactive command-line interface with real-time progress bars.

To launch the CLI, simply run:
```bash
python backend/cli.py
```
Follow the interactive numbered menu to generate dictionaries, crack hashes, or analyze passwords—no browser required!

---

## ⚖️ Ethical Use Notice

**Read this before you proceed:**
CipherGuard is a weapon forged *strictly* for educational purposes and authorized security testing in controlled lab environments. 

**Never** run this tool against systems, accounts, passwords, or data that you do not own, or do not have explicit written permission to test. The author takes no responsibility for any misuse. If you are unsure whether a particular use is authorized, assume it is illegal.

---

## ⚙️ Tech Stack
- **Frontend:** HTML5, Tailwind CSS, Vanilla JavaScript
- **Backend:** Python 3, Flask, Flask-CORS
- **AI & Helper Server:** Node.js, Express.js, Google Gemini API
- **Core Security Logic:** hashlib, passlib, impacket
- **CLI Tools:** colorama, tqdm, getpass

---

*Engineered & Crafted with precision by Raj.*  
*"Security is not a product. It is a process."*
