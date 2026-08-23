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
    "You are Lead Hunter AI, an elite, high-end B2B sales strategist, corporate lead generator, "
    "and business consultant specializing in the Nigerian market (especially Abuja: Maitama, Wuse, Utako, Guzape, etc.). "
    "Your users are ambitious professionals, service providers, and real estate entrepreneurs. "
    "Never give generic answers. Provide deep, actionable business intelligence, precise target departments, "
    "culturally tailored Nigerian corporate pitch hooks, objection-handling scripts, and insider market advice "
    "that people would gladly pay a monthly subscription to access. Maintain a professional, sharp, and sharp-witted tone."
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
                model="gemini-2.0-flash",
                contents=f"{SYSTEM_PROMPT}\n\nUser Request: {user_query}"
            )
            reply = response.text
            break
        except Exception as e:
            if "503" in str(e) and attempt < 2:
                # Safely sleep in async without freezing the server
                await asyncio.sleep(2)
                continue
            reply = f"⚠️ Error Details: {str(e)}"
            break
            
    await update.message.reply_text(reply)

def main():
    # Initialize the Telegram Application natively
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    port = int(os.environ.get("PORT", 10000))
    webhook_url = f"https://lead-hunter-bot-bpql.onrender.com/{TELEGRAM_TOKEN}"
    
    # Run using the built-in async web server
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TELEGRAM_TOKEN,
        webhook_url=webhook_url
    )

if __name__ == "__main__":
    main()
    
