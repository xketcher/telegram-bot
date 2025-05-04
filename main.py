import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, ContextTypes, MessageHandler, filters
from telegram.ext.fastapi import create_app
from secret_generator import save_secret

TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = os.getenv("BASE_URL")  # Required for webhook

WEBHOOK_PATH = f"/webhook/{TOKEN}"
app = FastAPI()

telegram_app: Application = ApplicationBuilder().token(TOKEN).build()

@telegram_app.message_handler(filters.TEXT & ~filters.COMMAND)
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    secret = update.message.text
    filename = f"{update.effective_user.id}_secret.so"
    path = save_secret(secret, filename)

    await update.message.reply_text("Here's your .so file:")
    await update.message.reply_document(open(path, "rb"))

app.mount(WEBHOOK_PATH, create_app(telegram_app))

@app.on_event("startup")
async def set_webhook():
    await telegram_app.bot.set_webhook(url=f"{BASE_URL}{WEBHOOK_PATH}")
