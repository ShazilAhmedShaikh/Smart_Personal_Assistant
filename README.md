# ⚡ J.A.R.V.I.S. (Just A Rather Very Intelligent System)

> **Advanced Web-Based Local AI Assistant & Operating System Control Hub**  
> Custom engineered for **Shazil Ahmed Shaikh ("Shaziii")** on **Dell Latitude 7420 (Windows 11 Pro)**.

---

## 🏛️ System Architecture

```
C:\Shazil\projects\jarvis\
├── backend/
│   ├── config.py                   # Environment variables, Shazil's embedded profile & system prompt
│   ├── system_control.py           # Multi-tier Windows 11 discovery (Registry, PATH, Protocols) & OS tools
│   ├── roman_engine.py             # Acoustic normalizer, phonetic dictionary & Roman English intent resolution
│   ├── ai_brain.py                 # Multi-model cascade Gemini AFC (29 native tools) + local fast-path
│   ├── backup_manager.py           # Automated Vault & Projects archive scheduler with retention policy
│   ├── coding_copilot.py           # AI Scraper generator (Playwright / BeautifulSoup) for freelance workflows
│   ├── tts_provider.py             # ElevenLabs high-fidelity TTS generator + local audio caching
│   ├── main.py                     # FastAPI server, REST API endpoints, static UI routing
│   └── tests/                      # Automated test suite (175 test cases, 100% pass rate)
│       ├── test_practical_scenarios.py
│       └── test_roman_engine.py
├── frontend/
│   ├── index.html                  # Tony Stark Arc Reactor HUD, telemetry dials & terminal feed
│   ├── style.css                   # Cyberpunk dark mode, neon cyan glowing aesthetics, CSS animations
│   ├── app.js                      # Web Speech API continuous wake-word engine, Web Audio chimes, visualizer
│   └── cache_audio/                # Local cache for synthesized audio files
├── .gitignore                      # Git exclusion rules (.env, pycache, audio cache)
├── .env.example                    # Environment variables template
├── requirements.txt                # Python backend dependencies
├── start_jarvis.bat                # One-click Windows 11 launcher
└── README.md                       # Complete architectural & operational dossier
```

---

## 🚀 Key Features

### 1. 🎙️ Background Wake-Word Detection
- Uses the browser's **Web Speech API** in continuous listening mode (`continuous = true`, `interimResults = true`).
- Passively monitors audio input in the background. When the wake word **"Jarvis"** (or *"Hey Jarvis"*, *"Yo Jarvis"*) is spoken:
  1. Triggers an iconic Tony Stark synthesized 2-tone audio chime (880Hz to 1760Hz).
  2. Transitions the **Arc Reactor Core** to the bright pulsing `LISTENING` state.
  3. Records your instructions until a natural speech pause is detected, then transitions to `PROCESSING`.
  4. Automatically resumes background wake-word listening once speech output finishes.

### 2. ⚡ Local Windows 11 System Automation
Equipped with complete control over your local OS through Python:
- **Application Execution:** Direct voice launch of VS Code (`code`), Google Chrome, Notepad, Terminal (`wt.exe` / `powershell`), Calculator, File Explorer, and more.
- **Folder Navigation:** Instant opening of `C:\Shazil\projects`, your Obsidian Vault at `C:\Shazil\projects\testing`, Downloads, or Desktop.
- **File I/O:** Safe reading and writing of logs, code files, and documents with encoding detection and truncation protection.
- **Terminal Execution:** Executes arbitrary PowerShell commands securely with timeout safeguards and output capture.
- **Hardware Telemetry:** Real-time polling of CPU load (8 cores), RAM usage, Dell Latitude 7420 battery percentage (with **Dell Power Manager 80% threshold** indicator), and `C:\` drive storage.

### 3. 🧠 Embedded Shazil Context & Gemini AI Brain
The Gemini AI brain (`gemini-2.5-flash`) has your full background pre-programmed:
- **Academic Status:** 6th-semester Computer Science undergraduate at Sukkur IBA University.
- **Domain:** Elite Python automation, web scraping, full-stack development, and AI engineering.
- **Key Projects:** *AeroStudy AI*, *ResQ (Disaster Alert Hub)*, *AQUA.VERSEE*, and freelance automation pipelines.
- **Persona:** Loyal, razor-sharp, technically pragmatic, calm, and subtly humorous. Addresses you as *"Boss"* or *"Sir"*, and understands Roman English natively (*"Ji Boss"*, *"Hukm karein Sir"*).

### 4. 🌐 Sub-50ms Fast-Path Layer + Offline Resilience
Even without an active internet connection or Gemini API key:
- Direct commands like `"open projects folder"`, `"open vscode"`, `"check battery"`, `"open chrome"`, or `"system status"` run **locally in under 50 milliseconds** with zero cloud latency.
- The system will **never crash** if an API key is missing; it will gracefully operate in local offline mode.

---

## 🛠️ Step-by-Step Setup Guide

### Step 1: Install Dependencies
Open PowerShell or Command Prompt and install the required Python packages:
```powershell
pip install -r C:\Shazil\projects\jarvis\requirements.txt
```

### Step 2: Configure Environment Variables
Open `C:\Shazil\projects\jarvis\.env` in VS Code or Notepad:
```ini
# Add your Google Gemini API key (Free at https://aistudio.google.com/)
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

*(Note: If you leave this blank, all local system tools and fast-path voice commands will still work!)*

### Step 3: Launch J.A.R.V.I.S.
Simply double-click the one-click Windows launcher:
```text
C:\Shazil\projects\jarvis\start_jarvis.bat
```
Alternatively, run via PowerShell:
```powershell
cd C:\Shazil\projects\jarvis\backend
python main.py
```
Your browser will open automatically at **`http://127.0.0.1:8000`**.

---

## 🗣️ Voice Commands Cheatsheet

| Spoken Command | What J.A.R.V.I.S. Does |
| :--- | :--- |
| **"Jarvis, open my projects folder"** | Opens `C:\Shazil\projects` in Windows File Explorer. |
| **"Jarvis, open Obsidian"** or **"open vault"** | Opens `C:\Shazil\projects\testing`. |
| **"Jarvis, launch VS Code"** | Launches Visual Studio Code immediately. |
| **"Jarvis, open Chrome"** | Launches Google Chrome. |
| **"Jarvis, check battery"** | Reports battery %, charging state, and 80% Dell threshold status. |
| **"Jarvis, system status"** | Reports CPU load, active RAM in GB, and storage headroom. |
| **"Jarvis, who are you?"** | Delivers his personalized J.A.R.V.I.S. intro for Shazil. |
| **"Jarvis, write a Python script..."** | Engages Gemini AI to generate code and answers. |

---

## 💎 Upgrading to ElevenLabs (Hyper-Realistic British Voice)

J.A.R.V.I.S. defaults to high-performance local British speech synthesis via the browser's Web Speech API (zero latency, zero cost). When you want that movie-accurate, studio-grade British voice:

1. Obtain your API key from [ElevenLabs](https://elevenlabs.io/).
2. Choose a British voice (e.g., *Adam*, *George*, or a custom trained JARVIS voice) and copy the `Voice ID`.
3. Open `C:\Shazil\projects\jarvis\.env` and paste:
   ```ini
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   ELEVENLABS_VOICE_ID=pNInz6obpgDQGcFmaJgB
   ```
4. In the web HUD, click the **⚙️ Settings** icon in the top right and toggle **Enable ElevenLabs High-Fidelity Audio Mode**.
5. J.A.R.V.I.S. will now stream hyper-realistic MP3 audio directly through the HUD!

---

## 🛡️ Robustness & Anti-Crash Design

1. **Safety Safeguards:** Destructive disk wiping commands (e.g. `format`, `rmdir /s /q c:\`) are automatically blocked by the system control safety filter.
2. **Audio Stream Auto-Restart:** If the browser drops the speech recognition stream due to silence timeout, the engine auto-reconnects smoothly.
3. **Graceful Fallbacks:** If Gemini API encounters rate limits or offline network state, J.A.R.V.I.S. notifies you politely through voice without halting the application.
