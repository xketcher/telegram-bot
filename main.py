import os
import requests
from fastapi import FastAPI, Request
from so_generator import generate_so_with_secret

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = os.getenv("BASE_URL")  # e.g., https://your-app-name.onrender.com
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = FastAPI()

@app.on_event("startup")
async def set_webhook():
    webhook_url = f"{BASE_URL}/webhook/{BOT_TOKEN}"
    res = requests.post(f"{API_URL}/setWebhook", json={"url": webhook_url})
    print("Webhook set response:", res.json())

@app.post(f"/webhook/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    message = data.get("message")

    if not message:
        return {"status": "no message"}

    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    if not text:
        return {"status": "empty message"}

    # Generate .so file with the user's secret
    filename = f"{chat_id}_secret.so"
    so_path = generate_so_with_secret(text, filename)

    # Send the .so file back to the user
    with open(so_path, "rb") as file:
        files = {"document": file}
        payload = {"chat_id": chat_id}
        res = requests.post(f"{API_URL}/sendDocument", data=payload, files=files)

    return {"status": "ok"}
