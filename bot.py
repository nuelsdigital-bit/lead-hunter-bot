import logging
import os
import asyncio
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters
from google import genai
from google.genai import types

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
)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_query = update.message.text.strip()
    await update.message.reply_text("🗣️ Lead Hunter AI: Analyzing market data & formulating strategy...")

    reply = ""
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=user_query,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.7,
                )
            )
            reply = response.text
            break
        except Exception as e:
            error_str = str(e)
            if ("429" in error_str or "RESOURCE_EXHAUSTED" in error_str) and attempt < 2:
                await asyncio.sleep(4)
                continue
            reply = f"⚠️ Error Details: {error_str}"
            break

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
