#!/bin/bash
# CipherGuard — Linux Shadow File Extractor
# Sirf root user hi is script ko chala sakta hai
# Engineered & Crafted by Raj

# Root check karo
if [ "$EUID" -ne 0 ]; then
  echo "[ERROR] Root privileges chahiye. sudo se run karo."
  exit 1
fi

# Banner print karo
echo "╔══════════════════════════════════════╗"
echo "║   CipherGuard Shadow Extractor       ║"
echo "║   Engineered & Crafted by Raj        ║"
echo "╚══════════════════════════════════════╝"

# Output path set karo
OUTPUT="./backend/output/shadow_hashes.txt"

# Output directory banao agar exist nahi karti
mkdir -p "$(dirname "$OUTPUT")"

# Shadow file extract karo — invalid entries skip karo
echo "[INFO] /etc/shadow se hashes nikal rahe hain..."
grep -v "^#" /etc/shadow | grep -v ":\*:" | grep -v ":!:" | grep -v "^$" > "$OUTPUT"

COUNT=$(wc -l < "$OUTPUT")
echo "[SUCCESS] $COUNT hashes saved to $OUTPUT"
echo "[WARNING] Is data ko sirf authorized lab environment mein use karo."
echo "[WARNING] Ethical use only — Engineered & Crafted by Raj"
