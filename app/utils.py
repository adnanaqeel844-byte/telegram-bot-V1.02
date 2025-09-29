import logging
import requests
import uuid
import os
from openai import AsyncOpenAI
from elevenlabs import AsyncElevenLabs
from fastapi_limiter.depends import RateLimiter
from .config import XAI_API_KEY, DISCORD_WEBHOOK_URL, ELEVENLABS_API_KEY, TELEGRAM_BOT_TOKEN, RECORDINGS_PATH

os.makedirs(RECORDINGS_PATH, exist_ok=True)

# xAI client
client = AsyncOpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")

# ElevenLabs client
elevenlabs = AsyncElevenLabs(api_key=ELEVENLABS_API_KEY)

# Discord alert
def send_alert(msg):
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": msg})
        logging.info(f"Alert: {msg}")
    except Exception as e:
        logging.error(f"Alert failed: {e}")

# xAI query function (text or media)
async def query_xai(msg, media_url=None, max_tokens=150):
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant powered by xAI Grok. Transcribe or describe media if provided."},
            {"role": "user", "content": msg}
        ]
        if media_url:
            messages.append({"role": "user", "content": [{"type": "image_url", "image_url": {"url": media_url}}]})
        response = await client.chat.completions.create(
            model="grok-4",
            messages=messages,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"xAI error: {e}")
        send_alert(f"xAI error: {e}")
        return None

# Generate Jitsi video call link with recording
def generate_jitsi_link(room_name=None, record=False):
    room = room_name or str(uuid.uuid4())[:8]
    params = f"?record=true" if record else ""
    return f"https://{JITSI_DOMAIN}/{room}{params}"

# Generate call context with xAI
async def generate_call_context(chat_history):
    return await query_xai(f"Summarize this chat history for an upcoming video call: {chat_history}")

# Download and save recording
async def download_recording(url, filename):
    try:
        response = requests.get(url)
        response.raise_for_status()
        filepath = os.path.join(RECORDINGS_PATH, filename)
        with open(filepath, "wb") as f:
            f.write(response.content)
        logging.info(f"Recording saved: {filepath}")

Nawab Mental, [9/29/25 12:45 AM]
send_alert(f"Recording saved: {filepath}")
        # Summarize with xAI
        summary = await query_xai(f"Transcribe and summarize this call recording: {filepath}")
        if summary:
            summary_file = os.path.join(RECORDINGS_PATH, f"{filename}.summary.txt")
            with open(summary_file, "w") as f:
                f.write(summary)
            logging.info(f"Summary saved: {summary_file}")
        return filepath
    except Exception as e:
        logging.error(f"Recording download error: {e}")
        send_alert(f"Recording download error: {e}")
        return None

# Download Telegram voice (unchanged)
async def download_telegram_voice(file_id):
    try:
        file_response = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}")
        file_response.raise_for_status()
        file_path = file_response.json()["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
        return file_url
    except Exception as e:
        logging.error(f"Telegram voice download error: {e}")
        send_alert(f"Telegram voice download error: {e}")
        return None

# Text-to-speech (unchanged)
async def text_to_speech(text):
    try:
        audio = await elevenlabs.text_to_speech.convert(
            voice_id="pNInz6obpgDQGcFmaJgB",
            text=text,
            model_id="eleven_monolingual_v1"
        )
        audio_data = b""
        async for chunk in audio:
            audio_data += chunk
        return audio_data
    except Exception as e:
        logging.error(f"TTS error: {e}")
        send_alert(f"TTS error: {e}")
        return None

# Rate limiter
rate_limiter = RateLimiter(times=RATE_LIMIT_REQUESTS, seconds=RATE_LIMIT_WINDOW)
rate_limiter = RateLimiter(times=RATE_LIMIT_REQUESTS, seconds=RATE_LIMIT_WI
