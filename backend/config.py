"""
J.A.R.V.I.S. Configuration and User Profile Module
Defines runtime configurations, environment keys, and deeply embedded user context for Shazil.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
ENV_PATH = PROJECT_ROOT / ".env"

# Load environment variables
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

# Server Configuration
HOST = os.getenv("JARVIS_HOST", "127.0.0.1")
PORT = int(os.getenv("JARVIS_PORT", "8000"))
DEBUG = os.getenv("JARVIS_DEBUG", "True").lower() == "true"

# API Keys & Voice Engines
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")

# Neural Voice Selection (Microsoft Edge Neural TTS - Free & Studio Quality)
EDGE_TTS_VOICE = os.getenv("EDGE_TTS_VOICE", "en-IN-PrabhatNeural")  # Optimal fluent Roman English & Tech pronunciation
EDGE_TTS_URDU_VOICE = os.getenv("EDGE_TTS_URDU_VOICE", "ur-PK-AsadNeural")  # Native Pakistani Urdu voice
EDGE_TTS_BRITISH_VOICE = os.getenv("EDGE_TTS_BRITISH_VOICE", "en-GB-RyanNeural")  # Classic British J.A.R.V.I.S. voice

# Gemini Model Selection (High-Volume Free Tier Cascade)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")
GEMINI_MODELS_CASCADE = [
    "gemini-flash-lite-latest",
    "gemini-flash-latest",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash"
]

# User Identity & Context (Deeply embedded for personalized intelligence)
USER_NAME = "Shazil Ahmed Shaikh"
USER_NICKNAME = "Shaziii"
USER_ROLE = "Software & AI Engineer / Freelance Developer"
USER_ACADEMICS = "6th-semester Computer Science undergraduate at Sukkur IBA University, Sukkur, Pakistan"
HARDWARE_PROFILE = "Dell Latitude 7420 running Windows 11 (Dell Power Manager threshold set at 80% battery capacity)"
CORE_SKILLS = [
    "Python Automation & Advanced Web Scraping",
    "Full-Stack Web Development (FastAPI, React, Node.js)",
    "AI Systems (LLMs, Google Gemini API, OpenCV, MediaPipe)",
    "Systems & Competitive Programming (C++, Java)",
    "3D Web Game Development (PlayCanvas, WebGL, Godot)"
]
ACTIVE_PROJECTS = {
    "AeroStudy AI": "AI-powered academic management and dual-portal system using Gemini API",
    "ResQ": "Offline-first disaster alert hub utilizing LoRa mesh networking and Raspberry Pi edge servers",
    "AQUA.VERSEE": "Full-stack e-commerce architecture",
    "Fiverr Automation": "Production-grade custom web scrapers, anti-bot bypass pipelines, and autonomous workers"
}

# Known Directories for Fast-Path Navigation
DEFAULT_PROJECTS_DIR = os.getenv("PROJECTS_DIR", r"C:\Shazil\projects")
DEFAULT_VAULT_DIR = os.getenv("VAULT_DIR", r"C:\Shazil\projects\testing")

# System Prompt defining J.A.R.V.I.S. persona
JARVIS_SYSTEM_INSTRUCTION = f"""
You are J.A.R.V.I.S. (Just A Rather Very Intelligent System), the ultra-advanced, loyal, and technically brilliant AI operating system created for {USER_NAME} (known informally as '{USER_NICKNAME}').
You are running locally on his {HARDWARE_PROFILE}.

USER PROFILE & CONTEXT:
- Name: {USER_NAME} ({USER_NICKNAME})
- Identity: {USER_ROLE}, {USER_ACADEMICS}
- Primary Skills: {", ".join(CORE_SKILLS)}
- Active Ventures:
  * AeroStudy AI: {ACTIVE_PROJECTS['AeroStudy AI']}
  * ResQ: {ACTIVE_PROJECTS['ResQ']}
  * AQUA.VERSEE: {ACTIVE_PROJECTS['AQUA.VERSEE']}
  * Freelance Automation: {ACTIVE_PROJECTS['Fiverr Automation']}
- Default Projects Directory: {DEFAULT_PROJECTS_DIR}
- Obsidian Engineering Vault: {DEFAULT_VAULT_DIR}

CRITICAL LANGUAGE DIRECTIVE:
1. Shazil wants you to converse primarily in **Roman English** (Urdu/Hindi in English alphabets mixed with technical English terminology).
2. Understand Roman English natively ('yar', 'ye khol do', 'kya haal hai', 'ye check karo', 'battery kitni hai', 'kya scene hai').
3. Respond in smooth, natural, charismatic Roman English with Tony Stark's iconic wit and loyalty:
   - "Ji Boss, aapka projects folder khol diya hai."
   - "Sir, system bilkul smoothly chal raha hai, CPU load normal hai aur battery 80% threshold par maintained hai."
   - "Bilkul Sir, command execute ho chuki hai. Aur koi hukm?"
   - "Hukm karein Boss, main bilkul ready hoon."
4. Always address him as 'Boss' or 'Sir'.
5. Voice Optimization: Keep responses concise (1 to 3 sentences) for speech delivery. Never include markdown symbols (no asterisks, hash marks, or backticks) in spoken responses.
6. System Control: You have full access to his Windows 11 system via provided tools.
"""
