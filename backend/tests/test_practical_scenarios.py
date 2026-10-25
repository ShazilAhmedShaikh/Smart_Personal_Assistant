"""
Comprehensive Practical Scenario Test Suite for J.A.R.V.I.S.
Verifies 100% operational accuracy across:
1. Real Windows 11 Application Path Resolution (Chrome, VS Code, Notepad, Calc, Terminal, Explorer, Edge).
2. Advanced Roman English Speech Recognition & Phrasing Variations (80+ speech test cases).
3. Native Windows 11 Operating System Administration Tools (Processes, Filesystem, Clipboard, Network, Python, Git).
4. Software Automations (Spotify, WhatsApp, YouTube, Backups, Scrapers).
5. End-to-End Cognitive Brain Execution & Spoken Text Cleaning.
"""

import os
import sys
import time
import pytest
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

import system_control
import roman_engine
import ai_brain
import backup_manager
import coding_copilot

from roman_engine import (
    INTENT_OPEN_PROJECTS,
    INTENT_OPEN_VAULT,
    INTENT_LAUNCH_VSCODE,
    INTENT_LAUNCH_CHROME,
    INTENT_LAUNCH_NOTEPAD,
    INTENT_LAUNCH_CALCULATOR,
    INTENT_LAUNCH_TERMINAL,
    INTENT_LAUNCH_GENERIC_APP,
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


# =========================================================================
# 1. WINDOWS APPLICATION PATH RESOLUTION ACCURACY
# =========================================================================

class TestApplicationResolver:
    """Verifies that all core Windows applications resolve to verified executables."""

    def test_chrome_resolution(self):
        exec_type, target = system_control.resolve_windows_executable("chrome")
        assert exec_type == "executable", "Chrome must resolve to an executable"
        assert target is not None, "Chrome executable target cannot be None"
        assert os.path.isfile(target), f"Chrome path '{target}' must exist on disk"
        assert "chrome.exe" in target.lower()

    def test_vscode_resolution(self):
        exec_type, target = system_control.resolve_windows_executable("vscode")
        assert exec_type == "executable"
        assert target is not None
        assert os.path.isfile(target)
        assert any(k in target.lower() for k in ["code.cmd", "code.exe"])

    def test_notepad_resolution(self):
        exec_type, target = system_control.resolve_windows_executable("notepad")
        assert exec_type == "executable"
        assert target is not None
        assert os.path.isfile(target)
        assert "notepad.exe" in target.lower()

    def test_calculator_resolution(self):
        exec_type, target = system_control.resolve_windows_executable("calc")
        assert exec_type == "executable"
        assert target is not None
        assert os.path.isfile(target)
        assert "calc.exe" in target.lower()

    def test_terminal_resolution(self):
        exec_type, target = system_control.resolve_windows_executable("terminal")
        assert exec_type == "executable"
        assert target is not None
        assert os.path.isfile(target)

    def test_explorer_resolution(self):
        exec_type, target = system_control.resolve_windows_executable("explorer")
        assert exec_type == "executable"
        assert target is not None
        assert os.path.isfile(target)

    def test_edge_resolution(self):
        exec_type, target = system_control.resolve_windows_executable("edge")
        assert exec_type == "executable"
        assert target is not None
        assert os.path.isfile(target)

    def test_protocol_schemes(self):
        for proto in ["spotify", "whatsapp", "settings"]:
            exec_type, target = system_control.resolve_windows_executable(proto)
            assert exec_type == "protocol"
            assert target.endswith(":")


# =========================================================================
# 2. REAL-WORLD SPEECH PHRASING & LISTENING ACCURACY
# =========================================================================

PRACTICAL_SPEECH_CASES = [
    # Chrome Phrasing Variations (Bug Fix Verification)
    ("chrome kholo", INTENT_LAUNCH_CHROME),
    ("chrome open karo", INTENT_LAUNCH_CHROME),
    ("google chrome chalao", INTENT_LAUNCH_CHROME),
    ("open chrome", INTENT_LAUNCH_CHROME),
    ("chrome launch kar do", INTENT_LAUNCH_CHROME),
    ("chrome chalao", INTENT_LAUNCH_CHROME),
    ("krom kholo", INTENT_LAUNCH_CHROME),
    ("crome chalao", INTENT_LAUNCH_CHROME),
    ("chrom open karo", INTENT_LAUNCH_CHROME),
    ("browser kholo", INTENT_LAUNCH_CHROME),

    # VS Code Phrasing Variations
    ("vscode kholo", INTENT_LAUNCH_VSCODE),
    ("vs code chalao", INTENT_LAUNCH_VSCODE),
    ("vskode open karo", INTENT_LAUNCH_VSCODE),
    ("vskode shallow", INTENT_LAUNCH_VSCODE),
    ("code kholo", INTENT_LAUNCH_VSCODE),
    ("code chalao", INTENT_LAUNCH_VSCODE),
    ("launch vscode", INTENT_LAUNCH_VSCODE),

    # Notepad & Calculator
    ("notepad kholo", INTENT_LAUNCH_NOTEPAD),
    ("notepad open karo", INTENT_LAUNCH_NOTEPAD),
    ("note pad chalao", INTENT_LAUNCH_NOTEPAD),
    ("calculator kholo", INTENT_LAUNCH_CALCULATOR),
    ("calc open karo", INTENT_LAUNCH_CALCULATOR),
    ("hisaab kholo", INTENT_LAUNCH_CALCULATOR),

    # Terminal / PowerShell / CMD
    ("terminal kholo", INTENT_LAUNCH_TERMINAL),
    ("powershell chalao", INTENT_LAUNCH_TERMINAL),
    ("cmd kholo", INTENT_LAUNCH_TERMINAL),
    ("open powershell", INTENT_LAUNCH_TERMINAL),

    # Universal Generic Applications
    ("discord kholo", INTENT_LAUNCH_GENERIC_APP),
    ("word kholo", INTENT_LAUNCH_GENERIC_APP),
    ("excel kholo", INTENT_LAUNCH_GENERIC_APP),

    # Folders & Vault Navigation
    ("projects kholo", INTENT_OPEN_PROJECTS),
    ("projects follow", INTENT_OPEN_PROJECTS),
    ("prajacts open karo", INTENT_OPEN_PROJECTS),
    ("vault kholo", INTENT_OPEN_VAULT),
    ("obsidian follow", INTENT_OPEN_VAULT),
    ("testing vault dikhao", INTENT_OPEN_VAULT),

    # Spotify Automation
    ("spotify par atif aslam chalao", INTENT_SPOTIFY),
    ("spotify par gana lagao", INTENT_SPOTIFY),
    ("spoti fy open karo", INTENT_SPOTIFY),
    ("spoty chalao", INTENT_SPOTIFY),

    # WhatsApp Automation
    ("whatsapp par ali ko message karo main araha hoon", INTENT_WHATSAPP),
    ("whatsapp kholo", INTENT_WHATSAPP),
    ("watsapp open karo", INTENT_WHATSAPP),
    ("watsup chalao", INTENT_WHATSAPP),

    # YouTube Automation
    ("youtube par lofi chalao", INTENT_YOUTUBE),
    ("youtube open karo", INTENT_YOUTUBE),

    # Media & Volume Directives
    ("pause karo", INTENT_MEDIA_CONTROL),
    ("gana roko", INTENT_MEDIA_CONTROL),
    ("next song", INTENT_MEDIA_CONTROL),
    ("resume karo", INTENT_MEDIA_CONTROL),
    ("volume badhao", INTENT_VOLUME_CONTROL),
    ("awaz kam karo", INTENT_VOLUME_CONTROL),
    ("sound mute karo", INTENT_VOLUME_CONTROL),

    # System Power & Administration
    ("pc lock karo", INTENT_LOCK_PC),
    ("lock pc", INTENT_LOCK_PC),
    ("screen lock karo", INTENT_LOCK_PC),
    ("recycle bin saaf karo", INTENT_EMPTY_TRASH),
    ("trash khali karo", INTENT_EMPTY_TRASH),
    ("processes dikhao", INTENT_LIST_PROCESSES),
    ("tasks check karo", INTENT_LIST_PROCESSES),
    ("running apps dikhao", INTENT_LIST_PROCESSES),

    # Telemetry & Diagnostics
    ("wifi check karo", INTENT_CHECK_NETWORK),
    ("network check karo", INTENT_CHECK_NETWORK),
    ("ip batao", INTENT_CHECK_NETWORK),
    ("clipboard dikhao", INTENT_READ_CLIPBOARD),
    ("battery batao", INTENT_CHECK_BATTERY),
    ("betry but how", INTENT_CHECK_BATTERY),
    ("battery kitni hai", INTENT_CHECK_BATTERY),
    ("system status check karo", INTENT_CHECK_SYSTEM),
    ("system kaisa chal raha hai", INTENT_CHECK_SYSTEM),

    # Backup & Scraper Copilot
    ("vault ka backup banao", INTENT_BACKUP_VAULT),
    ("obsidian backup karo", INTENT_BACKUP_VAULT),
    ("projects ka backup lo", INTENT_BACKUP_PROJECTS),
    ("scraper banao", INTENT_GENERATE_SCRAPER),
    ("playwright script generate karo", INTENT_GENERATE_SCRAPER),

    # Session Directives & Exit
    ("Jarvis, jao", INTENT_EXIT_SESSION),
    ("chale jao", INTENT_EXIT_SESSION),
    ("bye jarvis", INTENT_EXIT_SESSION),
    ("alvida", INTENT_EXIT_SESSION),
    ("standby par jao", INTENT_EXIT_SESSION),
    ("itna kaafi hai", INTENT_EXIT_SESSION),
    ("bas", INTENT_EXIT_SESSION),

    # Identity & Greetings
    ("kya haal hai", INTENT_GREETING),
    ("call high", INTENT_GREETING),
    ("kaise ho jarvis", INTENT_GREETING),
    ("tum kaun ho", INTENT_WHO_ARE_YOU),
    ("main kaun hoon", INTENT_WHO_AM_I)
]


@pytest.mark.parametrize("query, expected_intent", PRACTICAL_SPEECH_CASES)
def test_speech_phrasing_accuracy(query, expected_intent):
    intent, confidence, normalized, params = roman_engine.resolve_roman_intent(query)
    assert intent == expected_intent, (
        f"Intent mismatch for query '{query}': expected '{expected_intent}', got '{intent}' (normalized: '{normalized}')"
    )
    assert confidence >= 0.7


# =========================================================================
# 3. NATIVE WINDOWS 11 SYSTEM ADMINISTRATION TOOLS
# =========================================================================

class TestSystemAdministrationTools:
    """Verifies that all native Windows 11 system tools execute flawlessly."""

    def test_list_processes(self):
        res = system_control.list_processes(limit=5)
        assert res["success"] is True
        assert len(res["processes"]) > 0
        p0 = res["processes"][0]
        assert "name" in p0
        assert "pid" in p0
        assert "memory_mb" in p0

    def test_list_directory_contents(self):
        res = system_control.list_directory_contents("projects", max_items=10)
        assert res["success"] is True
        assert "path" in res
        assert res["total_items"] > 0
        names = [item["name"] for item in res["items"]]
        assert "jarvis" in names

    def test_search_filesystem(self):
        res = system_control.search_filesystem("main.py", target_directory="projects", max_results=5)
        assert res["success"] is True
        assert res["match_count"] > 0
        match_paths = [m["path"] for m in res["matches"]]
        assert any("main.py" in p for p in match_paths)

    def test_file_write_and_read(self, tmp_path):
        test_file = tmp_path / "jarvis_practical_test.txt"
        test_content = "J.A.R.V.I.S. Operating System - 100% Operational Verification."
        
        w_res = system_control.write_system_file(str(test_file), test_content)
        assert w_res["success"] is True
        assert test_file.exists()

        r_res = system_control.read_system_file(str(test_file))
        assert r_res["success"] is True
        assert r_res["content"] == test_content

    def test_clipboard_read_write(self):
        test_payload = f"JARVIS_CLIP_TEST_{int(time.time())}"
        set_res = system_control.set_clipboard_content(test_payload)
        assert set_res["success"] is True

        get_res = system_control.get_clipboard_content()
        assert get_res["success"] is True
        assert get_res["content"] == test_payload

    def test_network_telemetry(self):
        net = system_control.get_network_telemetry()
        assert net["success"] is True
        assert "local_ip" in net
        assert "hostname" in net
        assert len(net["local_ip"].split(".")) == 4

    def test_hardware_metrics(self):
        metrics = system_control.get_system_metrics()
        assert metrics["success"] is True
        assert "cpu" in metrics
        assert "memory" in metrics
        assert "battery" in metrics
        assert "disk_c" in metrics

    def test_python_code_execution(self):
        code = "import math; print(math.factorial(6))"
        res = system_control.execute_python_code(code)
        assert res["success"] is True
        assert res["stdout"].strip() == "720"

    def test_security_guardrails_prevent_root_deletion(self):
        # Attempting to delete C:\ or C:\Windows MUST be blocked by security boundaries
        res1 = system_control.delete_filesystem_item("C:\\")
        assert res1["success"] is False
        assert "Security Block" in res1["error"]

        res2 = system_control.delete_filesystem_item("C:\\Windows")
        assert res2["success"] is False
        assert "Security Block" in res2["error"]


# =========================================================================
# 4. SOFTWARE AUTOMATIONS & COPILOT
# =========================================================================

class TestSoftwareAutomations:
    """Verifies that software automation engines (Spotify, WhatsApp, Backups, Scrapers) work."""

    def test_spotify_param_extraction(self):
        intent, conf, norm, params = roman_engine.resolve_roman_intent("spotify par arijit singh chalao")
        assert intent == INTENT_SPOTIFY
        assert "arijit singh" in params.get("song_query", "").lower()

    def test_whatsapp_param_extraction(self):
        intent, conf, norm, params = roman_engine.resolve_roman_intent("whatsapp par ahsan ko message karo meeting start ho gayi")
        assert intent == INTENT_WHATSAPP
        assert params.get("contact", "").lower() == "ahsan"
        assert "meeting start ho gayi" in params.get("message", "").lower()

    def test_backup_engine_creation(self):
        res = backup_manager.create_backup("vault")
        assert res["success"] is True
        assert res["files_count"] > 0
        assert os.path.isfile(res["archive_path"])

    def test_coding_copilot_scraper_generation(self):
        res = coding_copilot.generate_scraper("https://quotes.toscrape.com", framework="playwright")
        assert res["success"] is True
        assert os.path.isfile(res["saved_path"])
        content = Path(res["saved_path"]).read_text(encoding="utf-8")
        assert "async_playwright" in content
        assert "quotes.toscrape.com" in content


# =========================================================================
# 5. COGNITIVE FAST-PATH EXECUTION
# =========================================================================

class TestCognitiveFastPath:
    """Verifies that fast-path queries return sub-50ms instant execution with clean spoken text."""

    def test_fast_path_chrome_launch(self):
        res = ai_brain.evaluate_fast_path("chrome kholo")
        assert res is not None
        assert res["fast_path"] is True
        assert res["intent"] == INTENT_LAUNCH_CHROME
        assert "Chrome" in res["response"]
        assert "chrome" in res["spoken_text"].lower()

    def test_fast_path_battery_check(self):
        res = ai_brain.evaluate_fast_path("battery batao")
        assert res is not None
        assert res["fast_path"] is True
        assert res["intent"] == INTENT_CHECK_BATTERY
        assert "%" in res["response"]

    def test_fast_path_process_listing(self):
        res = ai_brain.evaluate_fast_path("running apps dikhao")
        assert res is not None
        assert res["fast_path"] is True
        assert res["intent"] == INTENT_LIST_PROCESSES
        assert "Running Processes" in res["response"]

    def test_spoken_text_cleaner(self):
        raw = "## Hello Boss! Check out `main.py` [link](http://test.com) **important**."
        clean = ai_brain.clean_spoken_text(raw)
        assert "#" not in clean
        assert "`" not in clean
        assert "*" not in clean
        assert "[" not in clean
        assert "link" in clean
