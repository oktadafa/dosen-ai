from telegram import Update
from telegram.ext import  ContextTypes
import asyncio
import os 
from dotenv import load_dotenv
# from google import genai
from src.utils.split_message_html import split_message_html
from src.database.database import insert_message, get_history_messages, get_images
from telegram.error import BadRequest
import re
import chromadb
import requests
from io import BytesIO
from PIL import Image

from  src.model.model import interaction_ai, embed_ai
load_dotenv()



async def message(update:Update, context:ContextTypes.DEFAULT_TYPE)-> None:
    chunks = []
    images = []
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
        client = chromadb.HttpClient(host=os.getenv('CHROMA_HOST'), port=os.getenv("CHROMA_PORT"), ssl=False)
        collection = client.get_collection(name=os.getenv("CHROMA_NAME"))
        embed_query = await embed_ai(contents=[update.message.text], taskType="RETRIEVAL_QUERY")
        get_query = collection.query(
            query_embeddings=[embed_query.embeddings[0].values],
            n_results=3,
            include=["metadatas", "distances"]
        )
        
        for result in range(len(get_query['ids'][0])):
            if(get_query['distances'][0][result] < 0.7):
                image_id=get_query['metadatas'][0][result]['image_id']
                query_image = get_images(image_id)
            
                request_img = requests.get(query_image['public_url'])
                image = Image.open(BytesIO(request_img.content))
                images.append(image)
                await update.message.reply_text(f"Found a relevant document with a distance of {get_query['distances'][0][result]}:\n{get_query['metadatas'][0][result]}")


        last_message = '' 
        for history in get_history_messages():
            history_message = f"{history['role']}: {history['message']}\n"
            last_message += history_message
        insert_message(role="user", message=update.message.text) 
        main_prompt = [
            f"History percakapan sebelumnya: {last_message}",
            f"Pertanyaan Sekarang: {update.message.text}",
            "jangan mengucapkan kata pembuka seperti 'hallo', 'selamat datang', apabila pada history percakapan sebelumnya sudah ada.",
            "apabila pertanyaan sekarang ada di percakapan sebelumnya, gunakan jawaban sama dengan percakapan sebelumnya",
            "apabila pertanyaan berkaitan dengan mata kuliah, maka data dibawah ini wajib kamu jadikan referensi utama, jika data dibawah kosong atau tidak relevan dengan pertanyaan tersebut maka kamu boleh gunakan pengetahuanmu namun wajib bilang 'untuk materi tersbu, belum ada saat ini', namun ketika user bertanya pertanyaan yang masih relevan dengan sebelumnya kamu tidak perlu bilang ''untuk materi tersbu, belum ada saat ini'",                  
        ]
        main_prompt.extend(images)
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
