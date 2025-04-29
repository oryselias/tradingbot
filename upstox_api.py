# upstox_api.py

import requests
import webbrowser
from config import API_KEY, API_SECRET, REDIRECT_URI, BASE_URL
from logger import logger

access_token = None

def authenticate():
    global access_token
    logger.info("Starting Upstox authentication flow...")

    # Step 1: Generate auth URL
    auth_url = f"https://api-sandbox.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={API_KEY}&redirect_uri={REDIRECT_URI}"

    logger.info(f"Opening auth URL: {auth_url}")
    webbrowser.open(auth_url)
    auth_code = input("Paste the code from the URL after authorization: ").strip()

    # Step 2: Exchange code for access token
    url = f"{BASE_URL}login/authorization/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "code": auth_code,
        "client_id": API_KEY,
        "client_secret": API_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        access_token = response.json()["access_token"]
        logger.info("Successfully obtained access token.")
    else:
        logger.error(f"Failed to obtain access token: {response.text}")

def place_order(symbol, qty, side):
    if not access_token:
        logger.error("No access token. Call authenticate() first.")
        return

    url = f"{BASE_URL}order/place"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    order_data = {
        "quantity": qty,
        "product": "I",  # Intraday
        "transaction_type": side,  # "BUY" or "SELL"
        "exchange": "NSE",
        "symbol": symbol,
        "order_type": "MARKET",
        "validity": "DAY",
        "price": "0",
        "trigger_price": "0",
        "is_amo": False
    }

    response = requests.post(url, headers=headers, json=order_data)
    if response.status_code == 200:
        logger.info(f"Order placed successfully: {response.json()}")
    else:
        logger.error(f"Order placement failed: {response.text}")
