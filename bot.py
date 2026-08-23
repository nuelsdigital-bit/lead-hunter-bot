import logging
import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters
from google import genai
import asyncio

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL") # Automatically provided by Render

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = (
    "You are Lead Hunter AI, an elite, high-end B2B sales strategist, corporate lead generator, "
    "and business consultant specializing in the Nigerian market (especially Abuja: Maitama, Wuse, Utako, Guzape, etc.). "
    "Your users are ambitious professionals, service providers, and real estate entrepreneurs. "
    "Never give generic answers. Provide deep, actionable business intelligence, precise target departments, "
    "culturally tailored Nigerian corporate pitch hooks, objection-handling scripts, and insider market advice "
    "that people would gladly pay a monthly subscription to access. Maintain a professional, sharp, and sharp-witted tone."
)

app = Flask(__name__)

# Initialize Telegram Application for Webhook
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = update.message.text.strip()
    await update.message.reply_text("🗣️ Lead Hunter AI: Analyzing market data & formulating strategy...")
    
    reply = ""
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"{SYSTEM_PROMPT}\n\nUser Request: {user_query}"
            )
            reply = response.text
            break
        except Exception as e:
            if "503" in str(e) and attempt < 2:
                import time
                time.sleep(2)
                continue
            reply = f"⚠️ Error Details: {str(e)}"
            
    await update.message.reply_text(reply)

telegram_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

@app.route("/")
def index():
    return "Lead Hunter AI Webhook Server is Live!"

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    """Endpoint that Telegram calls when a user sends a message"""
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    asyncio.run(telegram_app.process_update(update))
    return "ok", 200

if __name__ == "__main__":
    # Automatically set webhook url on startup
    if RENDER_EXTERNAL_URL:
        import requests
        webhook_url = f"{RENDER_EXTERNAL_URL}/{TELEGRAM_TOKEN}"
        requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={webhook_url}")
        logging.info(f"Webhook set to: {webhook_url}")

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
