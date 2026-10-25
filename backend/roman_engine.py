"""
J.A.R.V.I.S. Roman English Phonetic & Intent Resolution Engine
Normalizes Roman Urdu / Roman English speech patterns, corrects ASR phonetic misrecognitions,
extracts software automation parameters (Spotify, WhatsApp, YouTube, Volume),
and provides robust fuzzy intent matching for hands-free local automation.
"""

import re
from typing import Dict, Any, Optional, Tuple, List

# Common ASR (Automatic Speech Recognition) phonetic mishearings mapped to intended keywords
PHONETIC_CORRECTIONS: Dict[str, str] = {
    # Misrecognitions of "kholo" (open)
    "follow": "kholo",
    "holo": "kholo",
    "hollow": "kholo",
    "colo": "kholo",
    "kolo": "kholo",
    "khol": "kholo",
    "khol do": "kholo",
    "kholna": "kholo",
    "kholiye": "kholo",
    "kholo na": "kholo",
    "open kar do": "kholo",
    "open karo": "kholo",
    
    # Misrecognitions of "chalao" (run/launch/play)
    "shallow": "chalao",
    "chalau": "chalao",
    "shalao": "chalao",
    "chala do": "chalao",
    "chala": "chalao",
    "chalayein": "chalao",
    "launch karo": "chalao",
    "run karo": "chalao",
    "play karo": "chalao",
    "lagao": "chalao",
    "laga do": "chalao",

    # Misrecognitions of "batao" (tell/check)
    "but how": "batao",
    "butto": "batao",
    "photo": "batao",
    "bata do": "batao",
    "bataayein": "batao",
    "bata": "batao",
    "check karo": "batao",

    # Misrecognitions of "dikhao" (show)
    "they cow": "dikhao",
    "the car": "dikhao",
    "dekhna": "dikhao",
    "dekho": "dikhao",
    "show karo": "dikhao",

    # Misrecognitions of "kya haal hai" (how are you)
    "call high": "kya haal hai",
    "car high": "kya haal hai",
    "can i have": "kya haal hai",
    "kya hall hai": "kya haal hai",
    "kya hal hai": "kya haal hai",
    "kya haal": "kya haal hai",
    "kya scene": "kya haal hai",
    "kya scene hai": "kya haal hai",
    "kaise ho": "kya haal hai",

    # Common entity misrecognitions
    "prajacts": "projects",
    "projets": "projects",
    "progects": "projects",
    "vskode": "vscode",
    "vs cod": "vscode",
    "v s code": "vscode",
    "we code": "vscode",
    "we score": "vscode",
    "krom": "chrome",
    "crome": "chrome",
    "chrom": "chrome",
    "krome": "chrome",
    "croam": "chrome",
    "crowm": "chrome",
    "gugle": "google",
    "brauser": "browser",
    "betry": "battery",
    "betri": "battery",
    "obsidion": "obsidian",
    "spoti fy": "spotify",
    "spoti-fy": "spotify",
    "spoty": "spotify",
    "spoti": "spotify",
    "watsapp": "whatsapp",
    "what's app": "whatsapp",
    "wats app": "whatsapp",
    "whtsapp": "whatsapp",
    "watsup": "whatsapp",
    "note pad": "notepad",
    "not pad": "notepad",
    "calculate": "calculator",
    "calci": "calculator",
    "power shell": "powershell",
    "ter minal": "terminal",
    "tarminal": "terminal"
}

# Core Intent Enums
INTENT_OPEN_PROJECTS = "OPEN_PROJECTS"
INTENT_OPEN_VAULT = "OPEN_VAULT"
INTENT_LAUNCH_VSCODE = "LAUNCH_VSCODE"
INTENT_LAUNCH_CHROME = "LAUNCH_CHROME"
INTENT_LAUNCH_NOTEPAD = "LAUNCH_NOTEPAD"
INTENT_LAUNCH_CALCULATOR = "LAUNCH_CALCULATOR"
INTENT_LAUNCH_TERMINAL = "LAUNCH_TERMINAL"
INTENT_LAUNCH_GENERIC_APP = "LAUNCH_GENERIC_APP"
INTENT_CHECK_BATTERY = "CHECK_BATTERY"
INTENT_CHECK_SYSTEM = "CHECK_SYSTEM"
INTENT_GREETING = "GREETING"
INTENT_WHO_ARE_YOU = "WHO_ARE_YOU"
INTENT_WHO_AM_I = "WHO_AM_I"

# Advanced Software Task Intents
INTENT_SPOTIFY = "SPOTIFY"
INTENT_WHATSAPP = "WHATSAPP"
INTENT_YOUTUBE = "YOUTUBE"
INTENT_MEDIA_CONTROL = "MEDIA_CONTROL"
INTENT_VOLUME_CONTROL = "VOLUME_CONTROL"
INTENT_EXIT_SESSION = "EXIT_SESSION"

# Copilot & Backup Automation Intents
INTENT_BACKUP_VAULT = "BACKUP_VAULT"
INTENT_BACKUP_PROJECTS = "BACKUP_PROJECTS"
INTENT_GENERATE_SCRAPER = "GENERATE_SCRAPER"

# Omnipotent System Administration Intents
INTENT_LOCK_PC = "LOCK_PC"
INTENT_EMPTY_TRASH = "EMPTY_TRASH"
INTENT_LIST_PROCESSES = "LIST_PROCESSES"
INTENT_CHECK_NETWORK = "CHECK_NETWORK"
INTENT_READ_CLIPBOARD = "READ_CLIPBOARD"

INTENT_UNKNOWN = "UNKNOWN"


def levenshtein_distance(s1: str, s2: str) -> int:
    """Computes Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def similarity_ratio(s1: str, s2: str) -> float:
    """Computes normalized string similarity (0.0 to 1.0)."""
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    dist = levenshtein_distance(s1.lower(), s2.lower())
    return 1.0 - (dist / max_len)


def normalize_roman_text(text: str) -> str:
    """
    Cleans transcript, strips wake word prefix, and replaces known
    ASR phonetic errors with canonical Roman English keywords.
    """
    q = text.lower().strip()
    
    # Strip wake-word prefixes
    q = re.sub(r"^(hey\s+|yo\s+|ok\s+|suno\s+|oye\s+)?jarvis[,.]?\s*", "", q).strip()
    q = re.sub(r"\s+", " ", q)

    # 1. Multi-word phrase replacements
    for phrase, replacement in PHONETIC_CORRECTIONS.items():
        if " " in phrase and phrase in q:
            q = q.replace(phrase, replacement)

    # 2. Single token replacements
    tokens = q.split()
    corrected_tokens = []
    for token in tokens:
        clean_token = re.sub(r"[^\w]", "", token)
        if clean_token in PHONETIC_CORRECTIONS:
            corrected_tokens.append(PHONETIC_CORRECTIONS[clean_token])
        else:
            corrected_tokens.append(clean_token)

    return " ".join(corrected_tokens).strip()


def resolve_roman_intent(raw_query: str) -> Tuple[str, float, str, Dict[str, Any]]:
    """
    Resolves the user's Roman English query into a canonical intent with extracted parameters,
    returning (intent_name, confidence, normalized_query, params_dict).
    """
    normalized = normalize_roman_text(raw_query)
    tokens = normalized.split()
    params: Dict[str, Any] = {}

    # 0. Session Exit / Standby Directives ("jao", "chale jao", "bye", "standby")
    exit_patterns = [
        r"\bjao\b", r"\bchale jao\b", r"\bchalo jao\b", r"\bjaao\b",
        r"\bbye\b", r"\bgoodbye\b", r"\bgood bye\b", r"\balvida\b",
        r"\bstandby\b", r"\bstand by\b", r"\bso jao\b", r"\bsojao\b",
        r"\bstop karo\b", r"\bbas karo\b", r"\bitna kaafi hai\b", r"\bbas\b"
    ]
    for ep in exit_patterns:
        if re.search(ep, normalized):
            params["session_exit"] = True
            return INTENT_EXIT_SESSION, 1.0, normalized, params

    # 1. Spotify Automation (Song Playback & Search)
    if "spotify" in normalized or "gana chalao" in normalized or "song chalao" in normalized:
        song_query = ""
        # Extract song name: e.g. "spotify par atif aslam chalao" -> "atif aslam"
        match = re.search(r"spotify\s+(?:par|pe|me|mein)?\s*(.*?)\s*(?:chalao|kholo|play|lagao)?$", normalized)
        if match and match.group(1).strip():
            candidate = match.group(1).strip()
            # Clean filler words
            candidate = re.sub(r"\b(koi|song|gana|geet|music|play|chalao|lagao)\b", "", candidate).strip()
            if candidate:
                song_query = candidate

        params["song_query"] = song_query
        return INTENT_SPOTIFY, 1.0, normalized, params

    # 2. WhatsApp Automation (Contacts & Messages)
    if "whatsapp" in normalized:
        contact_name = ""
        message_text = ""
        # e.g. "whatsapp par ali ko message karo main pohanch gaya"
        contact_match = re.search(r"whatsapp\s+(?:par|pe|me)?\s*([a-zA-Z0-9_\+]+)\s+ko\s+(?:message|msg|bolo)?\s*(.*)", normalized)
        if contact_match:
            contact_name = contact_match.group(1).strip()
            message_text = contact_match.group(2).strip()
            # Clean message prefix
            message_text = re.sub(r"^(karo|bhejo|bolo)\s*", "", message_text).strip()

        params["contact"] = contact_name
        params["message"] = message_text
        return INTENT_WHATSAPP, 1.0, normalized, params

    # 3. YouTube Search / Play
    if "youtube" in normalized:
        yt_query = ""
        match = re.search(r"youtube\s+(?:par|pe)?\s*(.*?)\s*(?:chalao|kholo|play|search)?$", normalized)
        if match and match.group(1).strip():
            yt_query = re.sub(r"\b(koi|video|search|karo|chalao)\b", "", match.group(1)).strip()
        params["yt_query"] = yt_query
        return INTENT_YOUTUBE, 1.0, normalized, params

    # 4. Backup Directives (Vault & Projects)
    if "backup" in normalized or "back up" in normalized:
        if any(k in normalized for k in ["vault", "obsidian", "notes", "testing"]):
            return INTENT_BACKUP_VAULT, 1.0, normalized, params
        elif any(k in normalized for k in ["project", "projects", "code"]):
            return INTENT_BACKUP_PROJECTS, 1.0, normalized, params
        else:
            return INTENT_BACKUP_VAULT, 1.0, normalized, params

    # 5. AI Scraper Generator Directives
    if any(k in normalized for k in ["scraper banao", "scraper generate", "scraping script", "scraper script", "playwright script"]):
        params["url"] = "https://example.com"
        params["framework"] = "playwright"
        return INTENT_GENERATE_SCRAPER, 1.0, normalized, params

    # 5.1 Lock Workstation
    if any(k in normalized for k in ["pc lock", "lock pc", "lock karo", "screen lock", "laptop lock"]):
        return INTENT_LOCK_PC, 1.0, normalized, params

    # 5.2 Empty Recycle Bin
    if any(k in normalized for k in ["recycle bin", "trash saaf", "trash khali", "bin empty", "bin saaf"]):
        return INTENT_EMPTY_TRASH, 1.0, normalized, params

    # 5.3 Process List / Active Tasks
    if any(k in normalized for k in ["processes", "tasks", "running apps", "konsi app"]):
        if any(v in normalized for v in ["dikhao", "batao", "check", "chal rahi", "list"]):
            return INTENT_LIST_PROCESSES, 1.0, normalized, params

    # 5.4 Network & Wi-Fi Check
    if any(k in normalized for k in ["wifi", "network", "internet", "ping"]) or re.search(r"\bip\b", normalized):
        if any(v in normalized for v in ["check", "batao", "dikhao", "kaisa", "status"]):
            return INTENT_CHECK_NETWORK, 1.0, normalized, params

    # 5.5 Clipboard Content
    if any(k in normalized for k in ["clipboard", "clip board", "kya copy hai", "copy kya kiya"]):
        return INTENT_READ_CLIPBOARD, 1.0, normalized, params

    # 6. Media Playback Controls (Play/Pause/Next/Prev)
    if any(k in normalized for k in ["pause karo", "gana roko", "song pause", "resume karo", "next song", "agla gana", "pichla gana"]):
        if any(w in normalized for w in ["next", "agla", "skip"]):
            params["action"] = "next"
        elif any(w in normalized for w in ["prev", "pichla"]):
            params["action"] = "previous"
        else:
            params["action"] = "toggle"
        return INTENT_MEDIA_CONTROL, 1.0, normalized, params

    # 5. Volume Controls
    if any(k in normalized for k in ["volume", "awaz", "sound", "awaaz"]):
        if any(w in normalized for w in ["badhao", "tez", "up", "high", "barhao"]):
            params["action"] = "up"
            return INTENT_VOLUME_CONTROL, 1.0, normalized, params
        elif any(w in normalized for w in ["kam", "slow", "down", "low"]):
            params["action"] = "down"
            return INTENT_VOLUME_CONTROL, 1.0, normalized, params
        elif any(w in normalized for w in ["mute", "band", "khamosh", "off"]):
            params["action"] = "mute"
            return INTENT_VOLUME_CONTROL, 1.0, normalized, params

    # 6. Projects Directory
    if any(k in normalized for k in [
        "projects kholo", "project kholo", "projects folder", "my projects",
        "open projects", "projects dikhao", "project folder", "projects open"
    ]):
        return INTENT_OPEN_PROJECTS, 1.0, normalized, params

    # 7. Obsidian Vault
    if any(k in normalized for k in [
        "vault kholo", "obsidian kholo", "notes kholo", "notes dikhao",
        "testing vault", "open vault", "open obsidian", "obsidian open"
    ]):
        return INTENT_OPEN_VAULT, 1.0, normalized, params

    # 8. Visual Studio Code
    if "vscode" in normalized or "vs code" in normalized or ("code" in normalized and any(v in normalized for v in ["kholo", "chalao", "open", "launch", "start", "run"])):
        return INTENT_LAUNCH_VSCODE, 1.0, normalized, params

    # 9. Google Chrome
    if "chrome" in normalized or "google chrome" in normalized or ("browser" in normalized and any(v in normalized for v in ["kholo", "chalao", "open", "launch", "start", "run"])):
        return INTENT_LAUNCH_CHROME, 1.0, normalized, params

    # 10. Notepad
    if "notepad" in normalized or "note pad" in normalized:
        return INTENT_LAUNCH_NOTEPAD, 1.0, normalized, params

    # 11. Calculator
    if "calculator" in normalized or "calc" in normalized or "hisaab" in normalized:
        return INTENT_LAUNCH_CALCULATOR, 1.0, normalized, params

    # 12. Terminal / PowerShell
    if any(t in normalized for t in ["terminal", "powershell", "cmd", "command prompt"]):
        return INTENT_LAUNCH_TERMINAL, 1.0, normalized, params

    # 12.1 Universal Generic Application Launcher
    for app_cand in ["discord", "word", "excel", "powerpoint", "edge", "settings", "taskmgr", "taskmanager", "task manager", "explorer"]:
        if app_cand in normalized and any(v in normalized for v in ["kholo", "chalao", "open", "launch", "start", "run"]):
            params["app_name"] = app_cand
            return INTENT_LAUNCH_GENERIC_APP, 1.0, normalized, params

    # 13. Battery Check
    if any(k in normalized for k in [
        "battery", "charging", "battery batao", "battery kitni", "check battery", "power status"
    ]):
        return INTENT_CHECK_BATTERY, 1.0, normalized, params

    # 14. System Diagnostics (Check system/pc keywords first)
    if any(k in normalized for k in ["system", "pc", "laptop", "diagnostics", "performance"]):
        if any(v in normalized for v in ["status", "check", "kaisa", "kya haal", "batao", "performance"]):
            return INTENT_CHECK_SYSTEM, 1.0, normalized, params

    # 15. Greetings
    if any(k in normalized for k in [
        "kya haal hai", "kaise ho", "kya scene", "how are you", "hello"
    ]):
        return INTENT_GREETING, 1.0, normalized, params

    # 16. Identity Questions
    if any(k in normalized for k in [
        "who are you", "tum kaun ho", "apna intro", "introduce yourself"
    ]):
        return INTENT_WHO_ARE_YOU, 1.0, normalized, params

    if any(k in normalized for k in [
        "who am i", "main kaun hoon", "do you know me", "mera naam"
    ]):
        return INTENT_WHO_AM_I, 1.0, normalized, params

    # Fuzzy Matching Fallback for Misheard ASR Words
    for token in tokens:
        if similarity_ratio(token, "projects") >= 0.75 and any(v in normalized for v in ["kholo", "open", "dikhao"]):
            return INTENT_OPEN_PROJECTS, 0.85, normalized, params
        if similarity_ratio(token, "vscode") >= 0.75:
            return INTENT_LAUNCH_VSCODE, 0.85, normalized, params
        if similarity_ratio(token, "battery") >= 0.75:
            return INTENT_CHECK_BATTERY, 0.85, normalized, params
        if similarity_ratio(token, "chrome") >= 0.75 and any(v in normalized for v in ["kholo", "open", "chalao"]):
            return INTENT_LAUNCH_CHROME, 0.85, normalized, params
        if similarity_ratio(token, "spotify") >= 0.75:
            params["song_query"] = ""
            return INTENT_SPOTIFY, 0.85, normalized, params
        if similarity_ratio(token, "whatsapp") >= 0.75:
            params["contact"] = ""
            params["message"] = ""
            return INTENT_WHATSAPP, 0.85, normalized, params

    return INTENT_UNKNOWN, 0.0, normalized, params
