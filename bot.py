import logging
import os
import threading
import time
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from google import genai

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = (
    "You are Lead Hunter AI, an elite, high-end B2B sales strategist, corporate lead generator, "
    "and business consultant specializing in the Nigerian market (especially Abuja: Maitama, Wuse, Utako, Guzape, etc.). "
    "Your users are ambitious professionals, service providers, and real estate entrepreneurs. "
    "Never give generic answers. Provide deep, actionable business intelligence, precise target departments, "
    "culturally tailored Nigerian corporate pitch hooks, objection-handling scripts, and insider market advice "
    "that people would gladly pay a monthly subscription to access. Maintain a professional, sharp, and sharp-witted tone."
)

# Initialize Flask app for Render web service health checks
app = Flask(__name__)

@app.route("/")
def home():
    return "Lead Hunter AI Bot is active and running!"

def run_telegram_bot():
    """Runs the Telegram bot polling loop in a separate background thread."""
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_query = update.message.text.strip()
        await update.message.reply_text("🗣️ Lead Hunter AI: Analyzing market data & formulating strategy...")
        
        reply = ""
        # Automatic retry loop to handle 503 high-demand spikes
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
                    time.sleep(2)  # Wait 2 seconds before retrying
                    continue
                reply = f"⚠️ Error Details: {str(e)}"
            
        await update.message.reply_text(reply)

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("🤖 Telegram Bot Polling Started...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    # Start Telegram bot in a background thread so Flask can run on the main thread
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()

    # Bind Flask to Render's required PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
