"""
CipherGuard — Hash Extractor Core Logic
Linux shadow files aur Windows SAM/SYSTEM hives se hashes nikalne ka kaam
Sirf core logic — koi Flask dependency nahi
Engineered & Crafted by Raj
"""


# Algorithm detection mapping — hash prefix se algorithm pata lagao
HASH_ALGO_MAP = {
    '$1$': 'MD5',
    '$5$': 'SHA-256',
    '$6$': 'SHA-512',
    '$2b$': 'bcrypt',
    '$2y$': 'bcrypt',
    '$y$': 'yescrypt',
    '$sha1$': 'SHA1-crypt',
}


def _detect_algorithm(hash_string):
    """
    Hash string ke prefix se algorithm ka naam detect karta hai
    Agar koi prefix match nahi hota toh 'Unknown' return karta hai
    """
    for prefix, algo_name in HASH_ALGO_MAP.items():
        if hash_string.startswith(prefix):
            return algo_name
    return 'Unknown'


def parse_shadow_file(file_content):
    """
    Linux /etc/shadow file ka raw text content parse karta hai
    Har valid line se username, algorithm aur hash extract karta hai
    Invalid lines (comments, locked accounts, empty passwords) skip karta hai
    
    Returns: list of dicts — [{"username": str, "algorithm": str, "hash": str}]
    """
    results = []

    # Har line ko process karo
    for line in file_content.strip().split('\n'):
        line = line.strip()

        # Comment lines skip karo
        if line.startswith('#') or not line:
            continue

        # Colon se split karo — shadow file mein fields colon separated hote hain
        parts = line.split(':')
        if len(parts) < 2:
            continue

        username = parts[0]
        hash_field = parts[1]

        # Locked accounts aur empty passwords skip karo
        # * matlab account disabled hai, ! matlab password locked hai
        if hash_field in ('*', '!', '!!', '') or hash_field.startswith('!'):
            continue

        # Algorithm detect karo hash prefix se
        algorithm = _detect_algorithm(hash_field)

        # Result dict banao aur list mein add karo
        results.append({
            "username": username,
            "algorithm": algorithm,
            "hash": hash_field
        })

    return results


def extract_sam_hashes(sam_file_path, system_file_path):
    """
    Windows SAM aur SYSTEM hive files se NTLM hashes extract karta hai
    impacket library ka use karta hai — agar installed nahi hai toh gracefully handle karta hai
    
    Returns: list of dicts — [{"username": str, "algorithm": "NTLM", "hash": str}]
    Ya error dict agar kuch galat ho jaaye
    """
    results = []

    try:
        # impacket import karo — yeh optional dependency hai
        from impacket.examples.secretsdump import LocalOperations, SAMHashes

        # LocalOperations instance banao SYSTEM hive ke saath
        local_ops = LocalOperations(system_file_path)

        # Boot key nikalo SYSTEM hive se — yeh encryption key hai
        boot_key = local_ops.getBootKey()

        # SAMHashes instance banao SAM file aur boot key ke saath
        sam_hashes = SAMHashes(sam_file_path, boot_key)

        # Saare hashes dump karo
        # dump() method internally callback use karta hai, hum list mein collect karenge
        hash_entries = []

        # Custom callback function jo har hash entry ko capture karega
        def _hash_callback(secret):
            hash_entries.append(secret)

        sam_hashes.dump()

        # SAMHashes ke _items se directly access karo
        for item in sam_hashes._items if hasattr(sam_hashes, '_items') else []:
            try:
                # Format hota hai: username:rid:lm_hash:nt_hash:::
                parts = str(item).split(':')
                if len(parts) >= 4:
                    username = parts[0]
                    nt_hash = parts[3]
                    results.append({
                        "username": username,
                        "algorithm": "NTLM",
                        "hash": nt_hash
                    })
            except Exception:
                continue

        # Agar _items se kuch nahi mila toh alternative method try karo
        if not results:
            try:
                # Kuch impacket versions mein exportSecrets() hota hai
                exported = sam_hashes.export(sam_file_path + '.export')
                # File read karke parse karo
                with open(sam_file_path + '.export', 'r') as f:
                    for line in f:
                        parts = line.strip().split(':')
                        if len(parts) >= 4:
                            results.append({
                                "username": parts[0],
                                "algorithm": "NTLM",
                                "hash": parts[3]
                            })
            except Exception:
                pass

        # Cleanup karo
        sam_hashes.finish()

    except ImportError:
        # Agar impacket installed nahi hai toh user ko batao
        return {"error": "impacket library installed nahi hai. Install karo: pip install impacket"}
    except Exception as e:
        # Koi aur error aaye toh gracefully handle karo
        return {"error": f"SAM extraction mein error aaya: {str(e)}"}

    return results
