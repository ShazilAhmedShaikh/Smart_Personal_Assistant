"""
Test suite for J.A.R.V.I.S. Roman English Phonetic & Intent Engine.
Verifies accurate intent resolution across real-world speech misrecognitions,
software automation (Spotify, WhatsApp, YouTube), media controls, and conversational session exits.
"""

import sys
from pathlib import Path
import pytest

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

import roman_engine
from roman_engine import (
    INTENT_OPEN_PROJECTS,
    INTENT_OPEN_VAULT,
    INTENT_LAUNCH_VSCODE,
    INTENT_LAUNCH_CHROME,
    INTENT_LAUNCH_NOTEPAD,
    INTENT_LAUNCH_CALCULATOR,
    INTENT_LAUNCH_TERMINAL,
    INTENT_CHECK_BATTERY,
    INTENT_CHECK_SYSTEM,
    INTENT_GREETING,
    INTENT_WHO_ARE_YOU,
    INTENT_WHO_AM_I,
    INTENT_SPOTIFY,
    INTENT_WHATSAPP,
    INTENT_YOUTUBE,
    INTENT_MEDIA_CONTROL,
    INTENT_VOLUME_CONTROL,
    INTENT_EXIT_SESSION,
    INTENT_BACKUP_VAULT,
    INTENT_BACKUP_PROJECTS,
    INTENT_GENERATE_SCRAPER,
    INTENT_LOCK_PC,
    INTENT_EMPTY_TRASH,
    INTENT_LIST_PROCESSES,
    INTENT_CHECK_NETWORK,
    INTENT_READ_CLIPBOARD
)

TEST_CASES = [
    # System Administration Omnipotence
    ("pc lock karo", INTENT_LOCK_PC),
    ("lock pc", INTENT_LOCK_PC),
    ("recycle bin saaf karo", INTENT_EMPTY_TRASH),
    ("trash khali karo", INTENT_EMPTY_TRASH),
    ("processes dikhao", INTENT_LIST_PROCESSES),
    ("tasks check karo", INTENT_LIST_PROCESSES),
    ("wifi check karo", INTENT_CHECK_NETWORK),
    ("network check karo", INTENT_CHECK_NETWORK),
    ("clipboard dikhao", INTENT_READ_CLIPBOARD),

    # Backup Directives
    ("vault ka backup banao", INTENT_BACKUP_VAULT),
    ("obsidian backup karo", INTENT_BACKUP_VAULT),
    ("projects ka backup lo", INTENT_BACKUP_PROJECTS),

    # AI Coding Copilot Directives
    ("scraper banao", INTENT_GENERATE_SCRAPER),
    ("playwright script generate karo", INTENT_GENERATE_SCRAPER),

    # Conversational Session Exits ("jao", "bye", "standby", "alvida")
    ("Jarvis, jao", INTENT_EXIT_SESSION),
    ("chale jao", INTENT_EXIT_SESSION),
    ("chalo jao", INTENT_EXIT_SESSION),
    ("bye jarvis", INTENT_EXIT_SESSION),
    ("alvida", INTENT_EXIT_SESSION),
    ("standby par jao", INTENT_EXIT_SESSION),
    ("stand by", INTENT_EXIT_SESSION),
    ("itna kaafi hai", INTENT_EXIT_SESSION),
    ("bas", INTENT_EXIT_SESSION),

    # Spotify Automation
    ("spotify par atif aslam chalao", INTENT_SPOTIFY),
    ("spotify par gana lagao", INTENT_SPOTIFY),
    ("spotify chalao", INTENT_SPOTIFY),
    ("spoti fy kholo", INTENT_SPOTIFY),

    # WhatsApp Automation
    ("whatsapp par ali ko message karo main araha hoon", INTENT_WHATSAPP),
    ("whatsapp kholo", INTENT_WHATSAPP),
    ("watsapp open karo", INTENT_WHATSAPP),

    # YouTube Automation
    ("youtube par lofi chalao", INTENT_YOUTUBE),
    ("youtube kholo", INTENT_YOUTUBE),

    # Media & Volume Controls
    ("pause karo", INTENT_MEDIA_CONTROL),
    ("next song", INTENT_MEDIA_CONTROL),
    ("volume badhao", INTENT_VOLUME_CONTROL),
    ("awaz kam karo", INTENT_VOLUME_CONTROL),
    ("sound mute karo", INTENT_VOLUME_CONTROL),

    # Projects Directory & ASR Mishearings
    ("Jarvis, projects kholo", INTENT_OPEN_PROJECTS),
    ("projects follow", INTENT_OPEN_PROJECTS),
    ("Jarvis, project holo", INTENT_OPEN_PROJECTS),
    ("projects open kar do", INTENT_OPEN_PROJECTS),
    ("prajacts kholo", INTENT_OPEN_PROJECTS),

    # Obsidian Engineering Vault
    ("Jarvis, vault kholo", INTENT_OPEN_VAULT),
    ("obsidian follow", INTENT_OPEN_VAULT),
    ("testing vault dikhao", INTENT_OPEN_VAULT),

    # VS Code
    ("vscode chalao", INTENT_LAUNCH_VSCODE),
    ("vskode shallow", INTENT_LAUNCH_VSCODE),
    ("code kholo", INTENT_LAUNCH_VSCODE),

    # Google Chrome
    ("chrome chalao", INTENT_LAUNCH_CHROME),
    ("krom kholo", INTENT_LAUNCH_CHROME),

    # Battery
    ("battery batao", INTENT_CHECK_BATTERY),
    ("betry but how", INTENT_CHECK_BATTERY),
    ("battery kitni hai", INTENT_CHECK_BATTERY),

    # System Health
    ("system status check karo", INTENT_CHECK_SYSTEM),
    ("system kaisa chal raha hai", INTENT_CHECK_SYSTEM),

    # Greetings
    ("kya haal hai", INTENT_GREETING),
    ("call high", INTENT_GREETING),
    ("kaise ho jarvis", INTENT_GREETING),

    # Identity
    ("tum kaun ho", INTENT_WHO_ARE_YOU),
    ("main kaun hoon", INTENT_WHO_AM_I)
]


@pytest.mark.parametrize("query, expected_intent", TEST_CASES)
def test_roman_intent_resolution(query, expected_intent):
    intent, confidence, normalized, params = roman_engine.resolve_roman_intent(query)
    assert intent == expected_intent, (
        f"Failed for query '{query}': expected '{expected_intent}', got '{intent}' (normalized: '{normalized}')"
    )
    assert confidence >= 0.7, f"Confidence too low ({confidence}) for query '{query}'"


def test_spotify_param_extraction():
    intent, conf, norm, params = roman_engine.resolve_roman_intent("spotify par atif aslam chalao")
    assert intent == INTENT_SPOTIFY
    assert "atif aslam" in params.get("song_query", "").lower()


def test_whatsapp_param_extraction():
    intent, conf, norm, params = roman_engine.resolve_roman_intent("whatsapp par ali ko message karo main araha hoon")
    assert intent == INTENT_WHATSAPP
    assert params.get("contact", "").lower() == "ali"
    assert "main araha hoon" in params.get("message", "").lower()


def test_exit_session_flag():
    intent, conf, norm, params = roman_engine.resolve_roman_intent("chale jao jarvis")
    assert intent == INTENT_EXIT_SESSION
    assert params.get("session_exit") is True
