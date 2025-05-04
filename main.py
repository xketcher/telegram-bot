import os
import requests
from fastapi import FastAPI, Request
from secret_generator import save_secret

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = os.getenv("BASE_URL")  # https://your-app-name.onrender.com
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = FastAPI()

@app.on_event("startup")
async def set_webhook():
    url = f"{API_URL}/setWebhook"
    webhook_url = f"{BASE_URL}/webhook/{BOT_TOKEN}"
    res = requests.post(url, json={"url": webhook_url})
    print("Webhook set:", res.json())

@app.post(f"/webhook/{BOT_TOKEN}")
async def webhook(request: Request):
    data = await request.json()

    message = data.get("message")
    if not message:
        return {"status": "no message"}

    user_id = message["from"]["id"]
    text = message.get("text", "")

    filename = f"{user_id}_secret.so"
    path = save_secret(text, filename)

    # Send .so file back to the user
    with open(path, "rb") as f:
        files = {"document": f}
        payload = {"chat_id": user_id}
        send_url = f"{API_URL}/sendDocument"
        res = requests.post(send_url, data=payload, files=files)

    return {"status": "ok"}
