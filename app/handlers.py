from telegram.ext import CommandHandler, MessageHandler, filters
from .utils import send_alert, query_xai, download_telegram_voice, text_to_speech, generate_jitsi_link
from .videocall import initiate_telegram_video_call

async def start(update, _):
    await update.message.reply_text("Bot started! Send text, voice, or /video_call for video chat with recording.")
    send_alert(f"User {update.effective_user.id} started bot")

async def handle_text(update, _):
    msg = update.message.text
    user_id = update.effective_user.id
    logging.info(f"User {user_id}: {msg}")
    
    reply = await query_xai(msg)
    if reply:
        await update.message.reply_text(reply)
        logging.info(f"xAI response to {user_id}: {reply}")
    else:
        await update.message.reply_text("Sorry, something went wrong!")
    
    if "error" in msg.lower():
        send_alert(f"Error from {user_id}: {msg}")

async def handle_voice(update, _):
    user_id = update.effective_user.id
    voice_file_id = update.message.voice.file_id
    logging.info(f"Telegram voice from {user_id}: {voice_file_id}")
    
    voice_url = await download_telegram_voice(voice_file_id)
    if voice_url:
        query_text = "Transcribe and respond to this voice message."
        reply = await query_xai(query_text, media_url=voice_url)
        if reply:
            audio_data = await text_to_speech(reply)
            if audio_data:
                await update.message.reply_voice(voice=audio_data)
                logging.info(f"xAI voice response to {user_id}: {reply}")
            else:
                await update.message.reply_text(reply)
                logging.info(f"xAI text fallback to {user_id}: {reply}")
        else:
            await update.message.reply_text("Sorry, couldn't process the voice!")
        if "error" in reply.lower():
            send_alert(f"Error in Telegram voice from {user_id}")
    else:
        await update.message.reply_text("Failed to download voice!")

Nawab Mental, [9/29/25 12:45 AM]
async def handle_video_call(update, _):
    user_id = update.effective_user.id
    logging.info(f"Video call request from {user_id}")
    call_link = await initiate_telegram_video_call(user_id, record=True)  # Enable recording
    await update.message.reply_text(f"Join video call with recording: {call_link}")

def register_handlers(bot_app):
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    bot_app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    bot_app.add_handler(CommandHandler("video_call", handle_video_call))
