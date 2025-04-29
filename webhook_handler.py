from flask import Blueprint, request, jsonify
from upstox_api import place_order
import logging

webhook = Blueprint('webhook', __name__)
logger = logging.getLogger(__name__)

@webhook.route('/webhook', methods=['POST'])
def webhook_alert():
    try:
        data = request.get_json()
        logger.info(f"Received webhook data: {data}")

        if not data or 'signal' not in data:
            logger.warning("Invalid payload")
            return jsonify({"status": "error", "message": "Invalid payload"}), 400

        signal = data['signal'].lower()

        if signal == 'buy':
            place_order(transaction_type='BUY')
        elif signal == 'sell':
            place_order(transaction_type='SELL')
        else:
            logger.warning(f"Unknown signal: {signal}")
            return jsonify({"status": "error", "message": "Unknown signal"}), 400

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.exception("Error handling webhook")
        return jsonify({"status": "error", "message": str(e)}), 500
