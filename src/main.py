from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os 
from dotenv import load_dotenv
from google import genai
from utils.split_message_html import split_message_html

load_dotenv()

client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))

async def start(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello, I'm your dosen")

async def file(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.photo:
        print(update.message.photo, 'test')
    if update.message.document:
        print(update.message.document.file_name,'test')
    await update.message.reply_text(f"Ypu sai: {update.message.text}")
   

async def message(update:Update, context:ContextTypes.DEFAULT_TYPE)-> None:
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input=update.message.text
        )
        chunks = split_message_html(interaction.output_text)
        for chunk in chunks:
            await update.message.reply_text(chunk, parse_mode="HTML")  
    except Exception as e:
        print(f"Error occurred: {e}")
        await update.message.reply_text("Sorry, I encountered an error while processing your request.")
    finally:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="cancel")

def main():
    app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.ATTACHMENT, file))
    app.add_handler(MessageHandler(filters.TEXT, message))
    print("Bot is Starting")
    app.run_polling()

if __name__ == "__main__":
    main()
