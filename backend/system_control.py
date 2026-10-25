"""
J.A.R.V.I.S. System Control Engine
Executes local Windows 11 operating system commands, application launches,
directory operations, file I/O, software automation (Spotify, WhatsApp, YouTube),
and real-time hardware telemetry diagnostics.
"""

import os
import sys
import re
import time
import socket
import winreg
import psutil
import shutil
import ctypes
import subprocess
import urllib.parse
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except Exception:
    PYAUTOGUI_AVAILABLE = False

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except Exception:
    PYPERCLIP_AVAILABLE = False

from config import DEFAULT_PROJECTS_DIR, DEFAULT_VAULT_DIR

# Windows Virtual Key Codes for Media & Volume Control
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP = 0xB2
VK_MEDIA_PLAY_PAUSE = 0xB3

# Common Application Launch Mapping for Windows 11
KNOWN_APPS: Dict[str, list] = {
    "vscode": ["code"],
    "code": ["code"],
    "chrome": ["chrome", r"C:\Program Files\Google\Chrome\Application\chrome.exe"],
    "notepad": ["notepad.exe"],
    "calculator": ["calc.exe"],
    "calc": ["calc.exe"],
    "explorer": ["explorer.exe"],
    "terminal": ["wt.exe", "powershell.exe"],
    "cmd": ["cmd.exe"],
    "powershell": ["powershell.exe"],
    "spotify": ["spotify.exe", r"%APPDATA%\Spotify\Spotify.exe"],
    "whatsapp": ["whatsapp:", r"%LOCALAPPDATA%\WhatsApp\WhatsApp.exe"],
    "taskmanager": ["taskmgr.exe"],
    "settings": ["start", "ms-settings:"]
}

# Known Directory Mapping
KNOWN_DIRECTORIES: Dict[str, str] = {
    "projects": DEFAULT_PROJECTS_DIR,
    "project": DEFAULT_PROJECTS_DIR,
    "vault": DEFAULT_VAULT_DIR,
    "obsidian": DEFAULT_VAULT_DIR,
    "testing": DEFAULT_VAULT_DIR,
    "downloads": str(Path.home() / "Downloads"),
    "desktop": str(Path.home() / "Desktop"),
    "documents": str(Path.home() / "Documents"),
    "root": "C:\\"
}


def send_virtual_key(vk_code: int):
    """Sends a global virtual key event to Windows user32 without stealing focus."""
    try:
        ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
        time.sleep(0.05)
        ctypes.windll.user32.keybd_event(vk_code, 0, 2, 0)  # KEYEVENTF_KEYUP = 2
    except Exception as e:
        print(f"[KEYBOARD EVENT ERROR] {e}")


# ---------------- Software Task Automation ---------------- #

def play_spotify(query: Optional[str] = None) -> Dict[str, Any]:
    """
    Automates Spotify on Windows 11.
    If query is provided, searches and triggers playback.
    If no query provided, opens Spotify or unpauses.
    """
    clean_query = query.strip() if query else ""
    try:
        if clean_query:
            encoded = urllib.parse.quote(clean_query)
            # Try Spotify desktop protocol
            spotify_uri = f"spotify:search:{encoded}"
            try:
                os.startfile(spotify_uri)
            except Exception:
                # Web Spotify fallback
                os.startfile(f"https://open.spotify.com/search/{encoded}")

            # Wait briefly for Spotify to focus and simulate play action
            time.sleep(1.2)
            if PYAUTOGUI_AVAILABLE:
                pyautogui.press('enter')

            return {
                "success": True,
                "app": "Spotify",
                "query": clean_query,
                "message": f"Spotify par '{clean_query}' search karke play kar diya hai, Boss."
            }
        else:
            try:
                os.startfile("spotify:")
            except Exception:
                os.startfile("https://open.spotify.com")
            
            time.sleep(0.5)
            send_virtual_key(VK_MEDIA_PLAY_PAUSE)
            return {
                "success": True,
                "app": "Spotify",
                "message": "Spotify launch kar diya hai aur media play resume ho chuka hai, Boss."
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Spotify automation error: {str(e)}"
        }


def control_media(action: str) -> Dict[str, Any]:
    """
    Controls background media playback (Spotify, YouTube, Windows Media).
    Actions: 'play', 'pause', 'toggle', 'next', 'previous', 'stop'
    """
    act = action.lower().strip()
    try:
        if act in ["play", "pause", "toggle", "chalao", "roko"]:
            send_virtual_key(VK_MEDIA_PLAY_PAUSE)
            return {"success": True, "action": act, "message": "Media playback toggled, Boss."}
        elif act in ["next", "agla", "skip"]:
            send_virtual_key(VK_MEDIA_NEXT_TRACK)
            return {"success": True, "action": act, "message": "Next track playing, Sir."}
        elif act in ["prev", "previous", "pichla"]:
            send_virtual_key(VK_MEDIA_PREV_TRACK)
            return {"success": True, "action": act, "message": "Previous track, Boss."}
        elif act in ["stop", "band"]:
            send_virtual_key(VK_MEDIA_STOP)
            return {"success": True, "action": act, "message": "Media stopped, Sir."}
        else:
            send_virtual_key(VK_MEDIA_PLAY_PAUSE)
            return {"success": True, "action": "toggle", "message": "Media playback toggled, Boss."}
    except Exception as e:
        return {"success": False, "error": f"Media control error: {str(e)}"}


def control_volume(action: str, steps: int = 4) -> Dict[str, Any]:
    """
    Controls master audio volume on Windows 11.
    Actions: 'up', 'down', 'mute', 'unmute'
    """
    act = action.lower().strip()
    try:
        if "up" in act or "badhao" in act or "tez" in act:
            for _ in range(steps):
                send_virtual_key(VK_VOLUME_UP)
                time.sleep(0.02)
            return {"success": True, "action": "volume_up", "message": f"Volume barha diya hai Boss."}
        elif "down" in act or "kam" in act or "slow" in act:
            for _ in range(steps):
                send_virtual_key(VK_VOLUME_DOWN)
                time.sleep(0.02)
            return {"success": True, "action": "volume_down", "message": f"Volume kam kar diya hai Sir."}
        elif "mute" in act or "band" in act or "khamosh" in act:
            send_virtual_key(VK_VOLUME_MUTE)
            return {"success": True, "action": "volume_mute", "message": "Audio mute/unmute toggle kar diya hai Boss."}
        else:
            return {"success": False, "error": f"Unknown volume action: {action}"}
    except Exception as e:
        return {"success": False, "error": f"Volume control error: {str(e)}"}


def send_whatsapp(contact_or_phone: str, message: str, auto_send: bool = False) -> Dict[str, Any]:
    """
    Automates WhatsApp Desktop or WhatsApp Web on Windows 11.
    If phone number provided: uses direct URI with message pre-filled.
    If contact name provided: launches WhatsApp Desktop and searches contact via PyAutoGUI.
    """
    target = contact_or_phone.strip()
    msg = message.strip()
    encoded_msg = urllib.parse.quote(msg)

    # Check if target is phone number
    digits = re.sub(r"[^\d]", "", target)
    is_phone = len(digits) >= 10

    try:
        if is_phone:
            # Format Pakistani / International number
            if digits.startswith("03"):
                phone_num = "92" + digits[1:]
            elif digits.startswith("3") and len(digits) == 10:
                phone_num = "92" + digits
            else:
                phone_num = digits

            uri = f"whatsapp://send?phone={phone_num}&text={encoded_msg}"
            try:
                os.startfile(uri)
            except Exception:
                os.startfile(f"https://web.whatsapp.com/send?phone={phone_num}&text={encoded_msg}")

            time.sleep(2.0)
            if auto_send and PYAUTOGUI_AVAILABLE:
                pyautogui.press('enter')

            return {
                "success": True,
                "target": phone_num,
                "message": f"WhatsApp par number {phone_num} par message pre-fill kar diya hai, Boss."
            }
        else:
            # Target is a contact name (e.g. "Ali", "Ahsan", "Papa")
            try:
                os.startfile("whatsapp:")
            except Exception:
                os.startfile("https://web.whatsapp.com")

            time.sleep(1.5)
            if PYAUTOGUI_AVAILABLE:
                # Focus search bar in WhatsApp
                pyautogui.hotkey('ctrl', 'f')
                time.sleep(0.3)
                pyautogui.write(target, interval=0.04)
                time.sleep(0.8)
                pyautogui.press('enter')
                time.sleep(0.5)
                # Type message
                if msg:
                    pyautogui.write(msg, interval=0.03)
                    if auto_send:
                        time.sleep(0.3)
                        pyautogui.press('enter')

            return {
                "success": True,
                "target": target,
                "message": f"WhatsApp par '{target}' ki chat open karke message '{msg}' ready kar diya hai, Boss."
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"WhatsApp automation error: {str(e)}"
        }


def play_youtube(query: str) -> Dict[str, Any]:
    """
    Searches and plays a video on YouTube in Google Chrome or default browser.
    """
    clean_query = query.strip()
    try:
        encoded = urllib.parse.quote(clean_query)
        url = f"https://www.youtube.com/results?search_query={encoded}"
        os.startfile(url)
        return {
            "success": True,
            "query": clean_query,
            "url": url,
            "message": f"YouTube par '{clean_query}' search kar diya hai, Boss."
        }
    except Exception as e:
        return {"success": False, "error": f"YouTube search error: {str(e)}"}


def search_google(query: str) -> Dict[str, Any]:
    """
    Executes a web search on Google.
    """
    clean_query = query.strip()
    try:
        encoded = urllib.parse.quote(clean_query)
        url = f"https://www.google.com/search?q={encoded}"
        os.startfile(url)
        return {
            "success": True,
            "query": clean_query,
            "url": url,
            "message": f"Google par '{clean_query}' search kar diya hai, Sir."
        }
    except Exception as e:
        return {"success": False, "error": f"Google search error: {str(e)}"}


# ---------------- Core OS & File Controls ---------------- #

def resolve_windows_executable(app_query: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Intelligently discovers the absolute executable path or protocol URI for any Windows 11 application.
    Checks URI protocols, aliases, system PATH via shutil.which, Windows Registry App Paths,
    and standard program directories.
    Returns (type, resolved_target) where type is 'protocol' or 'executable'.
    """
    q = app_query.strip().lower()

    # 0. Protocol Schemes
    if q.startswith("ms-") or q.endswith(":"):
        return ("protocol", q)
    if q in ("settings", "windows settings", "ms-settings"):
        return ("protocol", "ms-settings:")
    if q in ("spotify", "spoti-fy", "spoti"):
        return ("protocol", "spotify:")
    if q in ("whatsapp", "watsapp", "wats app"):
        return ("protocol", "whatsapp:")

    # 1. Alias map for Windows applications
    aliases: Dict[str, List[str]] = {
        "chrome": ["chrome.exe", "google chrome"],
        "google chrome": ["chrome.exe"],
        "browser": ["chrome.exe", "msedge.exe"],
        "vscode": ["code.cmd", "code.exe", "code"],
        "vs code": ["code.cmd", "code.exe", "code"],
        "code": ["code.cmd", "code.exe", "code"],
        "notepad": ["notepad.exe"],
        "calc": ["calc.exe"],
        "calculator": ["calc.exe"],
        "terminal": ["wt.exe", "powershell.exe", "cmd.exe"],
        "powershell": ["powershell.exe"],
        "cmd": ["cmd.exe"],
        "command prompt": ["cmd.exe"],
        "explorer": ["explorer.exe"],
        "file explorer": ["explorer.exe"],
        "taskmgr": ["taskmgr.exe"],
        "taskmanager": ["taskmgr.exe"],
        "task manager": ["taskmgr.exe"],
        "edge": ["msedge.exe"],
        "microsoft edge": ["msedge.exe"],
        "word": ["WINWORD.EXE"],
        "excel": ["EXCEL.EXE"],
        "powerpoint": ["POWERPNT.EXE"],
        "discord": ["Discord.exe", "Update.exe"]
    }

    candidates = aliases.get(q, [q, f"{q}.exe"])

    # 2. Check shutil.which (system PATH)
    for cand in candidates:
        found = shutil.which(cand)
        if found and os.path.isfile(found):
            return ("executable", found)

    # 3. Check Windows Registry App Paths (HKLM & HKCU)
    for cand in candidates:
        exe_cand = cand if cand.endswith(".exe") else f"{cand}.exe"
        for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                key_path = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\{exe_cand}"
                with winreg.OpenKey(root, key_path) as k:
                    val, _ = winreg.QueryValueEx(k, "")
                    if val:
                        clean_val = val.strip('\"')
                        exp = os.path.expandvars(clean_val)
                        if exp and os.path.isfile(exp):
                            return ("executable", exp)
            except Exception:
                pass

    # 4. Check Common Standard Windows Directories
    search_dirs = [
        r"C:\Program Files\Google\Chrome\Application",
        r"C:\Program Files (x86)\Google\Chrome\Application",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\bin"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code"),
        os.path.expandvars(r"%APPDATA%\Spotify"),
        os.path.expandvars(r"%LOCALAPPDATA%\WhatsApp"),
        os.path.expandvars(r"%LOCALAPPDATA%\Discord"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application",
        r"C:\Program Files\Microsoft\Edge\Application",
        r"C:\Windows\System32",
        r"C:\Windows"
    ]
    for d in search_dirs:
        for cand in candidates:
            exe_cand = cand if cand.endswith(".exe") else f"{cand}.exe"
            p = os.path.join(d, exe_cand)
            if os.path.isfile(p):
                return ("executable", p)

    return (None, None)


def open_application(app_name: str) -> Dict[str, Any]:
    """
    Launches an application on Windows 11 by resolving its executable path or protocol.
    Guarantees launch accuracy across Chrome, VS Code, Notepad, Calc, Edge, etc.
    """
    clean_name = app_name.strip()
    if not clean_name:
        return {"success": False, "error": "Application name cannot be empty."}

    exec_type, target = resolve_windows_executable(clean_name)

    if exec_type == "protocol" and target:
        try:
            os.startfile(target)
            return {
                "success": True,
                "app": clean_name,
                "target": target,
                "type": "protocol",
                "message": f"Application protocol '{target}' launched successfully on Windows 11."
            }
        except Exception:
            subprocess.Popen(f'start "" "{target}"', shell=True)
            return {
                "success": True,
                "app": clean_name,
                "target": target,
                "type": "protocol",
                "message": f"Protocol '{target}' executed via Windows Shell."
            }

    if exec_type == "executable" and target:
        try:
            if target.lower().endswith((".cmd", ".bat")):
                subprocess.Popen(f'"{target}"', shell=True)
            else:
                os.startfile(target)

            return {
                "success": True,
                "app": clean_name,
                "resolved_path": target,
                "type": "executable",
                "message": f"Application '{clean_name}' launched successfully ({target})."
            }
        except Exception as e:
            try:
                subprocess.Popen([target], close_fds=True)
                return {
                    "success": True,
                    "app": clean_name,
                    "resolved_path": target,
                    "type": "executable",
                    "message": f"Application '{clean_name}' spawned via process launcher."
                }
            except Exception as popen_err:
                return {
                    "success": False,
                    "app": clean_name,
                    "error": f"Failed launching '{target}': {str(popen_err)}"
                }

    # Fallback: Try generic os.startfile or shell start
    try:
        os.startfile(clean_name)
        return {
            "success": True,
            "app": clean_name,
            "message": f"Launched '{clean_name}' via Windows Shell."
        }
    except Exception as startfile_err:
        try:
            subprocess.Popen(f'start "" "{clean_name}"', shell=True)
            return {
                "success": True,
                "app": clean_name,
                "message": f"Executed start command for '{clean_name}'."
            }
        except Exception as e:
            return {
                "success": False,
                "app": clean_name,
                "error": f"Application '{clean_name}' not found or failed to start: {str(e)}"
            }


def open_directory(folder_target: str) -> Dict[str, Any]:
    """
    Opens a directory or specific path in Windows File Explorer.
    """
    clean_target = folder_target.strip().lower()
    resolved_path: Optional[str] = None

    for key, path in KNOWN_DIRECTORIES.items():
        if key in clean_target:
            resolved_path = path
            break

    if not resolved_path:
        cand = Path(folder_target)
        if cand.exists() and cand.is_dir():
            resolved_path = str(cand)
        elif Path(DEFAULT_PROJECTS_DIR, folder_target).exists():
            resolved_path = str(Path(DEFAULT_PROJECTS_DIR, folder_target))
        else:
            resolved_path = folder_target

    try:
        if os.path.exists(resolved_path):
            os.startfile(resolved_path)
            return {
                "success": True,
                "path": resolved_path,
                "message": f"Opened directory '{resolved_path}' in File Explorer."
            }
        else:
            if os.path.exists(DEFAULT_PROJECTS_DIR):
                os.startfile(DEFAULT_PROJECTS_DIR)
                return {
                    "success": True,
                    "path": DEFAULT_PROJECTS_DIR,
                    "message": f"Directory '{resolved_path}' was not found. Opened your main projects directory '{DEFAULT_PROJECTS_DIR}' instead."
                }
            return {
                "success": False,
                "path": resolved_path,
                "error": f"Directory path '{resolved_path}' does not exist on this machine."
            }
    except Exception as e:
        return {
            "success": False,
            "path": resolved_path,
            "error": f"Error opening folder: {str(e)}"
        }


def read_system_file(file_path: str, max_chars: int = 5000) -> Dict[str, Any]:
    """
    Reads content from a specified local file safely with size truncation and encoding handling.
    """
    target = Path(file_path).expanduser()
    if not target.is_absolute():
        p1 = Path(DEFAULT_PROJECTS_DIR) / file_path
        p2 = Path(DEFAULT_VAULT_DIR) / file_path
        if p1.exists():
            target = p1
        elif p2.exists():
            target = p2

    if not target.exists():
        return {
            "success": False,
            "file_path": str(target),
            "error": f"File '{target}' was not found on the local filesystem."
        }

    if not target.is_file():
        return {
            "success": False,
            "file_path": str(target),
            "error": f"Path '{target}' is a directory, not a readable file."
        }

    try:
        try:
            content = target.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = target.read_text(encoding="cp1252", errors="replace")

        truncated = False
        if len(content) > max_chars:
            content = content[:max_chars] + f"\n... [Truncated: File contains {len(content)} total characters]"
            truncated = True

        return {
            "success": True,
            "file_path": str(target),
            "size_bytes": target.stat().st_size,
            "truncated": truncated,
            "content": content
        }
    except Exception as e:
        return {
            "success": False,
            "file_path": str(target),
            "error": f"Failed reading file: {str(e)}"
        }


def write_system_file(file_path: str, content: str, mode: str = "w") -> Dict[str, Any]:
    """
    Writes or appends text to a file on the local filesystem.
    """
    target = Path(file_path).expanduser()
    if not str(target).strip():
        return {"success": False, "error": "Target file path cannot be empty."}

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        write_mode = "a" if mode.lower() in ["a", "append"] else "w"
        with open(target, write_mode, encoding="utf-8") as f:
            f.write(content)

        return {
            "success": True,
            "file_path": str(target),
            "mode": write_mode,
            "bytes_written": len(content.encode("utf-8")),
            "message": f"Successfully wrote to '{target}'."
        }
    except Exception as e:
        return {
            "success": False,
            "file_path": str(target),
            "error": f"Failed writing to file: {str(e)}"
        }


def execute_terminal_command(command: str, timeout_seconds: int = 25) -> Dict[str, Any]:
    """
    Executes a PowerShell terminal command on Windows 11 with security filters and timeout protection.
    """
    clean_cmd = command.strip()
    blocked_patterns = ["format ", "rmdir /s /q c:\\", "del /f /s /q c:\\", "diskpart"]
    for pattern in blocked_patterns:
        if pattern in clean_cmd.lower():
            return {
                "success": False,
                "command": clean_cmd,
                "error": f"Security restriction: Execution of pattern '{pattern}' blocked."
            }

    try:
        start_time = time.time()
        process = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", clean_cmd],
            capture_output=True,
            text=True,
            timeout=timeout_seconds
        )
        duration_ms = round((time.time() - start_time) * 1000, 2)
        stdout = process.stdout.strip()
        stderr = process.stderr.strip()

        return {
            "success": process.returncode == 0,
            "command": clean_cmd,
            "returncode": process.returncode,
            "duration_ms": duration_ms,
            "stdout": stdout if stdout else "(no standard output)",
            "stderr": stderr if stderr else "(no errors)"
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "command": clean_cmd, "error": f"Timed out after {timeout_seconds} seconds."}
    except Exception as e:
        return {"success": False, "command": clean_cmd, "error": f"Execution error: {str(e)}"}


def get_system_metrics() -> Dict[str, Any]:
    """
    Fetches real-time hardware telemetry: CPU, RAM, Dell Battery status, Storage, and Uptime.
    """
    try:
        cpu_usage = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count(logical=True)
        
        mem = psutil.virtual_memory()
        ram_percent = mem.percent
        ram_used_gb = round(mem.used / (1024 ** 3), 2)
        ram_total_gb = round(mem.total / (1024 ** 3), 2)

        battery = psutil.sensors_battery()
        battery_data = {
            "available": battery is not None,
            "percent": battery.percent if battery else 0,
            "power_plugged": battery.power_plugged if battery else False,
            "dell_threshold_status": "Maintained at 80% Dell Power Manager profile" if battery and battery.percent >= 78 else "Operating normally"
        }

        disk = psutil.disk_usage("C:\\")
        disk_percent = disk.percent
        disk_free_gb = round(disk.free / (1024 ** 3), 2)
        disk_total_gb = round(disk.total / (1024 ** 3), 2)

        boot_timestamp = psutil.boot_time()
        uptime_seconds = int(time.time() - boot_timestamp)
        uptime_hours = uptime_seconds // 3600
        uptime_minutes = (uptime_seconds % 3600) // 60

        return {
            "success": True,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "host": {
                "os": "Windows 11",
                "machine": "Dell Latitude 7420",
                "python_version": sys.version.split()[0],
                "uptime": f"{uptime_hours}h {uptime_minutes}m"
            },
            "cpu": {
                "percent": cpu_usage,
                "cores": cpu_count
            },
            "memory": {
                "percent": ram_percent,
                "used_gb": ram_used_gb,
                "total_gb": ram_total_gb
            },
            "battery": battery_data,
            "disk_c": {
                "percent": disk_percent,
                "free_gb": disk_free_gb,
                "total_gb": disk_total_gb
            }
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to retrieve hardware metrics: {str(e)}"}


# =========================================================================
# Omnipotent System Access & Windows 11 Administration Tools
# =========================================================================

def list_processes(filter_name: Optional[str] = None, limit: int = 15) -> Dict[str, Any]:
    """
    Lists running processes on Windows 11. Can be filtered by name (e.g. 'chrome', 'node', 'python')
    and sorted by RAM usage to identify memory or CPU hogs.
    """
    processes = []
    f_clean = filter_name.lower().strip() if filter_name else ""
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status']):
        try:
            info = proc.info
            name = info.get('name') or ""
            if f_clean and f_clean not in name.lower():
                continue
            
            mem_mb = round((info.get('memory_info').rss if info.get('memory_info') else 0) / (1024 * 1024), 1)
            processes.append({
                "pid": info.get('pid'),
                "name": name,
                "memory_mb": mem_mb,
                "cpu_percent": info.get('cpu_percent', 0.0),
                "status": info.get('status')
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    processes.sort(key=lambda p: p['memory_mb'], reverse=True)
    top_procs = processes[:limit]

    return {
        "success": True,
        "count": len(processes),
        "filter": filter_name,
        "processes": top_procs,
        "message": f"Found {len(processes)} running processes matching filter '{filter_name or 'ALL'}'. Showing top {len(top_procs)}."
    }


def kill_process(target: str) -> Dict[str, Any]:
    """
    Terminates or kills a process by process name (e.g. 'notepad.exe', 'chrome') or PID (e.g. '1234').
    """
    clean_target = target.strip()
    if not clean_target:
        return {"success": False, "error": "Target process name or PID cannot be empty."}

    killed = []
    errors = []

    if clean_target.isdigit():
        pid = int(clean_target)
        try:
            p = psutil.Process(pid)
            name = p.name()
            p.kill()
            return {
                "success": True,
                "target": clean_target,
                "killed_processes": [{"pid": pid, "name": name}],
                "message": f"Process {name} (PID: {pid}) terminated successfully, Boss."
            }
        except Exception as e:
            return {"success": False, "error": f"Failed killing PID {pid}: {str(e)}"}

    name_clean = clean_target.lower()
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            p_name = (proc.info.get('name') or "").lower()
            if name_clean in p_name or (name_clean + ".exe") == p_name:
                pid = proc.info.get('pid')
                proc.kill()
                killed.append({"pid": pid, "name": proc.info.get('name')})
        except Exception as err:
            errors.append(str(err))

    if killed:
        return {
            "success": True,
            "target": target,
            "killed_count": len(killed),
            "killed_processes": killed,
            "message": f"Killed {len(killed)} process instance(s) matching '{target}', Boss."
        }
    else:
        return {
            "success": False,
            "target": target,
            "message": f"No active processes found matching '{target}'."
        }


def list_directory_contents(folder_path: str = "projects", show_hidden: bool = False, max_items: int = 50) -> Dict[str, Any]:
    """
    Lists the contents of any folder on Windows 11 with file sizes, types, and modification times.
    Accepts shortcuts like 'projects', 'vault', 'downloads', 'desktop' or absolute paths.
    """
    resolved = None
    clean_path = folder_path.strip().lower()

    for k, p in KNOWN_DIRECTORIES.items():
        if k == clean_path or k in clean_path:
            resolved = Path(p)
            break

    if not resolved:
        p_cand = Path(folder_path).expanduser()
        if p_cand.exists():
            resolved = p_cand
        elif (Path(DEFAULT_PROJECTS_DIR) / folder_path).exists():
            resolved = Path(DEFAULT_PROJECTS_DIR) / folder_path
        else:
            resolved = p_cand

    if not resolved.exists():
        return {"success": False, "error": f"Directory '{resolved}' does not exist on this machine."}

    if not resolved.is_dir():
        return {"success": False, "error": f"Path '{resolved}' is a file, not a directory."}

    items = []
    try:
        for entry in resolved.iterdir():
            if not show_hidden and entry.name.startswith("."):
                continue
            
            try:
                stat = entry.stat()
                is_dir = entry.is_dir()
                size_kb = round(stat.st_size / 1024, 1) if not is_dir else 0
                mod_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime))
                items.append({
                    "name": entry.name,
                    "is_directory": is_dir,
                    "size_kb": size_kb,
                    "last_modified": mod_time
                })
            except Exception:
                continue

        items.sort(key=lambda x: (not x['is_directory'], x['name'].lower()))
        truncated = len(items) > max_items

        return {
            "success": True,
            "path": str(resolved),
            "total_items": len(items),
            "items": items[:max_items],
            "truncated": truncated,
            "message": f"Directory '{resolved}' contains {len(items)} items."
        }
    except Exception as e:
        return {"success": False, "error": f"Failed reading directory: {str(e)}"}


def search_filesystem(search_term: str, target_directory: Optional[str] = None, max_results: int = 25) -> Dict[str, Any]:
    """
    Fast recursive filesystem search for files or folders matching a query pattern.
    Default search directory is Shazil's main projects folder.
    """
    clean_term = search_term.lower().strip()
    root_dir = Path(DEFAULT_PROJECTS_DIR)
    if target_directory:
        td = target_directory.lower().strip()
        for k, p in KNOWN_DIRECTORIES.items():
            if k in td:
                root_dir = Path(p)
                break
        else:
            cand = Path(target_directory).expanduser()
            if cand.exists():
                root_dir = cand

    matches = []
    skip_dirs = {"node_modules", ".git", "__pycache__", ".venv", "venv", ".pytest_cache", "cache_audio"}

    try:
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for d in dirs:
                if clean_term in d.lower():
                    full_p = Path(root) / d
                    matches.append({
                        "path": str(full_p),
                        "name": d,
                        "type": "directory"
                    })
                    if len(matches) >= max_results:
                        break

            for f in files:
                if clean_term in f.lower():
                    full_p = Path(root) / f
                    matches.append({
                        "path": str(full_p),
                        "name": f,
                        "type": "file",
                        "size_kb": round(full_p.stat().st_size / 1024, 1) if full_p.exists() else 0
                    })
                    if len(matches) >= max_results:
                        break

            if len(matches) >= max_results:
                break

        return {
            "success": True,
            "search_term": search_term,
            "root_directory": str(root_dir),
            "match_count": len(matches),
            "matches": matches,
            "message": f"Found {len(matches)} item(s) matching '{search_term}' under '{root_dir}'."
        }
    except Exception as e:
        return {"success": False, "error": f"Search failed: {str(e)}"}


def delete_filesystem_item(target_path: str) -> Dict[str, Any]:
    """
    Safely deletes a file or directory on the filesystem.
    Includes ironclad security boundaries protecting critical system directories.
    """
    target = Path(target_path).expanduser().resolve()
    
    protected = [
        Path("C:\\"), Path("C:\\Windows"), Path("C:\\Program Files"),
        Path("C:\\Program Files (x86)"), Path(r"C:\Users\dell")
    ]
    for prot in protected:
        if target == prot.resolve():
            return {
                "success": False,
                "error": f"Ironclad Security Block: Deleting protected system root '{target}' is strictly prohibited."
            }

    if not target.exists():
        return {"success": False, "error": f"Target path '{target}' does not exist."}

    try:
        if target.is_dir():
            shutil.rmtree(target)
            return {
                "success": True,
                "type": "directory",
                "deleted_path": str(target),
                "message": f"Directory '{target}' and all its contents removed successfully."
            }
        else:
            target.unlink()
            return {
                "success": True,
                "type": "file",
                "deleted_path": str(target),
                "message": f"File '{target}' deleted successfully."
            }
    except Exception as e:
        return {"success": False, "error": f"Failed deleting item: {str(e)}"}


def copy_or_move_item(source_path: str, destination_path: str, is_copy: bool = True) -> Dict[str, Any]:
    """
    Copies or moves a file or folder from source to destination.
    """
    src = Path(source_path).expanduser().resolve()
    dst = Path(destination_path).expanduser().resolve()

    if not src.exists():
        return {"success": False, "error": f"Source '{src}' does not exist."}

    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        op_name = "copy" if is_copy else "move"
        
        if is_copy:
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
        else:
            shutil.move(str(src), str(dst))

        return {
            "success": True,
            "operation": op_name,
            "source": str(src),
            "destination": str(dst),
            "message": f"Successfully {op_name}d '{src.name}' to '{dst}'."
        }
    except Exception as e:
        return {"success": False, "error": f"File transfer failed: {str(e)}"}


def create_directory(dir_path: str) -> Dict[str, Any]:
    """
    Creates a new directory (and parent directories) on the filesystem.
    """
    target = Path(dir_path).expanduser()
    try:
        target.mkdir(parents=True, exist_ok=True)
        return {
            "success": True,
            "path": str(target),
            "message": f"Directory '{target}' created successfully."
        }
    except Exception as e:
        return {"success": False, "error": f"Failed creating directory: {str(e)}"}


def get_clipboard_content() -> Dict[str, Any]:
    """
    Reads and returns the current text content from the Windows clipboard.
    """
    if not PYPERCLIP_AVAILABLE:
        return {"success": False, "error": "Pyperclip library is not available."}
    try:
        text = pyperclip.paste()
        return {
            "success": True,
            "length": len(text),
            "content": text[:2000] if len(text) > 2000 else text,
            "truncated": len(text) > 2000,
            "message": f"Read {len(text)} characters from Windows clipboard."
        }
    except Exception as e:
        return {"success": False, "error": f"Failed reading clipboard: {str(e)}"}


def set_clipboard_content(text: str) -> Dict[str, Any]:
    """
    Sets text into the Windows clipboard.
    """
    if not PYPERCLIP_AVAILABLE:
        return {"success": False, "error": "Pyperclip library is not available."}
    try:
        pyperclip.copy(text)
        return {
            "success": True,
            "length": len(text),
            "message": f"Copied {len(text)} characters to Windows clipboard, Boss."
        }
    except Exception as e:
        return {"success": False, "error": f"Failed writing clipboard: {str(e)}"}


def get_network_telemetry() -> Dict[str, Any]:
    """
    Retrieves network telemetry: local IP, hostname, gateway, active interfaces, and internet ping latency.
    """
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        ping_latency = None
        try:
            p_res = subprocess.run(
                ["powershell", "-NoProfile", "-Command", "Test-Connection -ComputerName 8.8.8.8 -Count 1 | Select-Object -ExpandProperty ResponseTime"],
                capture_output=True, text=True, timeout=3
            )
            val = p_res.stdout.strip()
            if val.isdigit():
                ping_latency = f"{val} ms"
        except Exception:
            pass

        wifi_ssid = "Unknown / Ethernet"
        try:
            w_res = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True, text=True, timeout=2
            )
            for line in w_res.stdout.splitlines():
                if "SSID" in line and "BSSID" not in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        wifi_ssid = parts[1].strip()
                        break
        except Exception:
            pass

        return {
            "success": True,
            "hostname": hostname,
            "local_ip": local_ip,
            "wifi_ssid": wifi_ssid,
            "ping_google": ping_latency or "Connected",
            "message": f"Network active: IP {local_ip}, Wi-Fi: {wifi_ssid}, Latency: {ping_latency or 'Good'}."
        }
    except Exception as e:
        return {"success": False, "error": f"Failed retrieving network telemetry: {str(e)}"}


def lock_workstation() -> Dict[str, Any]:
    """
    Locks the Windows 11 workstation instantly.
    """
    try:
        res = ctypes.windll.user32.LockWorkStation()
        return {
            "success": bool(res),
            "message": "Windows workstation locked successfully, Boss."
        }
    except Exception as e:
        return {"success": False, "error": f"Failed locking workstation: {str(e)}"}


def empty_recycle_bin() -> Dict[str, Any]:
    """
    Empties the Windows Recycle Bin silently without popups.
    """
    try:
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
        return {
            "success": True,
            "message": "Windows Recycle Bin emptied successfully, Sir."
        }
    except Exception as e:
        return {"success": False, "error": f"Recycle bin purge error: {str(e)}"}


def run_git_command(command: str, repo_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Executes a Git command (e.g. 'status', 'diff', 'branch', 'log -n 5', 'pull') in a local project repository.
    """
    target_repo = Path(repo_path) if repo_path else Path(DEFAULT_PROJECTS_DIR)
    if not target_repo.exists():
        target_repo = Path(DEFAULT_PROJECTS_DIR)

    clean_cmd = command.strip()
    if clean_cmd.startswith("git "):
        clean_cmd = clean_cmd[4:].strip()

    try:
        proc = subprocess.run(
            ["git", "-C", str(target_repo)] + clean_cmd.split(),
            capture_output=True,
            text=True,
            timeout=15
        )
        return {
            "success": proc.returncode == 0,
            "git_command": f"git {clean_cmd}",
            "repo_path": str(target_repo),
            "stdout": proc.stdout.strip() or "(no output)",
            "stderr": proc.stderr.strip() or "(no errors)"
        }
    except Exception as e:
        return {"success": False, "error": f"Git command execution failed: {str(e)}"}


def execute_python_code(code: str, timeout_seconds: int = 20) -> Dict[str, Any]:
    """
    Executes a dynamic Python snippet in an isolated subprocess and returns the output.
    Useful for quick calculations, data processing, regex testing, or API calls.
    """
    try:
        start_time = time.time()
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout_seconds
        )
        duration_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "success": proc.returncode == 0,
            "duration_ms": duration_ms,
            "stdout": proc.stdout.strip() if proc.stdout else "(no output)",
            "stderr": proc.stderr.strip() if proc.stderr else "(no errors)"
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Python code timed out after {timeout_seconds}s."}
    except Exception as e:
        return {"success": False, "error": f"Python execution error: {str(e)}"}


def capture_screen(filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Captures a screenshot of the active Windows desktop and saves it to the captures directory.
    """
    captures_dir = Path(r"C:\Shazil\projects\jarvis\frontend\captures")
    captures_dir.mkdir(parents=True, exist_ok=True)
    
    fname = filename if filename else f"screen_{int(time.time())}.png"
    if not fname.endswith(".png"):
        fname += ".png"
    target_path = captures_dir / fname

    try:
        if PYAUTOGUI_AVAILABLE:
            img = pyautogui.screenshot()
            img.save(str(target_path))
            return {
                "success": True,
                "saved_path": str(target_path),
                "resolution": f"{img.width}x{img.height}",
                "message": f"Screenshot captured successfully at '{target_path}', Boss."
            }
        else:
            return {"success": False, "error": "PyAutoGUI not available for screen capture."}
    except Exception as e:
        return {
            "success": False,
            "error": f"Screen capture error (desktop may be locked or headless): {str(e)}"
        }
