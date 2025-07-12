import requests
from decimal import Decimal
from django.conf import settings

FLUTTERWAVE_SECRET_KEY = getattr(settings, "FLUTTERWAVE_SECRET_KEY", None)
FLUTTERWAVE_PUBLIC_KEY = getattr(settings, "FLUTTERWAVE_PUBLIC_KEY", None)
FLUTTERWAVE_API_URL = "https://api.flutterwave.com/v3/payments"

def initiate_flutterwave_payment(user, amount):
    """
    Initiates a payment using Flutterwave API and returns the payment link.
    """
    if not FLUTTERWAVE_SECRET_KEY:
        print("❌ Error: Flutterwave API key is missing in settings.")
        return None  # Ensure API key is set

    headers = {
        "Authorization": f"Bearer {FLUTTERWAVE_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    # Ensure the amount is properly formatted
    amount = Decimal(amount).quantize(Decimal("0.00"))

    payload = {
        "tx_ref": f"TX-{user.id}-{int(amount * 1000)}",
        "amount": float(amount),  # Convert amount to float
        "currency": "NGN",
        "redirect_url": settings.FLUTTERWAVE_REDIRECT_URL,  # Use from settings
        "payment_options": "card,banktransfer,ussd",
        "customer": {
            "email": user.email,
            "phonenumber": getattr(user, "mobile", ""),  # Directly access the mobile field
            "name": user.get_full_name()
        },
        "customizations": {
            "title": "My Store Payment",
            "description": "Payment for Order",
            "logo": settings.STORE_LOGO_URL  # Store logo from settings
        }
    }

    try:
        response = requests.post(
            FLUTTERWAVE_API_URL, json=payload, headers=headers, timeout=10
        )

        # Check if the response has content
        if not response.content:
            print("❌ Flutterwave Error: Empty response content")
            return None

        try:
            response_data = response.json()
        except Exception as e:
            print(f"❌ JSON Decode Error: {str(e)}. Response text: {response.text}")
            return None

        if response.status_code == 200 and response_data.get("status") == "success":
            return response_data["data"]["link"]  # Return payment link
        else:
            print(f"❌ Flutterwave Error: {response_data.get('message', 'Unknown error')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {str(e)}")
        return None
