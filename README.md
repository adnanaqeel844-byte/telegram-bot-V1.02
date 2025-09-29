# Telegram & WhatsApp Bot with xAI, Tasker, Media/Voice/Video Calls, and Recording Support

## Setup Instructions
1. Unzip and Navigate:
   - Unzip telegram-bot.zip.
   - cd telegram-bot

2. Environment Variables:
   - Copy .env.example to .env.
   - Fill in vars (see comments).
   - RECORDINGS_PATH: Local dir for saved recordings (auto-created).

3. WhatsApp Setup:
   - Meta Dashboard: Enable "Call Recording" for voice/video (beta for video).
   - Set webhook: https://your-domain.com/whatsapp/webhook, subscribe to messages, calls, recording_available.
   - Verify: curl "http://localhost:8000/whatsapp/webhook?hub_mode=subscribe&hub_verify_token=your_token&hub_challenge=test".

4. Jitsi Setup (Telegram):
   - For recording, deploy Jibri on a Jitsi server (external; see https://jitsi.github.io/handbook/docs/devops-guide/jibri).

5. Run with Docker:
   `bash
   docker-compose up --build
