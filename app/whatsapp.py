import logging
import requests
import asyncio
from .config import WHATSAPP_VERIFY_TOKEN, WHATSAPP_ACCESS_TOKEN, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_VERSION
from .utils import send_alert, query_xai, download_media, text_to_speech, download_recording
from .videocall import create_whatsapp_call, handle_whatsapp_call_webhook

WHATSAPP_API_URL = f"https://graph.facebook.com/{WHATSAPP_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
MEDIA_API_URL = f"https://graph.facebook.com/{WHATSAPP_VERSION}"
CALLING_API_URL = f"https://graph.facebook.com/{WHATSAPP_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/calls"

# Download media (unchanged)
async def download_media(media_id):
    headers = {"Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}"}
    try:
        response = requests.get(f"{MEDIA_API_URL}/{media_id}", headers=headers)
        response.raise_for_status()
        media_url = response.json()["url"]
        media_response = requests.get(media_url, headers=headers)
        media_response.raise_for_status()
        return media_url
    except Exception as e:
        logging.error(f"Media download error: {e}")
        send_alert(f"Media download error: {e}")
        return None

# Send WhatsApp text, media, voice, or video call with recording
async def send_whatsapp_message(to_phone, text=None, media_id=None, media_type=None, voice_data=None, call_type="video", record=False):
    headers = {"Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": to_phone}
    if text:
        data.update({"type": "text", "text": {"body": text}})
    elif media_id and media_type in ["image", "video", "document", "audio"]:
        data.update({"type": media_type, media_type: {"id": media_id}})
    elif voice_data:
        # Upload voice first
        headers_upload = {"Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}"}
        files = {"file": ("voice.mp3", voice_data, "audio/mpeg")}
        response = requests.post(f"{MEDIA_API_URL}/{WHATSAPP_PHONE_NUMBER_ID}/media", headers=headers_upload, files=files)
        response.raise_for_status()
        media_id = response.json()["id"]
        data.update({"type": "audio", "audio": {"id": media_id}})
    elif call_type:
        # Initiate video call with recording
        call_data = {"callee_phone_number": to_phone, "call_type": call_type, "record": record}  # Enable recording
        call_response = requests.post(CALLING_API_URL, headers=headers, json=call_data)
        call_response.raise_for_status()
        call_id = call_response.json()["call_id"]
        data.update({"type": "call", "call": {"id": call_id}})
    try:
        response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
        response.raise_for_status()
        logging.info(f"WhatsApp message/call sent to {to_phone}: {text or media_type or 'voice' or f'{call_type} (record={record})'}")
    except Exception as e:
        logging.error(f"WhatsApp send error: {e}")
        send_alert(f"WhatsApp send error to {to_phone}: {e}") 
