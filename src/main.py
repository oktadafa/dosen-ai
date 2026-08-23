import asyncio
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
# URL Ngrok akan diisi otomatis di langkah berikutnya, atau bisa dimasukkan manual
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Inisialisasi Application PTB
ptb_app = Application.builder().token(BOT_TOKEN).build()


# ---------------------------------------------------------
# HANDLER BOT
# ---------------------------------------------------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text("Halo! Webhook lokal berhasil berjalan! 🚀")


ptb_app.add_handler(CommandHandler("start", start_command))


# ---------------------------------------------------------
# LIFESPAN FASTAPI (Set & Delete Webhook Otomatis)
# ---------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
  # Saat aplikasi dinyalakan: Inisialisasi bot & set webhook ke Telegram
  await ptb_app.initialize()
  await ptb_app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
  print(f"Webhook berhasil di-set ke: {WEBHOOK_URL}/webhook")

  yield

  # Saat aplikasi dimatikan: Hapus webhook
  await ptb_app.bot.delete_webhook()
  await ptb_app.shutdown()
  print("Webhook berhasil dihapus.")


app = FastAPI(lifespan=lifespan)


# ---------------------------------------------------------
# ENDPOINT WEBHOOK
# ---------------------------------------------------------
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