from telegram import Update
from telegram.ext import  ContextTypes
import asyncio
# import os 
from dotenv import load_dotenv
# from google import genai
from utils.split_message_html import split_message_html
from database.database import insert_message, get_history_messages
from telegram.error import BadRequest
import re
from  model.model import interaction_ai
load_dotenv()



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
            f"History percakapan sebelumnya: {last_message}",
            f"Pertanyaan Sekarang: {update.message.text}"
        ]
  
        interaction = await interaction_ai(prompt=main_prompt)
    
        insert_message(role="assistant_dosen", message=interaction)
        chunks = split_message_html(interaction)
  

    except Exception as e:
        print(f"Error occurred: {e}")
        await update.message.reply_text("Sorry, I encountered an error while processing your request.")
    finally:
         typing_task.cancel()
         await asyncio.gather(typing_task, return_exceptions=True) 
    for chunk in chunks:
         try:
            await update.message.reply_text(chunk, parse_mode="HTML")
         except BadRequest as e:
            if "Can't parse entities" in str(e):
                clean_text = re.sub(r'<[^>]+>', '', chunk)
                await update.message.reply_text(clean_text)
            else:
                raise e            
