from flask import Flask, request, jsonify
import os
import requests
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

# === CONFIGURATION ===

# Optional: Set these in Fly.io as secrets or environment variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")

EMAIL_SENDER = os.environ.get("EMAIL_SENDER", "")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER", "")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# === UTILITY FUNCTIONS ===

def send_telegram_message(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram not configured.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    response = requests.post(url, json=payload)
    print("Telegram response:", response.text)

def send_discord_message(message: str):
    if not DISCORD_WEBHOOK_URL:
        print("Discord not configured.")
        return
    payload = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    print("Discord response:", response.text)

def send_email(subject: str, body: str):
    if not EMAIL_SENDER or not EMAIL_PASSWORD or not EMAIL_RECEIVER:
        print("Email not configured.")
        return
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print("Email sent successfully")
    except Exception as e:
        print("Failed to send email:", str(e))

# === MAIN ROUTE ===

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print("Received data:", data)

        if not data or "signal" not in data:
            return jsonify({"error": "Invalid data"}), 400

        signal = data["signal"]
        symbol = data.get("symbol", "N/A")
        price = data.get("price", "N/A")
        strategy = data.get("strategy", "Webhook")

        message = f"📡 Signal: {signal.upper()}\n📈 Symbol: {symbol}\n💰 Price: {price}\n📊 Strategy: {strategy}"

        send_telegram_message(message)
        send_discord_message(message)
        send_email(f"Trading Signal - {signal.upper()}", message)

        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print("Webhook error:", str(e))
        return jsonify({"error": "Internal server error"}), 500

# === ENTRYPOINT FOR FLY.IO ===

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
