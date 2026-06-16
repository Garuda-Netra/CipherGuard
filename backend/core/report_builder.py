"""
CipherGuard — Report Builder Core Logic
Session data se structured security audit report generate karta hai
Sirf core logic — koi Flask dependency nahi
Engineered & Crafted by Raj
"""


def _generate_executive_summary(session_data):
    """
    Session data se ek professional executive summary paragraph auto-generate karta hai
    Findings ke basis pe relevant points include karta hai
    """
    summary_parts = []
    summary_parts.append("CipherGuard Password Credential Audit Suite ne ek comprehensive security assessment perform kiya.")

    # Dictionary results ka summary
    dict_data = session_data.get('dictionary_results', {})
    if dict_data:
        total = dict_data.get('total_words', 0)
        summary_parts.append(f"Custom dictionary generation se {total} unique password permutations create hui.")

    # Hash extraction results ka summary
    hash_data = session_data.get('hash_results', [])
    if hash_data and isinstance(hash_data, list):
        summary_parts.append(f"Hash extraction mein {len(hash_data)} user credentials successfully extract hue.")

    # Brute force results ka summary
    brute_data = session_data.get('brute_results', {})
    if brute_data:
        if brute_data.get('found'):
            summary_parts.append(
                f"Brute force attack successful raha — password '{brute_data.get('password', 'N/A')}' "
                f"crack ho gaya {brute_data.get('count', 0)} attempts mein."
            )
        else:
            summary_parts.append("Brute force attack se target hash crack nahi ho paya — strong password indication.")

    # Strength analysis results ka summary
    strength_data = session_data.get('strength_results', {})
    if strength_data:
        rating = strength_data.get('rating', 'Unknown')
        entropy = strength_data.get('entropy', 0)
        summary_parts.append(f"Password strength analysis mein rating '{rating}' mili entropy {entropy} bits ke saath.")

    # Agar koi data nahi hai toh generic message
    if len(summary_parts) <= 1:
        summary_parts.append("Abhi koi specific audit data available nahi hai. Individual tools chalayein pehle.")

    return " ".join(summary_parts)


def _generate_recommendations(session_data):
    """
    Findings ke basis pe specific security recommendations generate karta hai
    Generic advice nahi — actual results ke basis pe tailored suggestions
    """
    recommendations = []

    # Brute force se related recommendations
    brute_data = session_data.get('brute_results', {})
    if brute_data and brute_data.get('found'):
        recommendations.append("CRITICAL: Ek password successfully crack ho gaya — immediately change karein.")
        recommendations.append("Brute force resistant hashing algorithm use karein jaise Argon2id ya bcrypt.")
        recommendations.append("Account lockout policy implement karein — 5 failed attempts ke baad lock.")

    # Strength analysis se related recommendations
    strength_data = session_data.get('strength_results', {})
    if strength_data:
        rating = strength_data.get('rating', '')
        if rating in ('Weak', 'Fair'):
            recommendations.append("Password policy enforce karein — minimum 12 characters required.")
            recommendations.append("Multi-factor authentication (MFA) implement karein saare administrative accounts pe.")
        # Tips bhi add karo agar hain
        tips = strength_data.get('tips', [])
        for tip in tips:
            if tip not in recommendations:
                recommendations.append(tip)

    # Hash extraction se related recommendations
    hash_data = session_data.get('hash_results', [])
    if hash_data and isinstance(hash_data, list):
        algos = set()
        for h in hash_data:
            algos.add(h.get('algorithm', 'Unknown'))
        if 'MD5' in algos:
            recommendations.append("MD5 hashing se migrate karein — yeh outdated aur vulnerable hai. SHA-512 ya Argon2id use karein.")
        if 'Unknown' in algos:
            recommendations.append("Unknown hashing algorithms detected — security audit karein aur modern algorithms pe migrate karein.")

    # General recommendations hamesha add karo
    recommendations.append("Regular password rotation policy implement karein — har 90 din mein password change.")
    recommendations.append("Password manager ka use promote karein organization mein.")
    recommendations.append("Leaked password databases ke against periodic checks karein.")

    return recommendations


def _generate_risk_matrix(session_data):
    """
    Risk matrix generate karta hai — har analyzed password ka risk level
    Crack time estimates: Weak=<1 minute, Fair=1-60 minutes, Strong=days to months, Fortress=years+
    """
    risk_matrix = []

    # Strength data se risk matrix banao
    strength_data = session_data.get('strength_results', {})
    if strength_data:
        rating = strength_data.get('rating', 'Unknown')

        # Rating ke basis pe estimated crack time decide karo
        crack_time_map = {
            'Weak': '< 1 minute',
            'Fair': '1 — 60 minutes',
            'Strong': 'Days to months',
            'Fortress': 'Years to centuries'
        }
        risk_level_map = {
            'Weak': 'CRITICAL',
            'Fair': 'HIGH',
            'Strong': 'LOW',
            'Fortress': 'MINIMAL'
        }

        risk_matrix.append({
            "password_sample": "***analyzed***",
            "rating": rating,
            "estimated_crack_time": crack_time_map.get(rating, 'Unknown'),
            "risk_level": risk_level_map.get(rating, 'UNKNOWN')
        })

    # Brute force results se bhi data add karo agar available hai
    brute_data = session_data.get('brute_results', {})
    if brute_data and brute_data.get('found'):
        risk_matrix.append({
            "password_sample": brute_data.get('password', '***')[:4] + '****',
            "rating": "Weak",
            "estimated_crack_time": f"{brute_data.get('time_taken', 0)} seconds (actual)",
            "risk_level": "CRITICAL"
        })

    return risk_matrix


def build_report(session_data):
    """
    Complete structured security audit report build karta hai
    Saare tool results combine karke ek comprehensive report banata hai
    
    session_data: dict jismein dictionary_results, hash_results, brute_results, strength_results hain
    Returns: structured dict with all report sections
    """
    # Executive summary auto-generate karo findings ke basis pe
    executive_summary = _generate_executive_summary(session_data)

    # Dictionary results section
    dict_data = session_data.get('dictionary_results', {})
    dictionary_results = {
        "total_words": dict_data.get('total_words', 0),
        "mutations_used": dict_data.get('mutations_used', []),
        "file_path": dict_data.get('file_path', 'N/A')
    }

    # Hash findings section
    hash_findings = session_data.get('hash_results', [])
    if isinstance(hash_findings, dict) and 'error' in hash_findings:
        hash_findings = []

    # Brute force results section
    brute_data = session_data.get('brute_results', {})
    brute_force_results = {
        "target_hash": brute_data.get('target_hash', 'N/A'),
        "found": brute_data.get('found', False),
        "password": brute_data.get('password', None),
        "attempts": brute_data.get('count', 0),
        "time_taken": brute_data.get('time_taken', 0),
        "method": brute_data.get('method', 'N/A')
    }

    # Strength summary section
    strength_data = session_data.get('strength_results', {})
    strength_summary = []
    if strength_data:
        strength_summary.append({
            "password_sample": "***analyzed***",
            "rating": strength_data.get('rating', 'N/A'),
            "entropy": strength_data.get('entropy', 0),
            "score": strength_data.get('score', 0)
        })

    # Risk matrix generate karo
    risk_matrix = _generate_risk_matrix(session_data)

    # Recommendations generate karo — findings-based
    recommendations = _generate_recommendations(session_data)

    # Credits line — hamesha same rahegi
    credits = "CipherGuard — Password Credential Audit Suite. Engineered & Crafted by Raj."

    # Poora report dict assemble karo aur return karo
    report = {
        "executive_summary": executive_summary,
        "dictionary_results": dictionary_results,
        "hash_findings": hash_findings,
        "brute_force_results": brute_force_results,
        "strength_summary": strength_summary,
        "risk_matrix": risk_matrix,
        "recommendations": recommendations,
        "credits": credits
    }

    return report
