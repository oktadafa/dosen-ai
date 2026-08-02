import asyncio

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os 
from dotenv import load_dotenv
from google import genai
from utils.split_message_html import split_message_html
from database.database import insert_message, get_history_messages


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
    chunks = []
    async def keep_typing():
       try:
           while True:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            await asyncio.sleep(4)
       except Exception as e:
            print(f"Error occurred while sending typing action: {e}")
            pass
            
    typing_task = asyncio.create_task(keep_typing())        
    try: 
        last_message = '' 
        for history in get_history_messages():
            history_message = f"{history['role']}: {history['message']}\n"
            last_message += history_message
        insert_message(role="user", message=update.message.text) 
        main_prompt = [
            # "Kamu adalah assisten , yang membantu mahasiswa paham segala hal.",
            # "Berikan jawaban yang jelas, ringkas, dan mudah dipahami. Gunakan bahasa yang tidak terlalu formal.",
            f"History percakapan sebelumnya: {last_message}",
f"Pertanyaan Sekarang: {update.message.text}"
        ]
        interaction =await client.aio.models.generate_content(
            model="gemini-3.6-flash",
            contents=main_prompt
        )
        insert_message(role="assistant_dosen", message=interaction.text)
        chunks = split_message_html(interaction.text)
  

    except Exception as e:
        print(f"Error occurred: {e}")
        await update.message.reply_text("Sorry, I encountered an error while processing your request.")
    finally:
         typing_task.cancel()
         await asyncio.gather(typing_task, return_exceptions=True) 
    for chunk in chunks:
         await update.message.reply_text(chunk, parse_mode="HTML")  

def main():
    app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.ATTACHMENT, file))
    app.add_handler(MessageHandler(filters.TEXT, message))
    print("Bot is Starting")
    app.run_polling()

if __name__ == "__main__":
    main()
