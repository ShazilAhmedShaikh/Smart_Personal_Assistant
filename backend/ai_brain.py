"""
J.A.R.V.I.S. AI Cognitive Brain Module
Combines sub-50ms local fast-path heuristics with Roman English Phonetic Engine,
Persistent Multi-Turn Dialogue Memory, Automatic Function Calling (AFC),
and Omnipotent Windows 11 System Control across 30+ native operating system tools.
"""

import re
import json
import asyncio
from typing import Dict, Any, List, Optional
from google import genai
from google.genai import types

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_MODELS_CASCADE,
    JARVIS_SYSTEM_INSTRUCTION,
    USER_NAME,
    USER_NICKNAME,
    DEFAULT_PROJECTS_DIR,
    DEFAULT_VAULT_DIR
)
import system_control
import roman_engine
import backup_manager
import coding_copilot

# Initialize Gemini Client if key exists
genai_client = None
if GEMINI_API_KEY and GEMINI_API_KEY.strip() and GEMINI_API_KEY != "your_gemini_api_key_here":
    try:
        genai_client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"[JARVIS BRAIN WARNING] Failed to initialize Gemini Client: {e}")

# Global Multi-Turn Chat Session Cache
active_chat_session = None
active_chat_model = None


def clean_spoken_text(text: str) -> str:
    """
    Strips markdown symbols, emojis, and code formatting to provide
    smooth, natural phrasing for text-to-speech engines.
    """
    cleaned = re.sub(r"[#*_~`]", "", text)
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"\[.*?\]", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def evaluate_fast_path(query: str) -> Optional[Dict[str, Any]]:
    """
    Uses the Roman English Phonetic Engine to resolve voice intents instantly
    with sub-50ms execution, handling misheard speech recognition transcriptions
    and software automation (Spotify, WhatsApp, Media, Volume, System Admin).
    """
    intent, confidence, normalized, params = roman_engine.resolve_roman_intent(query)
    if intent == roman_engine.INTENT_UNKNOWN or confidence < 0.7:
        return None

    # 0. Session Exit / Standby Directive ("jao", "bye", "standby")
    if intent == roman_engine.INTENT_EXIT_SESSION:
        farewell = "Ji Boss, main standby mode par ja raha hoon. Jab bhi zaroorat ho 'Jarvis' keh kar bula lijiyega. Khuda Hafiz!"
        return {
            "fast_path": True,
            "intent": intent,
            "session_exit": True,
            "response": farewell,
            "spoken_text": clean_spoken_text("Ji Boss, main standby mode par ja raha hoon. Jab bhi zaroorat ho Jarvis keh kar bula lijiyega. Khuda Hafiz!"),
            "action": {"session_exit": True}
        }

    # 1. Spotify Automation
    if intent == roman_engine.INTENT_SPOTIFY:
        song = params.get("song_query", "")
        action = system_control.play_spotify(song)
        if song:
            spoken = f"Ji Boss, Spotify par {song} play kar diya hai."
            resp = f"Spotify par **{song}** search karke playback start kar diya hai, Boss."
        else:
            spoken = "Ji Boss, Spotify open kar diya hai aur media resume kar diya hai."
            resp = "Spotify open kar diya hai, Boss."
        return {
            "fast_path": True,
            "intent": intent,
            "response": resp,
            "spoken_text": clean_spoken_text(spoken),
            "action": action
        }

    # 2. WhatsApp Automation
    if intent == roman_engine.INTENT_WHATSAPP:
        contact = params.get("contact", "")
        message = params.get("message", "")
        action = system_control.send_whatsapp(contact, message)
        if contact and message:
            spoken = f"Boss, WhatsApp par {contact} ki chat open karke message type kar diya hai."
            resp = f"WhatsApp par **{contact}** ko message: *'{message}'* ready kar diya hai, Boss."
        elif contact:
            spoken = f"Boss, WhatsApp par {contact} ki chat open kar di hai."
            resp = f"WhatsApp par **{contact}** ki chat open kar di hai, Boss."
        else:
            spoken = "Boss, WhatsApp Desktop launch kar diya hai."
            resp = "WhatsApp launch kar diya hai, Boss."
        return {
            "fast_path": True,
            "intent": intent,
            "response": resp,
            "spoken_text": clean_spoken_text(spoken),
            "action": action
        }

    # 3. YouTube Search / Play
    if intent == roman_engine.INTENT_YOUTUBE:
        yt_query = params.get("yt_query", "")
        action = system_control.play_youtube(yt_query)
        spoken = f"Ji Boss, YouTube par {yt_query} search kar diya hai." if yt_query else "YouTube open kar diya hai, Boss."
        return {
            "fast_path": True,
            "intent": intent,
            "response": f"YouTube par **{yt_query}** search kar diya hai, Boss.",
            "spoken_text": clean_spoken_text(spoken),
            "action": action
        }

    # 4. Media Playback Controls
    if intent == roman_engine.INTENT_MEDIA_CONTROL:
        act = params.get("action", "toggle")
        action = system_control.control_media(act)
        return {
            "fast_path": True,
            "intent": intent,
            "response": action.get("message", "Media action executed, Boss."),
            "spoken_text": action.get("message", "Media action executed, Boss."),
            "action": action
        }

    # 5. Volume Controls
    if intent == roman_engine.INTENT_VOLUME_CONTROL:
        act = params.get("action", "up")
        action = system_control.control_volume(act)
        return {
            "fast_path": True,
            "intent": intent,
            "response": action.get("message", "Volume adjusted, Boss."),
            "spoken_text": action.get("message", "Volume adjusted, Boss."),
            "action": action
        }

    # 6. Automated Vault Backup
    if intent == roman_engine.INTENT_BACKUP_VAULT:
        action = backup_manager.create_backup("vault")
        if action.get("success"):
            spoken = f"Ji Boss, Obsidian Vault ka backup archive C Shazil backups mein save kar diya hai. Total {action.get('files_count', 0)} files compress hui hain."
            resp = f"Obsidian Vault backup complete, Boss!\nArchive: `{action.get('archive_name')}` ({action.get('size_mb')} MB, {action.get('files_count')} files, {action.get('duration_seconds')}s)."
        else:
            spoken = "Boss, Obsidian Vault backup banate waqt error aya hai."
            resp = f"Vault backup error: {action.get('error')}"
        return {
            "fast_path": True,
            "intent": intent,
            "response": resp,
            "spoken_text": clean_spoken_text(spoken),
            "action": action
        }

    # 7. Automated Projects Backup
    if intent == roman_engine.INTENT_BACKUP_PROJECTS:
        action = backup_manager.create_backup("projects")
        if action.get("success"):
            spoken = f"Boss, aapke projects folder ka compressed backup save ho gaya hai. Total {action.get('files_count', 0)} files archive hui hain."
            resp = f"Projects backup complete, Boss!\nArchive: `{action.get('archive_name')}` ({action.get('size_mb')} MB, {action.get('files_count')} files, {action.get('duration_seconds')}s)."
        else:
            spoken = "Boss, projects backup banate waqt error aya hai."
            resp = f"Projects backup error: {action.get('error')}"
        return {
            "fast_path": True,
            "intent": intent,
            "response": resp,
            "spoken_text": clean_spoken_text(spoken),
            "action": action
        }

    # 8. AI Coding Copilot - Scraper Generation
    if intent == roman_engine.INTENT_GENERATE_SCRAPER:
        target_url = params.get("url", "https://example.com")
        fw = params.get("framework", "playwright")
        action = coding_copilot.generate_scraper(url=target_url, framework=fw)
        if action.get("success"):
            spoken = f"Ji Boss, anti-bot Playwright web scraper ka template generate karke projects scrapers folder mein save kar diya hai."
            resp = f"Production-grade **{fw.title()}** anti-bot scraper generated!\nFile: `{action.get('saved_path')}`"
        else:
            spoken = "Boss, scraper template generate karte waqt issue aya hai."
            resp = f"Scraper generation error: {action.get('error')}"
        return {
            "fast_path": True,
            "intent": intent,
            "response": resp,
            "spoken_text": clean_spoken_text(spoken),
            "action": action
        }

    # 9. Lock Workstation
    if intent == roman_engine.INTENT_LOCK_PC:
        action = system_control.lock_workstation()
        return {
            "fast_path": True,
            "intent": intent,
            "response": "Workstation locked successfully, Boss.",
            "spoken_text": "Ji Boss, aapki Dell Latitude lock kar di hai.",
            "action": action
        }

    # 10. Empty Recycle Bin
    if intent == roman_engine.INTENT_EMPTY_TRASH:
        action = system_control.empty_recycle_bin()
        return {
            "fast_path": True,
            "intent": intent,
            "response": "Windows Recycle Bin emptied successfully, Sir.",
            "spoken_text": "Recycle Bin empty kar diya hai, Boss.",
            "action": action
        }

    # 11. List Running Processes
    if intent == roman_engine.INTENT_LIST_PROCESSES:
        action = system_control.list_processes(limit=6)
        procs = action.get("processes", [])
        proc_lines = [f"- **{p['name']}** (PID {p['pid']}): {p['memory_mb']} MB RAM" for p in procs]
        resp = "Top Running Processes:\n" + "\n".join(proc_lines)
        spoken = f"Boss, top active apps screen par hain. Sab se zyada RAM {procs[0]['name'] if procs else 'system'} use kar raha hai."
        return {
            "fast_path": True,
            "intent": intent,
            "response": resp,
            "spoken_text": clean_spoken_text(spoken),
            "action": action
        }

    # 12. Network & Wi-Fi Check
    if intent == roman_engine.INTENT_CHECK_NETWORK:
        action = system_control.get_network_telemetry()
        ip = action.get("local_ip", "Unknown")
        wifi = action.get("wifi_ssid", "Unknown")
        ping = action.get("ping_google", "Normal")
        resp = f"Network Telemetry:\n- Local IP: **{ip}**\n- Wi-Fi SSID: **{wifi}**\n- Google Ping: **{ping}**"
        spoken = f"Boss, aapka network normal hai. Wi-Fi {wifi} connected hai aur local IP {ip} hai."
        return {
            "fast_path": True,
            "intent": intent,
            "response": resp,
            "spoken_text": clean_spoken_text(spoken),
            "action": action
        }

    # 13. Read Clipboard Content
    if intent == roman_engine.INTENT_READ_CLIPBOARD:
        action = system_control.get_clipboard_content()
        clip_text = action.get("content", "")
        if clip_text.strip():
            resp = f"Clipboard Content:\n```text\n{clip_text}\n```"
            spoken = f"Boss, clipboard mein {len(clip_text)} characters copy hain."
        else:
            resp = "Clipboard is currently empty, Boss."
            spoken = "Clipboard khali hai, Boss."
        return {
            "fast_path": True,
            "intent": intent,
            "response": resp,
            "spoken_text": clean_spoken_text(spoken),
            "action": action
        }

    # 14. Projects Directory
    if intent == roman_engine.INTENT_OPEN_PROJECTS:
        action = system_control.open_directory("projects")
        return {
            "fast_path": True,
            "intent": intent,
            "response": f"Opening your main projects directory at `{DEFAULT_PROJECTS_DIR}`, Boss.",
            "spoken_text": "Ji Boss, aapka main projects directory open kar diya hai.",
            "action": action
        }

    # 15. Obsidian Vault
    if intent == roman_engine.INTENT_OPEN_VAULT:
        action = system_control.open_directory("vault")
        return {
            "fast_path": True,
            "intent": intent,
            "response": f"Accessing your Obsidian engineering vault at `{DEFAULT_VAULT_DIR}`, Sir.",
            "spoken_text": "Sir, aapka Obsidian engineering vault access kar raha hoon.",
            "action": action
        }

    # 16. VS Code
    if intent == roman_engine.INTENT_LAUNCH_VSCODE:
        action = system_control.open_application("code")
        return {
            "fast_path": True,
            "intent": intent,
            "response": "Launching Visual Studio Code now, Sir.",
            "spoken_text": "Sir, Visual Studio Code launch kar diya hai.",
            "action": action
        }

    # 17. Google Chrome
    if intent == roman_engine.INTENT_LAUNCH_CHROME:
        action = system_control.open_application("chrome")
        return {
            "fast_path": True,
            "intent": intent,
            "response": "Opening Google Chrome, Boss.",
            "spoken_text": "Google Chrome open ho gaya hai, Boss.",
            "action": action
        }

    # 18. Notepad
    if intent == roman_engine.INTENT_LAUNCH_NOTEPAD:
        action = system_control.open_application("notepad")
        return {
            "fast_path": True,
            "intent": intent,
            "response": "Notepad is ready on your screen, Boss.",
            "spoken_text": "Ji Boss, Notepad ready hai aapke saamne.",
            "action": action
        }

    # 19. Calculator
    if intent == roman_engine.INTENT_LAUNCH_CALCULATOR:
        action = system_control.open_application("calc")
        return {
            "fast_path": True,
            "intent": intent,
            "response": "Opening Calculator, Sir.",
            "spoken_text": "Calculator open kar diya hai, Sir.",
            "action": action
        }

    # 20. Terminal
    if intent == roman_engine.INTENT_LAUNCH_TERMINAL:
        action = system_control.open_application("terminal")
        return {
            "fast_path": True,
            "intent": intent,
            "response": "Terminal session initiated, Boss.",
            "spoken_text": "Terminal session start ho chuki hai, Boss.",
            "action": action
        }

    # 20.1 Universal Generic Application Launcher
    if intent == roman_engine.INTENT_LAUNCH_GENERIC_APP:
        target_app = params.get("app_name", "")
        action = system_control.open_application(target_app)
        if action.get("success"):
            spoken = f"Ji Boss, {target_app} open kar diya hai."
            resp = f"Application **{target_app}** launched successfully, Boss."
        else:
            spoken = f"Boss, {target_app} launch karne mein issue aya hai."
            resp = f"Error launching {target_app}: {action.get('error')}"
        return {
            "fast_path": True,
            "intent": intent,
            "response": resp,
            "spoken_text": clean_spoken_text(spoken),
            "action": action
        }

    # 21. Battery Check
    if intent == roman_engine.INTENT_CHECK_BATTERY:
        metrics = system_control.get_system_metrics()
        bat = metrics.get("battery", {})
        percent = bat.get("percent", 0)
        plugged = bat.get("power_plugged", False)
        status_str = "Plugged in aur charging par" if plugged else "Battery power par"
        spoken = f"Boss, aapki Dell Latitude ki battery {percent} percent hai, aur device {status_str} hai."
        if percent >= 78 and plugged:
            spoken += " Dell Power Manager ka 80 percent threshold battery protect kar raha hai."
        return {
            "fast_path": True,
            "intent": intent,
            "response": f"Battery Telemetry: **{percent}%** ({status_str}). Hardware profile maintained.",
            "spoken_text": clean_spoken_text(spoken),
            "action": {"metrics": metrics}
        }

    # 22. System Diagnostics
    if intent == roman_engine.INTENT_CHECK_SYSTEM:
        metrics = system_control.get_system_metrics()
        cpu_p = metrics.get("cpu", {}).get("percent", 0)
        ram_p = metrics.get("memory", {}).get("percent", 0)
        ram_used = metrics.get("memory", {}).get("used_gb", 0)
        ram_total = metrics.get("memory", {}).get("total_gb", 0)
        bat_p = metrics.get("battery", {}).get("percent", 0)
        
        spoken = f"All systems normal hain Boss. CPU load {cpu_p} percent hai, aur RAM {ram_used} out of {ram_total} gigabytes active hai. Battery {bat_p} percent par hai."
        return {
            "fast_path": True,
            "intent": intent,
            "response": f"Diagnostics Summary:\n- CPU: **{cpu_p}%**\n- RAM: **{ram_used}GB / {ram_total}GB ({ram_p}%)**\n- Battery: **{bat_p}%**",
            "spoken_text": clean_spoken_text(spoken),
            "action": {"metrics": metrics}
        }

    # 23. Greetings
    if intent == roman_engine.INTENT_GREETING:
        reply = "Main bilkul first class hoon Boss! Dell Latitude 7420 par aapki service ke liye poori tarah tayyar. Hukm karein Sir."
        return {
            "fast_path": True,
            "intent": intent,
            "response": reply,
            "spoken_text": reply,
            "action": None
        }

    # 24. Identity - J.A.R.V.I.S.
    if intent == roman_engine.INTENT_WHO_ARE_YOU:
        intro = f"Main hoon J.A.R.V.I.S., aapka dedicated AI systems architect aur local assistant, Boss. Aapke Dell Latitude 7420 par chal raha hoon. AeroStudy, ResQ, freelance automation ya Windows OS control, jo bhi command dein."
        return {
            "fast_path": True,
            "intent": intent,
            "response": intro,
            "spoken_text": clean_spoken_text(intro),
            "action": None
        }

    # 25. Identity - User
    if intent == roman_engine.INTENT_WHO_AM_I:
        identity = f"Aap hain {USER_NAME}, known as {USER_NICKNAME}. Sukkur IBA University mein 6th semester CS ke student, software developer aur mere creator. Hamesha aapki service mein, Boss."
        return {
            "fast_path": True,
            "intent": intent,
            "response": identity,
            "spoken_text": clean_spoken_text(identity),
            "action": None
        }

    return None


# Complete Omnipotent System Tools Arsenal for Google Gemini Brain
ALL_JARVIS_TOOLS = [
    # Desktop & OS Command Execution
    system_control.open_application,
    system_control.open_directory,
    system_control.execute_terminal_command,
    system_control.execute_python_code,
    system_control.run_git_command,

    # Process & Task Management
    system_control.list_processes,
    system_control.kill_process,

    # Comprehensive Filesystem Omnipotence
    system_control.read_system_file,
    system_control.write_system_file,
    system_control.list_directory_contents,
    system_control.search_filesystem,
    system_control.delete_filesystem_item,
    system_control.copy_or_move_item,
    system_control.create_directory,

    # Hardware & Network Diagnostics
    system_control.get_system_metrics,
    system_control.get_network_telemetry,
    system_control.lock_workstation,
    system_control.empty_recycle_bin,
    system_control.capture_screen,

    # Clipboard Omnipotence
    system_control.get_clipboard_content,
    system_control.set_clipboard_content,

    # Software & Media Automation
    system_control.play_spotify,
    system_control.control_media,
    system_control.control_volume,
    system_control.send_whatsapp,
    system_control.play_youtube,
    system_control.search_google,

    # Backup & AI Copilot Engines
    backup_manager.create_backup,
    coding_copilot.generate_scraper
]


def get_or_create_chat(model_name: str):
    """
    Retrieves or establishes a persistent multi-turn chat session with Automatic
    Function Calling (AFC) across all 30 system control tools.
    """
    global active_chat_session, active_chat_model, genai_client
    if not genai_client:
        return None

    if active_chat_session is None or active_chat_model != model_name:
        try:
            config = types.GenerateContentConfig(
                system_instruction=JARVIS_SYSTEM_INSTRUCTION,
                temperature=0.7,
                tools=ALL_JARVIS_TOOLS
            )
            active_chat_session = genai_client.chats.create(
                model=model_name,
                config=config
            )
            active_chat_model = model_name
        except Exception as e:
            print(f"[CHAT INIT ERROR] Failed creating chat session with {model_name}: {e}")
            return None

    return active_chat_session


async def process_jarvis_query(query: str, chat_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    """
    Main cognitive engine. First checks for instantaneous fast-path commands.
    If none match, routes to Google Gemini multi-turn chat with Automatic Function Calling.
    """
    clean_query = query.strip()
    if not clean_query:
        return {
            "response": "Ji Boss, main sun raha hoon. Kya command hai?",
            "spoken_text": "Ji Boss, main sun raha hoon. Kya command hai?",
            "action": None
        }

    # 1. Evaluate Instant Fast-Path via Roman Engine
    fast_result = evaluate_fast_path(clean_query)
    if fast_result:
        return fast_result

    # 2. Check if Gemini Client is active
    global genai_client, active_chat_session
    if not genai_client:
        from config import GEMINI_API_KEY as CURRENT_KEY
        if CURRENT_KEY and CURRENT_KEY.strip() and CURRENT_KEY != "your_gemini_api_key_here":
            try:
                genai_client = genai.Client(api_key=CURRENT_KEY)
            except Exception:
                pass

    if not genai_client:
        fallback_msg = (
            "Boss, local system control tools 100% operational hain, lekin Google Gemini API key "
            "aapki `.env` file mein abhi set nahi hui. Direct voice commands jaise 'projects kholo', "
            "'spotify par gana lagao', 'whatsapp kholo', 'vscode chalao', ya 'battery batao' bilkul ready hain."
        )
        return {
            "response": fallback_msg,
            "spoken_text": "Boss, local system control tools operational hain. Spotify, WhatsApp, aur apps direct chal rahi hain.",
            "action": None
        }

    # 3. Route to Multi-Turn Cognitive Brain with Automatic Tool Calling
    try:
        normalized_query = roman_engine.normalize_roman_text(clean_query)
        models_to_try = [GEMINI_MODEL] + [m for m in GEMINI_MODELS_CASCADE if m != GEMINI_MODEL]

        loop = asyncio.get_event_loop()
        response = None
        used_model = None
        last_error = None

        for model_candidate in models_to_try:
            try:
                chat = get_or_create_chat(model_candidate)
                if not chat:
                    continue

                response = await loop.run_in_executor(
                    None,
                    lambda c=chat, q=normalized_query: c.send_message(q)
                )
                if response:
                    used_model = model_candidate
                    break
            except Exception as candidate_err:
                err_str = str(candidate_err)
                print(f"[CASCADE WARNING] Model '{model_candidate}' failed: {err_str[:120]}. Trying next candidate...")
                active_chat_session = None  # Reset session on failure to avoid poisoned state
                last_error = candidate_err
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "404" in err_str:
                    continue
                else:
                    break

        if not response:
            fallback_spoken = "Boss, Gemini API ki free quota limit reach ho chuki hai, lekin local software automation aur PC control poori tarah active hain. Aap koi bhi software, Spotify, ya folder command dein, main execute kar doonga."
            return {
                "response": (
                    "⚠️ **Google Gemini Free Quota Reached (429 RESOURCE_EXHAUSTED)**\n\n"
                    "Boss, Google Gemini API ke free tier ki request quota temporarily exhaust ho chuki hai. "
                    "Lekin aapka local **J.A.R.V.I.S. operating system** bilkul 100% active hai:\n"
                    "- ✅ **Processes:** Listing, monitoring & task kill\n"
                    "- ✅ **Filesystem:** Browse, search, read, write & delete\n"
                    "- ✅ **Spotify & Media:** Gane search & volume controls\n"
                    "- ✅ **WhatsApp:** Messages & contacts automation\n"
                    "- ✅ **Hardware & Telemetry:** Dell 80% battery threshold & network diagnostics\n\n"
                    "*Yeh saari local commands zero quota use karti hain aur sub-50ms mein execute hoti hain!*"
                ),
                "spoken_text": fallback_spoken,
                "action": {"quota_exceeded": True}
            }

        # Extract any executed function calls from the chat history for frontend telemetry
        executed_actions = []
        if active_chat_session:
            try:
                history = active_chat_session.get_history()
                for h in history[-4:]:
                    for p in h.parts:
                        if p.function_call:
                            executed_actions.append({
                                "tool": p.function_call.name,
                                "args": dict(p.function_call.args or {})
                            })
            except Exception:
                pass

        response_text = response.text if response and response.text else "Command executed successfully, Boss."
        spoken_version = clean_spoken_text(response_text)
        if len(spoken_version.split()) > 45:
            sentences = [s.strip() for s in spoken_version.split(".") if s.strip()]
            spoken_version = ". ".join(sentences[:2]) + ". Complete details display screen par hain, Boss."

        return {
            "response": response_text,
            "spoken_text": spoken_version,
            "action": executed_actions if executed_actions else None
        }

    except Exception as e:
        error_msg = f"Neural processing error: {str(e)}"
        print(f"[JARVIS BRAIN ERROR] {error_msg}")
        return {
            "response": f"Apologies Boss, connection issue aya hai: `{str(e)}`",
            "spoken_text": "Apologies Boss, neural connection mein issue aya hai.",
            "action": {"error": str(e)}
        }
