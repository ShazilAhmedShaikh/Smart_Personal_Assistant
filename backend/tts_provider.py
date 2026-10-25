"""
J.A.R.V.I.S. Text-to-Speech (TTS) Provider Module
Handles ultra-realistic neural speech synthesis:
1. Microsoft Edge Neural TTS (Free, studio-quality neural voices like en-GB-RyanNeural & ur-PK-AsadNeural).
2. ElevenLabs REST API (Optional high-fidelity cloud voices).
"""

import os
import hashlib
import httpx
import edge_tts
from pathlib import Path
from typing import Dict, Any, Optional

from config import (
    ELEVENLABS_API_KEY,
    ELEVENLABS_VOICE_ID,
    EDGE_TTS_VOICE,
    EDGE_TTS_URDU_VOICE,
    PROJECT_ROOT
)

AUDIO_CACHE_DIR = PROJECT_ROOT / "frontend" / "cache_audio"
AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)


async def synthesize_edge_speech(text: str, voice: Optional[str] = None) -> Dict[str, Any]:
    """
    Synthesizes speech using Microsoft Edge Neural TTS.
    Returns the URL/path to the generated MP3 file.
    Studio-grade natural cadence with zero API keys required.
    """
    clean_text = text.strip()
    if not clean_text:
        return {"success": False, "error": "Empty text provided."}

    # Detect if text is predominantly Roman Urdu / English
    # Default to British Jarvis voice or specified voice
    selected_voice = voice or EDGE_TTS_VOICE

    try:
        # Create unique MD5 hash for filename caching
        text_hash = hashlib.md5(f"{selected_voice}_{clean_text}".encode("utf-8")).hexdigest()[:16]
        filename = f"jarvis_neural_{text_hash}.mp3"
        filepath = AUDIO_CACHE_DIR / filename

        # If already cached, reuse
        if not filepath.exists():
            communicate = edge_tts.Communicate(clean_text, selected_voice)
            await communicate.save(str(filepath))

        return {
            "success": True,
            "engine": "edge-tts",
            "voice": selected_voice,
            "audio_url": f"/cache_audio/{filename}"
        }
    except Exception as e:
        print(f"[EDGE-TTS ERROR] {e}")
        return {
            "success": False,
            "error": f"Failed Edge Neural synthesis: {str(e)}"
        }


async def synthesize_elevenlabs_speech(text: str, voice_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Synthesizes speech using the ElevenLabs Text-to-Speech REST API.
    Returns the URL/path to the generated MP3 file.
    """
    api_key = ELEVENLABS_API_KEY.strip()
    if not api_key or api_key == "your_elevenlabs_api_key_here":
        # Fallback seamlessly to Edge Neural TTS
        return await synthesize_edge_speech(text)

    selected_voice_id = voice_id or ELEVENLABS_VOICE_ID or "pNInz6obpgDQGcFmaJgB"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{selected_voice_id}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }

    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8
        }
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                text_hash = hashlib.md5(f"el_{selected_voice_id}_{text}".encode("utf-8")).hexdigest()[:16]
                filename = f"jarvis_el_{text_hash}.mp3"
                filepath = AUDIO_CACHE_DIR / filename
                filepath.write_bytes(response.content)

                return {
                    "success": True,
                    "engine": "elevenlabs",
                    "audio_url": f"/cache_audio/{filename}",
                    "voice_id": selected_voice_id
                }
            else:
                # Fallback to Edge Neural TTS
                return await synthesize_edge_speech(text)
    except Exception as e:
        # Fallback to Edge Neural TTS
        return await synthesize_edge_speech(text)
