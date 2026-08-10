from dotenv import load_dotenv
from telegram import Update
from telegram.ext import  ContextTypes
from pdf2image import convert_from_path
import cloudinary.uploader
import cloudinary
import os
import chromadb
from google import genai
from google.genai import types
import io
from database.database import insert_image, insert_message
from utils.random_string import random_string
load_dotenv()

async def document(update: Update, context: ContextTypes) -> None:
    if update.message.document:
        if update.message.document.mime_type == "application/pdf":
            try:
                message_id = insert_message("user", update.message.caption )
                gemini = genai.Client(api_key=os.getenv("GENAI_API_KEY"))
                client = chromadb.PersistentClient(path=".venv/chromadb_db")
                collection = client.get_collection(name="dosen-ai")
                cloudinary.config(
                    cloud_name="ddgad1ttp",
                    api_key=os.getenv("CLOUDINARY_API_KEY"),
                    api_secret=os.getenv("CLOUDINARY_API_SECRET")
                )
                document = update.message.document
                pdf_file = await document.get_file()
                images = convert_from_path(pdf_file.file_path, fmt='jpeg')    
                for i in range(len(images)):
                    stream = io.BytesIO()
                    images[i].save(stream, "JPEG")
                    image_bytes = stream.getvalue()
                    convert_embed = gemini.models.embed_content(
                        model="gemini-embedding-2",
                        contents=[
                            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
                        ],
                        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")

                    )
                    public_id = random_string()
                    response = cloudinary.uploader.upload(image_bytes, public_id=public_id, folder="pdf_pages")
                    image_id = insert_image(response["secure_url"], f"{document.file_name}_page_{i + 1}", message_id)
                    collection.add(embeddings=[convert_embed.embeddings[0].values], ids=[f"image_{collection.count() + 1}"], metadatas=[{"title": f"{document.file_name}_page_{i + 1}", "image_id": str(image_id)}])

              
            except Exception as e:
                print(f"Error occurred while processing the document: {e}")
                await update.message.reply_text("Sorry, I encountered an error while processing your document.")
        else:
            return await update.message.reply_text("Please send a PDF document.")
    else:
        await update.message.reply_text("No document found in the message.")