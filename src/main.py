from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from chromadb import PersistentClient
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from .controller.message import message
from .controller.document import document
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

ptb_app = Application.builder().token(BOT_TOKEN).build()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text("Halo! Webhook lokal berhasil berjalan! 🚀")


ptb_app.add_handler(CommandHandler("start", start_command))

ptb_app.add_handler(MessageHandler(filters.TEXT, message))
ptb_app.add_handler(MessageHandler(filters.ATTACHMENT, document))
@asynccontextmanager
async def lifespan(app: FastAPI):
  client = PersistentClient(".venv/chromadb_db")
  collection = client.get_or_create_collection(name="dosen-ai", configuration={
    "hnsw":{
      "space":"cosine",
      "ef_construction":200
    }
  })
  await ptb_app.initialize()
  await ptb_app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
  print(f"Webhook berhasil di-set ke: {WEBHOOK_URL}/webhook")

  yield

  await ptb_app.bot.delete_webhook()
  await ptb_app.shutdown()
  print("Webhook berhasil dihapus.")


app = FastAPI(lifespan=lifespan)


@app.post("/webhook")
async def process_webhook(request: Request):
  """Menerima kiriman update JSON dari Telegram"""
  data = await request.json()
  update = Update.de_json(data, ptb_app.bot)
  await ptb_app.process_update(update)
  return {"status": "ok"}


@app.get("/")
async def root():
  return {"message": "Server Webhook Aktif"}