import logging
import requests
import asyncio
from .config import WHATSAPP_ACCESS_TOKEN, WHATSAPP_VERSION, WHATSAPP_PHONE_NUMBER_ID
from .utils import generate_call_context, send_alert, generate_jitsi_link, download_recording

CALLING_API_URL = f"https://graph.facebook.com/{WHATSAPP_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/calls"

# Initiate Telegram video call (Jitsi link) with recording
async def initiate_telegram_video_call(user_id, chat_history="", record=False):
    context = await generate_call_context(chat_history) if chat_history else "Ready for video call."
    link = generate_jitsi_link(record=record)
    logging.info(f"Telegram video call link for {user_id}: {link} | Record: {record} | Context: {context}")
    return f"{context}\nJoin (recording enabled): {link}"

Nawab Mental, [9/29/25 12:45 AM]
# Create WhatsApp video call with recording
async def create_whatsapp_call(callee_phone, call_type="video", record=False):
    headers = {"Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {"callee_phone_number": callee_phone, "call_type": call_type, "record": record}
    try:
        response = requests.post(CALLING_API_URL, headers=headers, json=data)
        response.raise_for_status()
        call_id = response.json()["call_id"]
        logging.info(f"WhatsApp {call_type} call created: {call_id} | Record: {record}")
        return call_id
    except Exception as e:
        logging.error(f"WhatsApp call creation error: {e}")
        send_alert(f"WhatsApp call error: {e}")
        return None

# Handle WhatsApp call webhook (updated for recording)
async def handle_whatsapp_call_webhook(payload):
    try:
        call = payload["entry"][0]["changes"][0]["value"]["calls"][0]
        call_id = call["id"]
        from_phone = call["from"]
        call_type = call.get("call_type", "video")
        logging.info(f"Incoming WhatsApp {call_type} call {call_id} from {from_phone}")
        # Auto-accept
        accept_data = {"call_id": call_id, "status": "accepted"}
        headers = {"Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}"}
        requests.post(f"{CALLING_API_URL}/{call_id}/accept", headers=headers, json=accept_data)
        send_alert(f"Accepted {call_type} call from {from_phone}")
        # If recording enabled, wait for webhook (handled in handle_whatsapp_message)
    except Exception as e:
        logging.error(f"WhatsApp call webhook error: {e}")
        send_alert(f"WhatsApp call webhook error: {e}") 
