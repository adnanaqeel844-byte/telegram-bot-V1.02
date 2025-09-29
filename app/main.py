from fastapi import FastAPI, Request, HTTPException, Header, Query, UploadFile, File
from telegram import Update
from telegram.ext import Application
import logging
import os
import asyncio
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
from .config import TELEGRAM_BOT_TOKEN, WEBHOOK_URL, TASKER_SECRET, WHATSAPP_VERIFY_TOKEN
from .handlers import register_handlers
from .utils import send_alert, query_xai, rate_limiter
from .whatsapp import handle_whatsapp_message
from .videocall import initiate_telegram_video_call, create_whatsapp_call

# Logging setup
logging.basicConfig(filename=f'logs/bot_logs_{os.times()[4]:.0f}.log', level=logging.INFO, format='%(asctime)s - %(message)s')

app = FastAPI()
bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
register_handlers(bot_app)

# Initialize rate limiter
@app.on_event("startup")
async def init_limiter():
    redis_client = redis.from_url("redis://localhost:6379", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_client)

# Telegram webhook
@app.post("/webhook", dependencies=[rate_limiter])
async def telegram_webhook(request: Request):
    try:
        await bot_app.process_update(Update.de_json(await request.json(), bot_app.bot))
        return {"status": "ok"}
    except Exception as e:
        logging.error(f"Telegram webhook error: {e}")
        send_alert(f"Telegram webhook error: {e}")
        return {"status": "error"}

# WhatsApp webhook
@app.get("/whatsapp/webhook")
async def whatsapp_verify(
    hub_mode: str = Query(None),
    hub_verify_token: str = Query(None),
    hub_challenge: str = Query(None)
):
    if hub_mode == "subscribe" and hub_verify_token == WHATSAPP_VERIFY_TOKEN:
        logging.info("WhatsApp webhook verified")
        return hub_challenge
    raise HTTPException(status_code=403, detail="Forbidden")

@app.post("/whatsapp/webhook", dependencies=[rate_limiter])
async def whatsapp_webhook(request: Request):
    try:
        payload = await request.json()
        logging.info(f"WhatsApp webhook received: {payload}")
        await handle_whatsapp_message(payload)
        return {"status": "ok"}
    except Exception as e:
        logging.error(f"WhatsApp webhook error: {e}")
        send_alert(f"WhatsApp webhook error: {e}")
        return {"status": "error"}

Nawab Mental, [9/29/25 12:45 AM]
# Tasker endpoint (updated for recording)
@app.post("/tasker", dependencies=[rate_limiter])
async def tasker_endpoint(request: Request, authorization: str = Header(None)):
    if authorization != TASKER_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    data = await request.json()
    query = data.get("query")
    chat_id = data.get("chat_id")
    phone_number = data.get("phone_number")
    media_id = data.get("media_id")
    media_type = data.get("media_type")
    send_voice = data.get("send_voice", False)
    video_call = data.get("video_call", False)
    call_type = data.get("call_type", "video")
    record_call = data.get("record_call", False)  # New: Enable recording
    
    if not (query and (chat_id or phone_number)):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    logging.info(f"Tasker query: {query} for chat_id: {chat_id}, phone: {phone_number}, video_call: {video_call}, record: {record_call}")
    reply = await query_xai(query)
    
    if reply:
        if video_call:
            if chat_id:
                link = await initiate_telegram_video_call(chat_id, reply, record=record_call)
                await bot_app.bot.send_message(chat_id=chat_id, text=link)
            if phone_number:
                call_id = await create_whatsapp_call(phone_number, call_type, record=record_call)
                if call_id:
                    await send_whatsapp_message(phone_number, text=f"Video call initiated (recording: {record_call}): {call_id}")
        elif send_voice:
            audio_data = await text_to_speech(reply)
            if not audio_data:
                send_alert(f"TTS failure for {chat_id or phone_number}")
                return {"status": "error"}
            if chat_id:
                await bot_app.bot.send_voice(chat_id=chat_id, voice=audio_data)
            if phone_number:
                await send_whatsapp_message(phone_number, voice_data=audio_data)
        else:
            if chat_id:
                await bot_app.bot.send_message(chat_id=chat_id, text=reply)
            if phone_number:
                if media_id and media_type:
                    await send_whatsapp_message(phone_number, media_id=media_id, media_type=media_type)
                else:
                    await send_whatsapp_message(phone_number, text=reply)
        return {"status": "success", "response": reply}
    else:
        send_alert(f"Tasker xAI failure for {chat_id or phone_number}")
        return {"status": "error"}

# WhatsApp media upload (unchanged)
@app.post("/whatsapp/upload", dependencies=[rate_limiter])
async def upload_media(file: UploadFile = File(...), authorization: str = Header(None)):
    if authorization != TASKER_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        content = await file.read()
        headers = {"Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}"}
        files = {"file": (file.filename, content, file.content_type)}
        response = requests.post(
            f"https://graph.facebook.com/{WHATSAPP_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/media",
            headers=headers,
            files=files
        )
        response.raise_for_status()
        media_id = response.json()["id"]
        logging.info(f"Media uploaded: {media_id}")
        return {"status": "success", "media_id": media_id}
    except Exception as e:
        logging.error(f"Media upload error: {e}")
        send_alert(f"Media upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Set Telegram webhook on startup
@app.on_event("startup")
async def startup_webhook():
    if WEBHOOK_URL:
        await bot_app.bot.set_webhook(WEBHOOK_URL)
        logging.info(f"Telegram webhook set: {WEBHOOK_URL}")

]
if name == "main":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
  

  
    uvicorn.run(app, host="0.
