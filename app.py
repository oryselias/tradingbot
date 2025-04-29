# app.py

from flask import Flask, request
from webhook_handler import handle_webhook
from upstox_api import authenticate
from logger import logger

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data:
        handle_webhook(data)
        return "Webhook received", 200
    else:
        return "No data received", 400

if __name__ == "__main__":
    logger.info("Starting TradingBot Flask server...")
    authenticate()  # Authenticate on startup
    app.run(host='0.0.0.0', port=5000)
