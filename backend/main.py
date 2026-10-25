"""
J.A.R.V.I.S. Core FastAPI Server
Acts as the central operational bridge between the holographic frontend,
local Windows 11 system tools, and Google Gemini AI brain.
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from config import (
    HOST,
    PORT,
    DEBUG,
    GEMINI_API_KEY,
    ELEVENLABS_API_KEY,
    USER_NAME,
    USER_NICKNAME,
    PROJECT_ROOT
)
import system_control
import ai_brain
import tts_provider
import backup_manager
import coding_copilot

# Setup Directories
FRONTEND_DIR = PROJECT_ROOT / "frontend"
CACHE_AUDIO_DIR = FRONTEND_DIR / "cache_audio"
CACHE_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Initialize FastAPI App
app = FastAPI(
    title="J.A.R.V.I.S. OS",
    description="Tony Stark inspired local AI assistant and Windows 11 automation hub for Shazil Ahmed Shaikh.",
    version="3.8.0"
)

# Enable CORS for local web interactions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Frontend Static Assets
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
app.mount("/cache_audio", StaticFiles(directory=str(CACHE_AUDIO_DIR)), name="cache_audio")


# Request & Response Models
class ChatRequest(BaseModel):
    query: str
    voice_mode: bool = True
    use_elevenlabs: bool = False
    voice_id: Optional[str] = None
    chat_history: Optional[List[Dict[str, str]]] = None


class CommandRequest(BaseModel):
    command: str


class AppRequest(BaseModel):
    app_name: str


class FolderRequest(BaseModel):
    folder_target: str


class FileReadRequest(BaseModel):
    file_path: str


class FileWriteRequest(BaseModel):
    file_path: str
    content: str
    mode: str = "w"


class TTSRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None


class BackupRequest(BaseModel):
    target: str = "vault"


class ScraperRequest(BaseModel):
    url: str = "https://example.com"
    framework: str = "playwright"


class ProcessFilterRequest(BaseModel):
    filter_name: Optional[str] = None
    limit: int = 15


class ProcessKillRequest(BaseModel):
    target: str


class FSListRequest(BaseModel):
    folder_path: str = "projects"
    show_hidden: bool = False
    max_items: int = 50


class FSSearchRequest(BaseModel):
    search_term: str
    target_directory: Optional[str] = None
    max_results: int = 25


class FSDeleteRequest(BaseModel):
    target_path: str


class ClipboardSetRequest(BaseModel):
    text: str


class PythonExecRequest(BaseModel):
    code: str
    timeout_seconds: int = 20


class GitCommandRequest(BaseModel):
    command: str
    repo_path: Optional[str] = None


# ---------------- Background Tasks & Startup ---------------- #

@app.on_event("startup")
async def startup_event():
    """Starts background automation worker loop for scheduled backups."""
    asyncio.create_task(backup_manager.run_backup_scheduler_loop(interval_hours=12))


# ---------------- Root & Health Endpoints ---------------- #

@app.get("/")
async def serve_index():
    """Serves the main futuristic holographic J.A.R.V.I.S. interface."""
    index_file = FRONTEND_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Frontend index.html not found.")
    return FileResponse(str(index_file))


@app.get("/api/status")
async def get_status():
    """Returns J.A.R.V.I.S. system health, environment state, and active modules."""
    return {
        "system": "J.A.R.V.I.S. OS",
        "version": "4.0.0 OMNI",
        "status": "ONLINE",
        "user": {
            "name": USER_NAME,
            "nickname": USER_NICKNAME
        },
        "neural_core": {
            "gemini_active": bool(GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here"),
            "model": "gemini-flash-lite-latest (Cascade Enabled)"
        },
        "voice_engine": {
            "web_speech_api": "ENABLED (Continuous Wake-Word Detection on 'Jarvis')",
            "elevenlabs_active": bool(ELEVENLABS_API_KEY and ELEVENLABS_API_KEY != "your_elevenlabs_api_key_here")
        }
    }


@app.get("/api/system/metrics")
async def get_metrics():
    """Streams real-time CPU, RAM, Dell battery status, and storage metrics."""
    return system_control.get_system_metrics()


# ---------------- AI Interaction Endpoint ---------------- #

@app.post("/api/chat")
async def handle_chat(payload: ChatRequest):
    """
    Main communication channel. Analyzes query through fast-path heuristics
    or Gemini AI brain, executes local OS tools, and synthesizes spoken response.
    """
    try:
        result = await ai_brain.process_jarvis_query(
            query=payload.query,
            chat_history=payload.chat_history
        )

        audio_url = None
        spoken_text = result.get("spoken_text", "")

        # Generate hyper-realistic neural voice audio
        if payload.voice_mode and spoken_text:
            if payload.use_elevenlabs and ELEVENLABS_API_KEY and ELEVENLABS_API_KEY != "your_elevenlabs_api_key_here":
                tts_res = await tts_provider.synthesize_elevenlabs_speech(
                    text=spoken_text,
                    voice_id=payload.voice_id
                )
            else:
                tts_res = await tts_provider.synthesize_edge_speech(
                    text=spoken_text,
                    voice=payload.voice_id
                )

            if tts_res.get("success"):
                audio_url = tts_res.get("audio_url")

        return {
            "success": True,
            "response": result.get("response", ""),
            "spoken_text": spoken_text,
            "action": result.get("action"),
            "audio_url": audio_url
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Internal Jarvis runtime error: {str(e)}",
                "spoken_text": "An internal operational error occurred, Boss. Diagnostics logged."
            }
        )


# ---------------- Direct System Operations ---------------- #

@app.post("/api/system/command")
async def run_command(payload: CommandRequest):
    """Directly executes a PowerShell command on the Windows 11 host."""
    return system_control.execute_terminal_command(payload.command)


@app.post("/api/system/open-app")
async def launch_app(payload: AppRequest):
    """Launches an application by name or path."""
    return system_control.open_application(payload.app_name)


@app.post("/api/system/open-folder")
async def open_folder(payload: FolderRequest):
    """Opens a target directory in Windows Explorer."""
    return system_control.open_directory(payload.folder_target)


@app.post("/api/system/read-file")
async def read_file(payload: FileReadRequest):
    """Reads a file from the local filesystem."""
    return system_control.read_system_file(payload.file_path)


@app.post("/api/system/write-file")
async def write_file(payload: FileWriteRequest):
    """Writes content to a file on the local filesystem."""
    return system_control.write_system_file(
        file_path=payload.file_path,
        content=payload.content,
        mode=payload.mode
    )


@app.post("/api/tts/elevenlabs")
async def generate_tts(payload: TTSRequest):
    """Direct endpoint to synthesize ElevenLabs speech audio."""
    return await tts_provider.synthesize_elevenlabs_speech(
        text=payload.text,
        voice_id=payload.voice_id
    )


# ---------------- Backup & Copilot Endpoints ---------------- #

@app.post("/api/backup/create")
async def create_backup_endpoint(payload: Optional[BackupRequest] = None):
    """Generates a compressed zip backup archive for 'vault' or 'projects'."""
    target = payload.target if payload else "vault"
    return backup_manager.create_backup(target)


@app.get("/api/backup/list")
async def list_backups_endpoint():
    """Lists all available backup archives with file sizes and timestamps."""
    return backup_manager.list_backups()


@app.post("/api/copilot/generate-scraper")
async def generate_scraper_endpoint(payload: ScraperRequest):
    """Generates production-grade anti-bot Playwright or BeautifulSoup scraping script."""
    return coding_copilot.generate_scraper(url=payload.url, framework=payload.framework)


# ---------------- Advanced System Administration Endpoints ---------------- #

@app.post("/api/system/process/list")
async def list_processes_endpoint(payload: Optional[ProcessFilterRequest] = None):
    """Lists running processes with CPU & RAM telemetry."""
    f = payload.filter_name if payload else None
    lim = payload.limit if payload else 15
    return system_control.list_processes(filter_name=f, limit=lim)


@app.post("/api/system/process/kill")
async def kill_process_endpoint(payload: ProcessKillRequest):
    """Terminates a process by name or PID."""
    return system_control.kill_process(target=payload.target)


@app.post("/api/system/fs/list")
async def list_fs_endpoint(payload: Optional[FSListRequest] = None):
    """Lists files and folders in a directory."""
    folder = payload.folder_path if payload else "projects"
    hidden = payload.show_hidden if payload else False
    lim = payload.max_items if payload else 50
    return system_control.list_directory_contents(folder_path=folder, show_hidden=hidden, max_items=lim)


@app.post("/api/system/fs/search")
async def search_fs_endpoint(payload: FSSearchRequest):
    """Recursively searches for files or folders matching a query."""
    return system_control.search_filesystem(
        search_term=payload.search_term,
        target_directory=payload.target_directory,
        max_results=payload.max_results
    )


@app.post("/api/system/fs/delete")
async def delete_fs_endpoint(payload: FSDeleteRequest):
    """Safely deletes a file or directory with guardrails."""
    return system_control.delete_filesystem_item(target_path=payload.target_path)


@app.get("/api/system/clipboard")
async def get_clipboard_endpoint():
    """Reads current clipboard content."""
    return system_control.get_clipboard_content()


@app.post("/api/system/clipboard")
async def set_clipboard_endpoint(payload: ClipboardSetRequest):
    """Sets clipboard content."""
    return system_control.set_clipboard_content(text=payload.text)


@app.get("/api/system/network")
async def get_network_endpoint():
    """Returns real-time network, Wi-Fi SSID, and ping latency telemetry."""
    return system_control.get_network_telemetry()


@app.post("/api/system/lock")
async def lock_system_endpoint():
    """Locks Windows 11 workstation."""
    return system_control.lock_workstation()


@app.post("/api/system/recycle-bin/empty")
async def empty_recycle_bin_endpoint():
    """Empties the Windows Recycle Bin."""
    return system_control.empty_recycle_bin()


@app.post("/api/system/python/run")
async def run_python_endpoint(payload: PythonExecRequest):
    """Executes a dynamic Python snippet in an isolated subprocess."""
    return system_control.execute_python_code(code=payload.code, timeout_seconds=payload.timeout_seconds)


@app.post("/api/system/git")
async def run_git_endpoint(payload: GitCommandRequest):
    """Executes a Git command in a local repository."""
    return system_control.run_git_command(command=payload.command, repo_path=payload.repo_path)


# ---------------- Server Runner ---------------- #

if __name__ == "__main__":
    import uvicorn
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass
    print("\n=======================================================")
    print("  [+] J.A.R.V.I.S. ONLINE FOR SHAZIL AHMED SHAIKH")
    print(f"  Target Hardware: Dell Latitude 7420 (Windows 11)")
    print(f"  Local HUD: http://{HOST}:{PORT}")
    print("=======================================================\n")
    uvicorn.run("main:app", host=HOST, port=PORT, reload=False)
