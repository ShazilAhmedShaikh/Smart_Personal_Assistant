/**
 * J.A.R.V.I.S. // Holographic 3D Particle Core & Neural Voice Controller
 * Complete Web Speech API, Wake-Word Engine, 3D Particle Cloud & Telemetry.
 * Designed for Shazil Ahmed Shaikh | Dell Latitude 7420
 */

// ==========================================
// 1. STATE & CONSTANTS
// ==========================================
const JARVIS_STATE = {
    STANDBY: 'STANDBY',
    LISTENING: 'LISTENING',
    PROCESSING: 'PROCESSING',
    SPEAKING: 'SPEAKING',
    MUTED: 'MUTED'
};

let currentState = JARVIS_STATE.STANDBY;
let isWakeWordActive = true;
let isManualRecording = false;
let speechRecognition = null;
let speechSynth = window.speechSynthesis;
let availableVoices = [];
let selectedVoice = null;
let currentUtterance = null;
let currentHtmlAudio = null;
let audioContext = null;
let audioAnalyser = null;
let audioDataArray = null;
let audioSourceNode = null;
let silenceTimer = null;
let pendingVoiceQuery = "";

// Continuous Conversation Session State
let isConversationalSessionActive = false;
let sessionInactivityTimer = null;

function resetConversationalSessionTimer() {
    if (sessionInactivityTimer) clearTimeout(sessionInactivityTimer);
    if (isConversationalSessionActive) {
        // After 25 seconds of silence during active chat, return to passive standby
        sessionInactivityTimer = setTimeout(() => {
            if (isConversationalSessionActive && currentState !== JARVIS_STATE.SPEAKING) {
                isConversationalSessionActive = false;
                setJarvisState(JARVIS_STATE.STANDBY);
                dom.caption.innerText = 'Standing by for instructions, Boss.';
                dom.wakeBadge.innerHTML = '<span class="pulse-ring"></span><span class="wake-text">WAKE-WORD ACTIVE: <strong class="cyan-text">"JARVIS"</strong></span>';
                logTerminal("[SESSION] Inactivity timeout. Returned to background wake-word monitor.", "info");
            }
        }, 25000);
    }
}

// Speech audio intensity (0.0 to 1.0) for particle reactivity
let speechAudioIntensity = 0.0;

// User preferences
let userPreferences = {
    voiceRate: 1.05,
    voicePitch: 0.95,
    useElevenLabs: false,
    neuralVoice: "en-IN-PrabhatNeural", // Default: Fluent South Asian Roman English
    micLocale: "en-IN"                 // Default: South Asian acoustic speech model
};

// Client-Side Phonetic Mishearing Normalizer
const CLIENT_PHONETIC_MAP = {
    "follow": "kholo",
    "holo": "kholo",
    "hollow": "kholo",
    "colo": "kholo",
    "shallow": "chalao",
    "chalau": "chalao",
    "shalao": "chalao",
    "but how": "batao",
    "butto": "batao",
    "photo": "batao",
    "call high": "kya haal hai",
    "car high": "kya haal hai",
    "betry": "battery",
    "betri": "battery",
    "prajacts": "projects"
};

function cleanClientTranscript(text) {
    let clean = text.toLowerCase();
    for (const [err, fix] of Object.entries(CLIENT_PHONETIC_MAP)) {
        clean = clean.replace(new RegExp(`\\b${err}\\b`, 'g'), fix);
    }
    return clean;
}

// ==========================================
// 2. DOM ELEMENT REFERENCES
// ==========================================
const dom = {
    clock: document.getElementById('hud-clock'),
    headerBattery: document.getElementById('header-battery-val'),
    wakeBadge: document.getElementById('wake-status-badge'),
    particleContainer: document.getElementById('particle-core-container'),
    particleCanvas: document.getElementById('jarvis-particle-canvas'),
    stateTag: document.getElementById('jarvis-state-tag'),
    caption: document.getElementById('jarvis-spoken-caption'),
    waveStrip: document.getElementById('audio-wave-strip'),
    waveBars: document.querySelectorAll('.wave-bar'),
    
    // Metrics
    cpuVal: document.getElementById('cpu-percent'),
    cpuBar: document.getElementById('cpu-bar'),
    ramVal: document.getElementById('ram-percent'),
    ramBar: document.getElementById('ram-bar'),
    ramDetails: document.getElementById('ram-details'),
    batteryVal: document.getElementById('battery-percent'),
    batteryBar: document.getElementById('battery-bar'),
    batterySub: document.getElementById('battery-sub'),
    diskVal: document.getElementById('disk-percent'),
    diskBar: document.getElementById('disk-bar'),
    diskDetails: document.getElementById('disk-details'),

    // Feeds
    chatStream: document.getElementById('chat-stream'),
    terminalFeed: document.getElementById('terminal-feed'),
    chatTab: document.getElementById('chat-tab-content'),
    terminalTab: document.getElementById('terminal-tab-content'),
    chatTabBtn: document.getElementById('tab-chat-btn'),
    terminalTabBtn: document.getElementById('tab-terminal-btn'),

    // Controls
    commandForm: document.getElementById('command-form'),
    textInput: document.getElementById('user-text-input'),
    toggleWakeBtn: document.getElementById('toggle-wake-btn'),
    wakeLabel: document.getElementById('wake-toggle-label'),
    manualMicBtn: document.getElementById('manual-mic-btn'),
    stopSpeechBtn: document.getElementById('stop-speech-btn'),

    // Settings Modal
    settingsModal: document.getElementById('settings-modal'),
    openSettingsBtn: document.getElementById('open-settings-btn'),
    closeSettingsBtn: document.getElementById('close-settings-btn'),
    neuralVoiceSelect: document.getElementById('neural-voice-select'),
    micLocaleSelect: document.getElementById('mic-locale-select'),
    voiceSelect: document.getElementById('voice-select'),
    rateInput: document.getElementById('voice-rate'),
    rateVal: document.getElementById('rate-val'),
    pitchInput: document.getElementById('voice-pitch'),
    pitchVal: document.getElementById('pitch-val'),
    elevenlabsToggle: document.getElementById('elevenlabs-toggle'),
    saveSettingsBtn: document.getElementById('save-settings-btn'),

    // Analytics & Telemetry Widget
    headerWifi: document.getElementById('header-wifi-val'),
    engineLatencyVal: document.getElementById('engine-latency-val'),
    lastBackupVal: document.getElementById('last-backup-val'),
    backupCountVal: document.getElementById('backup-count-val'),
    schedulerStatus: document.getElementById('scheduler-status'),

    // Canvases
    ambientCanvas: document.getElementById('ambient-canvas')
};


// ==========================================
// 3. AUDIO SYNTHESIS & SOUND FX (Web Audio API)
// ==========================================
function getAudioContext() {
    if (!audioContext) {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        audioContext = new AudioCtx();
    }
    if (audioContext.state === 'suspended') {
        audioContext.resume();
    }
    return audioContext;
}

/**
 * Stark Industries iconic activation chime.
 */
function playStarkActivationChime() {
    try {
        const ctx = getAudioContext();
        const now = ctx.currentTime;

        const osc1 = ctx.createOscillator();
        const gain1 = ctx.createGain();
        osc1.type = 'sine';
        osc1.frequency.setValueAtTime(880, now);
        gain1.gain.setValueAtTime(0.12, now);
        gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
        osc1.connect(gain1);
        gain1.connect(ctx.destination);
        osc1.start(now);
        osc1.stop(now + 0.15);

        const osc2 = ctx.createOscillator();
        const gain2 = ctx.createGain();
        osc2.type = 'sine';
        osc2.frequency.setValueAtTime(1760, now + 0.08);
        gain2.gain.setValueAtTime(0.18, now + 0.08);
        gain2.gain.exponentialRampToValueAtTime(0.001, now + 0.28);
        osc2.connect(gain2);
        gain2.connect(ctx.destination);
        osc2.start(now + 0.08);
        osc2.stop(now + 0.28);
    } catch (e) {
        console.warn("Audio chime prevented by browser autoplay policy:", e);
    }
}


// ==========================================
// 4. SPEECH RECOGNITION & WAKE-WORD SYSTEM
// ==========================================
function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        logTerminal("WARNING: Web Speech API Recognition is not supported. Please use Google Chrome or Edge.", "warn");
        dom.wakeLabel.innerText = "MIC NOT SUPPORTED";
        dom.toggleWakeBtn.classList.remove('active');
        return;
    }

    speechRecognition = new SpeechRecognition();
    speechRecognition.continuous = true;
    speechRecognition.interimResults = true;
    speechRecognition.lang = userPreferences.micLocale || 'en-IN';

    speechRecognition.onstart = () => {
        logTerminal(`[VOICE CORE] Speech recognition stream online (${speechRecognition.lang}).`, "info");
    };

    speechRecognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }

        const rawText = (finalTranscript || interimTranscript).trim();
        const fullDetectedText = cleanClientTranscript(rawText);

        // 1. In STANDBY state (passive wake word mode)
        if (currentState === JARVIS_STATE.STANDBY && !isConversationalSessionActive) {
            const lower = fullDetectedText.toLowerCase();
            const jarvisIndex = lower.indexOf('jarvis');

            if (jarvisIndex !== -1) {
                playStarkActivationChime();
                isConversationalSessionActive = true;
                setJarvisState(JARVIS_STATE.LISTENING);
                dom.wakeBadge.innerHTML = '<span class="pulse-ring"></span><span class="wake-text">CONVERSATION ACTIVE // <strong class="cyan-text">SAY "JAO" OR "BYE" TO END</strong></span>';
                logTerminal(`[CONVERSATION ENGAGED] Trigger: "${fullDetectedText}"`, "cyan");

                const afterJarvis = fullDetectedText.slice(jarvisIndex + 6).trim();
                if (afterJarvis.length > 2) {
                    pendingVoiceQuery = afterJarvis;
                    dom.caption.innerText = `"${pendingVoiceQuery}"`;
                } else {
                    pendingVoiceQuery = "";
                    dom.caption.innerText = 'Ji Boss, main sun raha hoon...';
                }

                resetSilenceTimer();
                resetConversationalSessionTimer();
            }
        } 
        // 2. In LISTENING state or active conversational session (No need to repeat "Jarvis"!)
        else if (currentState === JARVIS_STATE.LISTENING || isConversationalSessionActive) {
            const cleanedQuery = fullDetectedText.replace(/^(hey\s+|yo\s+|ok\s+|suno\s+)?jarvis[,.]?\s*/i, '').trim();
            if (cleanedQuery) {
                setJarvisState(JARVIS_STATE.LISTENING);
                pendingVoiceQuery = cleanedQuery;
                dom.caption.innerText = `"${pendingVoiceQuery}"`;
                resetSilenceTimer();
                resetConversationalSessionTimer();
            }
        }
    };

    speechRecognition.onerror = (event) => {
        if (event.error !== 'no-speech') {
            logTerminal(`[VOICE ERROR] Speech error: ${event.error}`, "warn");
        }
    };

    speechRecognition.onend = () => {
        if (isWakeWordActive && currentState !== JARVIS_STATE.SPEAKING) {
            try {
                speechRecognition.start();
            } catch (e) {
                // Ignore already started
            }
        }
    };

    startListeningStream();
}

function startListeningStream() {
    if (speechRecognition && isWakeWordActive) {
        try {
            speechRecognition.start();
            logTerminal("[VOICE CORE] Listening stream active.", "success");
        } catch (e) {
            // Already running
        }
    }
}

function resetSilenceTimer() {
    if (silenceTimer) clearTimeout(silenceTimer);
    
    // 1.5 seconds silence trigger
    silenceTimer = setTimeout(() => {
        if (currentState === JARVIS_STATE.LISTENING && pendingVoiceQuery.trim().length > 1) {
            const queryToExecute = pendingVoiceQuery.trim();
            pendingVoiceQuery = "";
            dispatchJarvisQuery(queryToExecute);
        }
    }, 1500);
}


// ==========================================
// 5. HYPER-REALISTIC SPEECH SYNTHESIS ENGINE
// ==========================================
function loadSystemVoices() {
    availableVoices = speechSynth.getVoices();
    if (availableVoices.length === 0) return;

    dom.voiceSelect.innerHTML = '';
    let preferredBritishVoice = null;

    availableVoices.forEach((voice, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.textContent = `${voice.name} (${voice.lang})`;

        const isBritish = voice.lang.includes('GB') || voice.name.toLowerCase().includes('british') || voice.name.toLowerCase().includes('george') || voice.name.toLowerCase().includes('daniel');
        
        if (isBritish && !preferredBritishVoice) {
            preferredBritishVoice = voice;
            option.selected = true;
        }

        dom.voiceSelect.appendChild(option);
    });

    if (preferredBritishVoice) {
        selectedVoice = preferredBritishVoice;
    } else {
        selectedVoice = availableVoices[0];
    }
}

if (speechSynth.onvoiceschanged !== undefined) {
    speechSynth.onvoiceschanged = loadSystemVoices;
}
loadSystemVoices();

function onVocalPlaybackFinished() {
    dom.waveStrip.classList.remove('active');
    speechAudioIntensity = 0.0;

    if (isConversationalSessionActive) {
        // Continuous Conversation Mode: Re-open mic immediately without needing "Jarvis"!
        setJarvisState(JARVIS_STATE.LISTENING);
        dom.caption.innerText = 'Main sun raha hoon Boss... (Next command boliye ya "Jao" boliye)';
        dom.wakeBadge.innerHTML = '<span class="pulse-ring"></span><span class="wake-text">CONVERSATION ACTIVE // <strong class="cyan-text">SAY "JAO" OR "BYE" TO END</strong></span>';
        resetConversationalSessionTimer();
        startListeningStream();
    } else {
        // Passive Standby Mode: Wait for wake word
        setJarvisState(JARVIS_STATE.STANDBY);
        dom.caption.innerText = 'Standing by for instructions, Boss.';
        dom.wakeBadge.innerHTML = '<span class="pulse-ring"></span><span class="wake-text">WAKE-WORD ACTIVE: <strong class="cyan-text">"JARVIS"</strong></span>';
        startListeningStream();
    }
}

/**
 * Plays hyper-realistic neural voice audio or falls back to Web Speech.
 */
function speakJarvisResponse(text, audioUrl = null) {
    // 1. If backend provided ultra-realistic Edge Neural TTS or ElevenLabs MP3
    if (audioUrl) {
        playRealisticAudio(audioUrl);
        return;
    }

    // 2. Fallback to Web Speech API
    if (!speechSynth) return;
    speechSynth.cancel();

    if (!text || text.trim().length === 0) {
        onVocalPlaybackFinished();
        return;
    }

    currentUtterance = new SpeechSynthesisUtterance(text);
    if (selectedVoice) {
        currentUtterance.voice = selectedVoice;
    }
    currentUtterance.rate = userPreferences.voiceRate;
    currentUtterance.pitch = userPreferences.voicePitch;

    currentUtterance.onstart = () => {
        setJarvisState(JARVIS_STATE.SPEAKING);
        dom.caption.innerText = text;
        dom.waveStrip.classList.add('active');
        speechAudioIntensity = 0.7;
    };

    currentUtterance.onend = () => {
        onVocalPlaybackFinished();
    };

    currentUtterance.onerror = (e) => {
        console.error("SpeechSynthesis error:", e);
        onVocalPlaybackFinished();
    };

    if (speechRecognition) {
        try { speechRecognition.stop(); } catch (e) {}
    }

    speechSynth.speak(currentUtterance);
}

/**
 * Plays studio-grade Neural TTS MP3 audio with particle synchronization.
 */
function playRealisticAudio(audioUrl) {
    if (currentHtmlAudio) {
        currentHtmlAudio.pause();
        currentHtmlAudio = null;
    }

    currentHtmlAudio = new Audio(audioUrl);
    
    currentHtmlAudio.onplay = () => {
        setJarvisState(JARVIS_STATE.SPEAKING);
        dom.waveStrip.classList.add('active');
        speechAudioIntensity = 0.85;
        if (speechRecognition) {
            try { speechRecognition.stop(); } catch (e) {}
        }
    };

    currentHtmlAudio.ontimeupdate = () => {
        // Modulate speech intensity dynamically
        speechAudioIntensity = 0.6 + Math.sin(Date.now() * 0.015) * 0.35;
    };

    currentHtmlAudio.onended = () => {
        onVocalPlaybackFinished();
    };

    currentHtmlAudio.onerror = () => {
        logTerminal("[TTS WARNING] Neural audio stream error. Reverting to local synth.", "warn");
        onVocalPlaybackFinished();
    };

    currentHtmlAudio.play().catch(e => {
        console.warn("Autoplay audio blocked:", e);
        // Fallback to Web Speech if browser blocks initial audio tag
        speakJarvisResponse(dom.caption.innerText, null);
    });
}


// ==========================================
// 6. QUERY DISPATCH & FAST-PATH EXECUTION
// ==========================================
async function dispatchJarvisQuery(queryText) {
    if (!queryText || queryText.trim().length === 0) return;

    setJarvisState(JARVIS_STATE.PROCESSING);
    dom.caption.innerText = `Processing: "${queryText}"...`;
    
    appendChatMessage('user', queryText);
    logTerminal(`[DISPATCH] Roman English query: "${queryText}"`, "info");

    try {
        const payload = {
            query: queryText,
            voice_mode: true,
            voice_id: userPreferences.neuralVoice,
            use_elevenlabs: userPreferences.useElevenLabs
        };

        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.success) {
            appendChatMessage('jarvis', data.response);

            // Check if user requested to end session ("jao", "bye", "standby")
            if (data.action && (data.action.session_exit || data.action.action === "session_exit")) {
                isConversationalSessionActive = false;
                if (sessionInactivityTimer) clearTimeout(sessionInactivityTimer);
                logTerminal("[SESSION] Conversation ended by Commander. Entering passive standby.", "cyan");
            } else {
                isConversationalSessionActive = true;
                resetConversationalSessionTimer();
            }

            if (data.action) {
                logTerminal(`[SYSTEM ACTION] ${JSON.stringify(data.action)}`, "success");
            }

            dom.caption.innerText = data.spoken_text;
            speakJarvisResponse(data.spoken_text, data.audio_url);
        } else {
            const err = data.error || "Neural execution failed.";
            appendChatMessage('jarvis', `Error: ${err}`);
            logTerminal(`[ERROR] ${err}`, "error");
            speakJarvisResponse(data.spoken_text || "Command execute karne mein issue aya hai, Boss.");
        }
    } catch (err) {
        const errorText = `Local backend connection error: ${err.message}`;
        appendChatMessage('jarvis', errorText);
        logTerminal(`[CONN ERROR] ${errorText}`, "error");
        speakJarvisResponse("Backend se rabta disconnect ho gaya hai Boss.");
    }
}


// ==========================================
// 7. STATE MACHINE & HUD ANIMATIONS
// ==========================================
function setJarvisState(newState) {
    currentState = newState;
    dom.particleContainer.classList.remove('state-listening', 'state-processing', 'state-speaking');

    switch (newState) {
        case JARVIS_STATE.STANDBY:
            dom.stateTag.innerText = 'STANDBY // READY';
            dom.stateTag.className = 'status-indicator-tag cyan-text';
            dom.wakeBadge.classList.add('active');
            break;

        case JARVIS_STATE.LISTENING:
            dom.stateTag.innerText = 'VOICE ACTIVE // LISTENING...';
            dom.stateTag.className = 'status-indicator-tag cyan-text';
            dom.particleContainer.classList.add('state-listening');
            dom.wakeBadge.classList.add('active');
            break;

        case JARVIS_STATE.PROCESSING:
            dom.stateTag.innerText = 'PROCESSING // NEURAL LOGIC';
            dom.stateTag.className = 'status-indicator-tag blue-text';
            dom.particleContainer.classList.add('state-processing');
            break;

        case JARVIS_STATE.SPEAKING:
            dom.stateTag.innerText = 'VOCAL FEEDBACK // TRANSMITTING';
            dom.stateTag.className = 'status-indicator-tag cyan-text';
            dom.particleContainer.classList.add('state-speaking');
            break;

        case JARVIS_STATE.MUTED:
            dom.stateTag.innerText = 'MIC OFFLINE // STANDBY';
            dom.stateTag.className = 'status-indicator-tag orange-text';
            dom.wakeBadge.classList.remove('active');
            break;
    }
}


// ==========================================
// 8. HUD METRICS & TELEMETRY STREAM
// ==========================================
async function fetchSystemMetrics() {
    try {
        const res = await fetch('/api/system/metrics');
        if (!res.ok) return;
        const data = await res.json();
        if (!data.success) return;

        // CPU
        const cpu = data.cpu.percent;
        dom.cpuVal.innerText = `${cpu}%`;
        dom.cpuBar.style.width = `${Math.min(cpu, 100)}%`;

        // RAM
        const ram = data.memory.percent;
        dom.ramVal.innerText = `${ram}%`;
        dom.ramBar.style.width = `${Math.min(ram, 100)}%`;
        dom.ramDetails.innerText = `${data.memory.used_gb} GB / ${data.memory.total_gb} GB ACTIVE`;

        // Battery
        if (data.battery.available) {
            const bPercent = data.battery.percent;
            dom.batteryVal.innerText = `${bPercent}%`;
            dom.batteryBar.style.width = `${Math.min(bPercent, 100)}%`;
            dom.headerBattery.innerText = `${bPercent}%`;
            
            const plugged = data.battery.power_plugged ? "⚡ Plugged In" : "🔋 On Battery";
            dom.batterySub.innerText = `${plugged} // ${data.battery.dell_threshold_status}`;
        }

        // Storage
        const disk = data.disk_c.percent;
        dom.diskVal.innerText = `${disk}%`;
        dom.diskBar.style.width = `${Math.min(disk, 100)}%`;
        dom.diskDetails.innerText = `${data.disk_c.free_gb} GB FREE OF ${data.disk_c.total_gb} GB`;

    } catch (e) {
        // Quiet telemetry catch
    }
}

setInterval(fetchSystemMetrics, 2500);
fetchSystemMetrics();

// Backup & Analytics Telemetry
async function fetchBackupAnalytics() {
    try {
        const t0 = performance.now();
        const res = await fetch('/api/backup/list');
        const latency = Math.round(performance.now() - t0);
        if (dom.engineLatencyVal) {
            dom.engineLatencyVal.innerText = `${latency} ms`;
        }
        if (res.ok) {
            const archives = await res.json();
            if (dom.backupCountVal) {
                dom.backupCountVal.innerText = `${archives.length} ARCHIVES`;
            }
            if (archives.length > 0 && dom.lastBackupVal) {
                const latest = archives[0];
                const cleanDate = latest.created ? latest.created.split(' ')[1] : '--';
                dom.lastBackupVal.innerText = `${latest.size_mb}MB (${cleanDate})`;
            }
        }
    } catch (e) {
        // Quiet
    }
}
setInterval(fetchBackupAnalytics, 8000);
fetchBackupAnalytics();

async function fetchNetworkTelemetry() {
    try {
        const res = await fetch('/api/system/network');
        if (res.ok) {
            const data = await res.json();
            if (data.success && dom.headerWifi) {
                dom.headerWifi.innerText = `${data.wifi_ssid} (${data.local_ip})`;
            }
        }
    } catch (e) {}
}
setInterval(fetchNetworkTelemetry, 15000);
fetchNetworkTelemetry();

function updateClock() {
    const now = new Date();
    dom.clock.innerText = now.toTimeString().split(' ')[0] + " PKT";
}
setInterval(updateClock, 1000);
updateClock();


// ==========================================
// 9. FEEDS: CHAT & TERMINAL LOGGING
// ==========================================
function appendChatMessage(sender, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${sender === 'user' ? 'user-msg' : 'jarvis-msg'}`;

    const senderHeader = document.createElement('div');
    senderHeader.className = 'msg-sender';
    senderHeader.innerText = sender === 'user' ? 'COMMANDER (SHAZIL)' : 'J.A.R.V.I.S.';

    const bodyDiv = document.createElement('div');
    bodyDiv.className = 'msg-body';
    bodyDiv.innerText = text;

    const metaDiv = document.createElement('div');
    metaDiv.className = 'msg-meta';
    metaDiv.innerText = new Date().toLocaleTimeString();

    msgDiv.appendChild(senderHeader);
    msgDiv.appendChild(bodyDiv);
    msgDiv.appendChild(metaDiv);

    dom.chatStream.appendChild(msgDiv);
    dom.chatStream.scrollTop = dom.chatStream.scrollHeight;
}

function logTerminal(message, type = "info") {
    const line = document.createElement('div');
    line.className = `term-line ${type}`;
    const timestamp = new Date().toTimeString().split(' ')[0];
    line.innerText = `[${timestamp}] ${message}`;
    dom.terminalFeed.appendChild(line);
    dom.terminalFeed.scrollTop = dom.terminalFeed.scrollHeight;
}

function switchRightTab(tabName) {
    if (tabName === 'chat') {
        dom.chatTab.classList.add('active');
        dom.terminalTab.classList.remove('active');
        dom.chatTabBtn.classList.add('active');
        dom.terminalTabBtn.classList.remove('active');
    } else {
        dom.terminalTab.classList.add('active');
        dom.chatTab.classList.remove('active');
        dom.terminalTabBtn.classList.add('active');
        dom.chatTabBtn.classList.remove('active');
    }
}


// ==========================================
// 10. DIRECT ACTIONS & CONTROLS
// ==========================================
function executeQuickAction(actionKey) {
    switch (actionKey) {
        case 'open_projects':
            dispatchJarvisQuery('Jarvis, projects kholo');
            break;
        case 'open_vault':
            dispatchJarvisQuery('Jarvis, obsidian vault kholo');
            break;
        case 'backup_vault':
            dispatchJarvisQuery('Jarvis, vault ka backup banao');
            break;
        case 'generate_scraper':
            dispatchJarvisQuery('Jarvis, scraper banao');
            break;
        case 'list_processes':
            dispatchJarvisQuery('Jarvis, processes dikhao');
            break;
        case 'read_clipboard':
            dispatchJarvisQuery('Jarvis, clipboard dikhao');
            break;
        case 'empty_trash':
            dispatchJarvisQuery('Jarvis, recycle bin empty karo');
            break;
        case 'lock_pc':
            dispatchJarvisQuery('Jarvis, pc lock karo');
            break;
        case 'open_vscode':
            dispatchJarvisQuery('Jarvis, vscode launch karo');
            break;
        case 'open_chrome':
            dispatchJarvisQuery('Jarvis, chrome chalao');
            break;
        case 'run_diagnostics':
            dispatchJarvisQuery('Jarvis, system status check karo');
            break;
    }
}

function handleTextSubmit(e) {
    e.preventDefault();
    const query = dom.textInput.value.trim();
    if (!query) return;
    dom.textInput.value = '';
    dispatchJarvisQuery(query);
}

// Wake Word Toggle
dom.toggleWakeBtn.addEventListener('click', () => {
    isWakeWordActive = !isWakeWordActive;
    if (isWakeWordActive) {
        dom.toggleWakeBtn.classList.add('active');
        dom.wakeLabel.innerText = 'WAKE WORD: ACTIVE';
        setJarvisState(JARVIS_STATE.STANDBY);
        startListeningStream();
        logTerminal("[VOICE] Continuous wake-word listening re-enabled.", "success");
    } else {
        dom.toggleWakeBtn.classList.remove('active');
        dom.wakeLabel.innerText = 'WAKE WORD: MUTED';
        setJarvisState(JARVIS_STATE.MUTED);
        if (speechRecognition) {
            try { speechRecognition.stop(); } catch (e) {}
        }
        logTerminal("[VOICE] Continuous wake-word muted.", "warn");
    }
});

// Manual Push to Talk / Tap to Speak
dom.manualMicBtn.addEventListener('click', () => {
    getAudioContext();
    if (currentState === JARVIS_STATE.LISTENING) {
        if (silenceTimer) clearTimeout(silenceTimer);
        if (pendingVoiceQuery.trim().length > 1) {
            const q = pendingVoiceQuery.trim();
            pendingVoiceQuery = "";
            dispatchJarvisQuery(q);
        } else {
            setJarvisState(JARVIS_STATE.STANDBY);
        }
        dom.manualMicBtn.classList.remove('recording');
    } else {
        playStarkActivationChime();
        isConversationalSessionActive = true;
        setJarvisState(JARVIS_STATE.LISTENING);
        dom.caption.innerText = 'Ji Boss, batayein kya command hai...';
        dom.wakeBadge.innerHTML = '<span class="pulse-ring"></span><span class="wake-text">CONVERSATION ACTIVE // <strong class="cyan-text">SAY "JAO" OR "BYE" TO END</strong></span>';
        dom.manualMicBtn.classList.add('recording');
        resetConversationalSessionTimer();
        startListeningStream();
    }
});

// Stop / Mute Speech Button
dom.stopSpeechBtn.addEventListener('click', () => {
    if (speechSynth) speechSynth.cancel();
    if (currentHtmlAudio) {
        currentHtmlAudio.pause();
        currentHtmlAudio = null;
    }
    speechAudioIntensity = 0.0;
    isConversationalSessionActive = false;
    if (sessionInactivityTimer) clearTimeout(sessionInactivityTimer);
    dom.waveStrip.classList.remove('active');
    setJarvisState(JARVIS_STATE.STANDBY);
    dom.wakeBadge.innerHTML = '<span class="pulse-ring"></span><span class="wake-text">WAKE-WORD ACTIVE: <strong class="cyan-text">"JARVIS"</strong></span>';
    startListeningStream();
    logTerminal("[VOICE] Speech silenced by Commander. Standby initiated.", "info");
});

// Settings Modal
dom.openSettingsBtn.addEventListener('click', () => dom.settingsModal.classList.add('show'));
dom.closeSettingsBtn.addEventListener('click', () => dom.settingsModal.classList.remove('show'));

if (dom.neuralVoiceSelect) {
    dom.neuralVoiceSelect.addEventListener('change', (e) => {
        userPreferences.neuralVoice = e.target.value;
        logTerminal(`[VOICE CONFIG] Selected Neural Engine: ${userPreferences.neuralVoice}`, "cyan");
    });
}

if (dom.micLocaleSelect) {
    dom.micLocaleSelect.addEventListener('change', (e) => {
        userPreferences.micLocale = e.target.value;
        if (speechRecognition) {
            speechRecognition.lang = userPreferences.micLocale;
            try {
                speechRecognition.stop();
                setTimeout(startListeningStream, 200);
            } catch (err) {}
        }
        logTerminal(`[MIC CONFIG] Recognition locale switched to: ${userPreferences.micLocale}`, "cyan");
    });
}

dom.voiceSelect.addEventListener('change', (e) => {
    const idx = parseInt(e.target.value);
    if (availableVoices[idx]) {
        selectedVoice = availableVoices[idx];
    }
});

dom.rateInput.addEventListener('input', (e) => {
    userPreferences.voiceRate = parseFloat(e.target.value);
    dom.rateVal.innerText = `${userPreferences.voiceRate}x`;
});

dom.pitchInput.addEventListener('input', (e) => {
    userPreferences.voicePitch = parseFloat(e.target.value);
    dom.pitchVal.innerText = userPreferences.voicePitch;
});

dom.elevenlabsToggle.addEventListener('change', (e) => {
    userPreferences.useElevenLabs = e.target.checked;
    logTerminal(`[CONFIG] ElevenLabs high-fidelity mode set to: ${userPreferences.useElevenLabs}`, "cyan");
});

dom.saveSettingsBtn.addEventListener('click', () => {
    dom.settingsModal.classList.remove('show');
    logTerminal("[CONFIG] Audio parameters updated successfully.", "success");
    speakJarvisResponse("Ji Boss, vocal parameters update kar diye hain.");
});


// ==========================================
// 11. TONY STARK HOLOGRAPHIC 3D PARTICLE SYSTEM
// ==========================================
function init3DParticleCore() {
    const canvas = dom.particleCanvas;
    const ctx = canvas.getContext('2d');
    
    // High DPI scaling
    const size = 440;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = size * dpr;
    canvas.height = size * dpr;
    ctx.scale(dpr, dpr);

    const centerX = size / 2;
    const centerY = size / 2;

    // 3D Spherical Particle Cloud
    const particleCount = 480;
    const particles = [];

    for (let i = 0; i < particleCount; i++) {
        // Uniform spherical distribution via Fibonacci spiral
        const phi = Math.acos(1 - 2 * (i + 0.5) / particleCount);
        const theta = Math.PI * (1 + Math.sqrt(5)) * (i + 0.5);

        // Multi-layered shells (core shell + surface shell + orbital sparks)
        let layerRadius = 125;
        let isCore = false;

        if (i < 80) {
            // Inner energetic core
            layerRadius = Math.random() * 45 + 35;
            isCore = true;
        } else if (i > 420) {
            // Outer orbital satellite dust
            layerRadius = Math.random() * 35 + 140;
        } else {
            // Main holographic sphere shell
            layerRadius = 115 + (Math.random() - 0.5) * 20;
        }

        particles.push({
            theta: theta,
            phi: phi,
            baseRadius: layerRadius,
            currentRadius: layerRadius,
            isCore: isCore,
            speed: (Math.random() * 0.004 + 0.002) * (Math.random() < 0.5 ? 1 : -1),
            pulsePhase: Math.random() * Math.PI * 2,
            size: isCore ? Math.random() * 2.2 + 1.2 : Math.random() * 1.8 + 0.8,
            colorHue: isCore ? 180 : (Math.random() < 0.25 ? 205 : 190) // Cyan to Electric Blue
        });
    }

    // 3D Angles
    let rotX = 0.2;
    let rotY = 0.0;
    let rotZ = 0.0;

    // Mouse Parallax
    let targetRotX = 0.2;
    let targetRotY = 0.0;

    canvas.addEventListener('mousemove', (e) => {
        const rect = canvas.getBoundingClientRect();
        const mx = (e.clientX - rect.left) / rect.width - 0.5;
        const my = (e.clientY - rect.top) / rect.height - 0.5;
        targetRotY = mx * 1.2;
        targetRotX = -my * 1.2;
    });

    canvas.addEventListener('mouseleave', () => {
        targetRotX = 0.2;
        targetRotY = 0.0;
    });

    let time = 0;

    function render3DParticles() {
        ctx.clearRect(0, 0, size, size);

        // Smooth mouse parallax lerp
        rotX += (targetRotX - rotX) * 0.05;
        rotY += (targetRotY - rotY) * 0.05;

        // Base auto-rotation speeds driven by JARVIS State
        let autoSpeedY = 0.008;
        let autoSpeedX = 0.003;

        if (currentState === JARVIS_STATE.LISTENING) {
            autoSpeedY = 0.016;
            autoSpeedX = 0.008;
        } else if (currentState === JARVIS_STATE.PROCESSING) {
            autoSpeedY = 0.045; // Cyclone spin
            autoSpeedX = 0.02;
        } else if (currentState === JARVIS_STATE.SPEAKING) {
            autoSpeedY = 0.012;
            autoSpeedX = 0.005;
        }

        rotY += autoSpeedY;
        rotX += autoSpeedX;
        time += 0.03;

        // Compute 3D Projected Points
        const projected = [];
        const focalLength = 320;
        const zCamera = 360;

        for (let i = 0; i < particleCount; i++) {
            const p = particles[i];
            
            // Dynamic Radius Modulation by State
            let targetR = p.baseRadius;

            if (currentState === JARVIS_STATE.LISTENING) {
                // Expand outward + audio vibration
                targetR = p.baseRadius * 1.28 + Math.sin(time * 6 + p.pulsePhase) * 12;
            } else if (currentState === JARVIS_STATE.PROCESSING) {
                // Collapse inward into a dense high-speed cyclone
                targetR = p.isCore ? 30 : p.baseRadius * 0.65 + Math.sin(time * 8 + p.pulsePhase) * 6;
            } else if (currentState === JARVIS_STATE.SPEAKING) {
                // Harmonic soundwaves rippling across surface
                const wave = Math.sin(time * 8 + p.phi * 4 + p.theta * 2);
                targetR = p.baseRadius * (1.0 + speechAudioIntensity * 0.28 * wave);
            } else {
                // STANDBY: Gentle breathing
                targetR = p.baseRadius + Math.sin(time * 1.5 + p.pulsePhase) * 5;
            }

            p.currentRadius += (targetR - p.currentRadius) * 0.12;

            // Spherical to Cartesian
            const x0 = p.currentRadius * Math.sin(p.phi) * Math.cos(p.theta + p.speed * time * 50);
            const y0 = p.currentRadius * Math.sin(p.phi) * Math.sin(p.theta + p.speed * time * 50);
            const z0 = p.currentRadius * Math.cos(p.phi);

            // Rotate Y
            const cosY = Math.cos(rotY);
            const sinY = Math.sin(rotY);
            const x1 = x0 * cosY + z0 * sinY;
            const z1 = -x0 * sinY + z0 * cosY;

            // Rotate X
            const cosX = Math.cos(rotX);
            const sinX = Math.sin(rotX);
            const y2 = y0 * cosX - z1 * sinX;
            const z2 = y0 * sinX + z1 * cosX;

            // Perspective Projection
            const zFinal = z2 + zCamera;
            const scale = focalLength / zFinal;
            const px = x1 * scale + centerX;
            const py = y2 * scale + centerY;

            projected.push({
                x: px,
                y: py,
                z: z2,
                scale: scale,
                p: p
            });
        }

        // Sort by Z (painter's algorithm)
        projected.sort((a, b) => a.z - b.z);

        // 1. Draw Holographic Neural Connection Lines (Meshing proximate nodes)
        const maxDist = currentState === JARVIS_STATE.LISTENING ? 42 : 34;
        const lineCountLimit = 160;
        let drawnLines = 0;

        ctx.lineWidth = 0.8;
        for (let i = 0; i < projected.length && drawnLines < lineCountLimit; i += 2) {
            const pt1 = projected[i];
            if (pt1.z < -40) continue; // Skip deep back lines

            for (let j = i + 1; j < Math.min(i + 14, projected.length); j++) {
                const pt2 = projected[j];
                const dx = pt1.x - pt2.x;
                const dy = pt1.y - pt2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < maxDist) {
                    const alpha = (1 - dist / maxDist) * 0.35 * Math.max(0.1, (pt1.z + 150) / 300);
                    
                    let strokeColor = `rgba(0, 240, 255, ${alpha})`;
                    if (currentState === JARVIS_STATE.PROCESSING) {
                        strokeColor = `rgba(192, 132, 252, ${alpha})`;
                    } else if (currentState === JARVIS_STATE.SPEAKING) {
                        strokeColor = `rgba(0, 200, 255, ${alpha * 1.5})`;
                    }

                    ctx.strokeStyle = strokeColor;
                    ctx.beginPath();
                    ctx.moveTo(pt1.x, pt1.y);
                    ctx.lineTo(pt2.x, pt2.y);
                    ctx.stroke();
                    drawnLines++;
                }
            }
        }

        // 2. Draw Core Glow Nucleus
        const coreGlow = ctx.createRadialGradient(centerX, centerY, 5, centerX, centerY, 70);
        if (currentState === JARVIS_STATE.PROCESSING) {
            coreGlow.addColorStop(0, 'rgba(255, 255, 255, 0.95)');
            coreGlow.addColorStop(0.3, 'rgba(192, 132, 252, 0.6)');
            coreGlow.addColorStop(0.7, 'rgba(168, 85, 247, 0.2)');
            coreGlow.addColorStop(1, 'transparent');
        } else {
            coreGlow.addColorStop(0, 'rgba(255, 255, 255, 0.95)');
            coreGlow.addColorStop(0.25, 'rgba(0, 240, 255, 0.65)');
            coreGlow.addColorStop(0.65, 'rgba(0, 136, 255, 0.25)');
            coreGlow.addColorStop(1, 'transparent');
        }
        ctx.fillStyle = coreGlow;
        ctx.beginPath();
        ctx.arc(centerX, centerY, 70, 0, Math.PI * 2);
        ctx.fill();

        // 3. Draw 3D Particles
        for (let i = 0; i < projected.length; i++) {
            const item = projected[i];
            const p = item.p;
            
            // Depth-based opacity & radius
            const depthRatio = Math.max(0.1, Math.min(1.0, (item.z + 160) / 320));
            const particleRadius = Math.max(0.6, p.size * item.scale * (depthRatio * 0.9 + 0.4));
            
            let alpha = depthRatio * 0.85 + 0.15;
            let hue = p.colorHue;

            if (currentState === JARVIS_STATE.LISTENING) {
                alpha = Math.min(1.0, alpha * 1.3);
                hue = 175; // Intense neon cyan
            } else if (currentState === JARVIS_STATE.PROCESSING) {
                hue = 270; // Electric violet
            }

            ctx.beginPath();
            ctx.arc(item.x, item.y, particleRadius, 0, Math.PI * 2);

            // Front particles get bright glow halos
            if (item.z > 20) {
                ctx.shadowBlur = currentState === JARVIS_STATE.LISTENING ? 14 : 8;
                ctx.shadowColor = `hsl(${hue}, 100%, 65%)`;
                ctx.fillStyle = item.z > 80 ? '#ffffff' : `hsla(${hue}, 100%, 75%, ${alpha})`;
            } else {
                ctx.shadowBlur = 0;
                ctx.fillStyle = `hsla(${hue}, 90%, 55%, ${alpha * 0.65})`;
            }

            ctx.fill();
        }

        // Reset shadow
        ctx.shadowBlur = 0;

        // Bottom soundwave bars sync
        if (currentState === JARVIS_STATE.SPEAKING || currentState === JARVIS_STATE.LISTENING) {
            dom.waveBars.forEach((bar) => {
                const dynamicHeight = Math.floor(Math.random() * 26 + 4);
                bar.style.height = `${dynamicHeight}px`;
            });
        }

        requestAnimationFrame(render3DParticles);
    }

    render3DParticles();
}


// Ambient Canvas (Background Grid & Floating Data Bits)
function initAmbientCanvas() {
    const canvas = dom.ambientCanvas;
    const ctx = canvas.getContext('2d');
    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    const particles = [];
    const count = 40;

    for (let i = 0; i < count; i++) {
        particles.push({
            x: Math.random() * width,
            y: Math.random() * height,
            radius: Math.random() * 1.4 + 0.6,
            vx: (Math.random() - 0.5) * 0.35,
            vy: (Math.random() - 0.5) * 0.35,
            alpha: Math.random() * 0.45 + 0.1
        });
    }

    function render() {
        ctx.clearRect(0, 0, width, height);

        ctx.strokeStyle = 'rgba(0, 240, 255, 0.025)';
        ctx.lineWidth = 1;
        const gridSize = 65;
        for (let x = 0; x < width; x += gridSize) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, height);
            ctx.stroke();
        }
        for (let y = 0; y < height; y += gridSize) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(width, y);
            ctx.stroke();
        }

        particles.forEach(p => {
            p.x += p.vx;
            p.y += p.vy;

            if (p.x < 0) p.x = width;
            if (p.x > width) p.x = 0;
            if (p.y < 0) p.y = height;
            if (p.y > height) p.y = 0;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(0, 240, 255, ${p.alpha})`;
            ctx.shadowBlur = 4;
            ctx.shadowColor = '#00f0ff';
            ctx.fill();
        });

        requestAnimationFrame(render);
    }
    render();
}


// ==========================================
// 12. INITIALIZATION
// ==========================================
window.addEventListener('DOMContentLoaded', () => {
    initAmbientCanvas();
    init3DParticleCore();
    initSpeechRecognition();

    document.body.addEventListener('click', () => {
        getAudioContext();
    }, { once: true });

    logTerminal("J.A.R.V.I.S. 3D Holographic Particle Core Online. Say 'Jarvis' to engage.", "cyan");
});
