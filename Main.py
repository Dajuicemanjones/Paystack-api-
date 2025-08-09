from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")

@app.route('/')
def home():
    return 'Paystack payment API is running!'

@app.route('/create-payment', methods=['POST'])
def create_payment():
    data = request.get_json()
    amount_usd = data.get('amount')

    if not amount_usd:
        return jsonify({"error": "Amount is required"}), 400

    # Get exchange rate from USD to NGN
    forex_res = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
    forex_data = forex_res.json()
    usd_to_ngn = forex_data["rates"].get("NGN")

    if not usd_to_ngn:
        return jsonify({"error": "Could not fetch exchange rate"}), 500

    amount_ngn = int(amount_usd * usd_to_ngn * 100)  # kobo

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "email": data.get('email'),
        "amount": amount_ngn,
        "currency": "NGN"
    }

    response = requests.post(
        "https://api.paystack.co/transaction/initialize",
        json=payload,
        headers=headers
    )

    return jsonify(response.json())

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)


