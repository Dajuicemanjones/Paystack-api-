from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Get your secret key from Render environment variables
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")

# Paystack API endpoint
PAYSTACK_BASE_URL = "https://api.paystack.co/transaction/initialize"

# Example USD to NGN rate fetcher (from exchangerate.host)
def convert_usd_to_ngn(amount_usd):
    try:
        rate_res = requests.get("https://api.exchangerate.host/latest?base=USD&symbols=NGN")
        rate = rate_res.json()["rates"]["NGN"]
        return int(amount_usd * rate * 100)  # Paystack wants amount in kobo
    except:
        return int(amount_usd * 1600 * 100)  # fallback rate

@app.route('/')
def home():
    return 'Paystack payment API is running!'

@app.route('/create-payment', methods=['POST'])
def create_payment():
    try:
        data = request.get_json()

        if not data or "email" not in data or "amount_usd" not in data:
            return jsonify({"error": "Please provide email and amount_usd"}), 400

        email = data["email"]
        amount_usd = float(data["amount_usd"])
        amount_ngn_kobo = convert_usd_to_ngn(amount_usd)

        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "email": email,
            "amount": amount_ngn_kobo,
            "currency": "NGN",
            "callback_url": "https://yourstore.com/payment-success"  # change to your callback
        }

        response = requests.post(PAYSTACK_BASE_URL, headers=headers, json=payload)
        return jsonify(response.json())

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

