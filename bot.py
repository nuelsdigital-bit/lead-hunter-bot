import logging
import os
import asyncio
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters
from google import genai

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = (
    "You are Lead Hunter AI, a sharp B2B sales strategist for the Nigerian market "
    "(Abuja: Maitama, Wuse, Utako, Guzape, etc.). Your users are ambitious professionals, "
    "service providers, and real estate entrepreneurs. "
    "Give direct, actionable answers only. Maximum 3 short steps or points. "
    "Include ONE ready-to-use pitch line or script snippet, no more. "
    "Keep the entire response under 150 words. No long intros, no restating the question, "
    "no multiple sections or headers. Get straight to the strategy."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_query = update.message.text.strip()
    await update.message.reply_text("🗣️ Lead Hunter AI: Analyzing market data & formulating strategy...")
    
    reply = ""
    for attempt in range(3):
        try:
            # Asynchronous Gemini call to prevent blocking the web server
            response = await client.aio.models.generate_content(
                model="gemini-3.6-flash",
                contents=f"{SYSTEM_PROMPT}\n\nUser Request: {user_query}"
            )
            reply = response.text
            break
        except Exception as e:
            if "503" in str(e) and attempt < 2:
                await asyncio.sleep(2)
                continue
            reply = f"⚠️ Error Details: {str(e)}"
            break
            
    # Telegram limits messages to 4096 characters
    MAX_LEN = 4000
    for i in range(0, len(reply), MAX_LEN):
        await update.message.reply_text(reply[i:i+MAX_LEN])

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    port = int(os.environ.get("PORT", 10000))
    webhook_url = f"https://lead-hunter-bot-bpgf.onrender.com/{TELEGRAM_TOKEN}"
    
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TELEGRAM_TOKEN,
        webhook_url=webhook_url
    )

if __name__ == "__main__":
    main()
    
