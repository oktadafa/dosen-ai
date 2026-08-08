from telegram.ext import Application,  MessageHandler, filters, ContextTypes
import os 
from dotenv import load_dotenv
from google import genai

from controller.document import document
from controller.message import message

load_dotenv()

client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))



def main():
    app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    # app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ATTACHMENT, document))
    app.add_handler(MessageHandler(filters.TEXT, message))
    print("Bot is Starting")
    app.run_polling()

if __name__ == "__main__":
    main()
