import logging
import os
import asyncio
import traceback
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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = update.message.text.strip()
    
    await update.message.reply_text("🗣️ Lead Hunter AI: Analyzing market data & formulating strategy...")
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"{SYSTEM_PROMPT}\n\nUser Request: {user_query}"
        )
        reply = response.text
    except Exception as e:
        print("CRITICAL ERROR ENCOUNTERED:")
        traceback.print_exc()
        reply = f"⚠️ Error Details: {str(e)}"
        
    await update.message.reply_text(reply)

def main():
    print("🤖 Lead Hunter AI Dynamic Engine Active...")
    
    # Ensure an event loop is explicitly set for Python on this cloud host
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
    
