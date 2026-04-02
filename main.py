from flask import Flask, request, jsonify
from twilio.rest import Client
from dotenv import load_dotenv
from flask_cors import CORS
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
app = Flask(__name__)
CORS(app)

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
EMERGENCY_PHONE_NUMBER = os.getenv("EMERGENCY_PHONE_NUMBER")
print("SID loaded:", bool(TWILIO_ACCOUNT_SID))
print("TOKEN loaded:", bool(TWILIO_AUTH_TOKEN))
print("TWILIO number loaded:", bool(TWILIO_PHONE_NUMBER))
print("Emergency number loaded:", bool(EMERGENCY_PHONE_NUMBER))


@app.route("/")
def home():
    return {"message": "SAFE backend is running"}


@app.route("/send-alert", methods=["POST"])
def send_alert():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "Missing JSON body"}), 400

        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if latitude is None or longitude is None:
            return jsonify({"success": False, "error": "latitude and longitude are required"}), 400

        if not all([
            TWILIO_ACCOUNT_SID,
            TWILIO_AUTH_TOKEN,
            TWILIO_PHONE_NUMBER,
            EMERGENCY_PHONE_NUMBER
        ]):
            return jsonify({"success": False, "error": "Twilio environment variables are not set"}), 500

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        message_body = (
            f"🚨 Emergency! User may be in danger. "
            f"Location: https://maps.google.com/?q={latitude},{longitude}"
        )

        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=EMERGENCY_PHONE_NUMBER
        )

        return jsonify({
            "success": True,
            "message": "Alert sent successfully",
            "sid": message.sid
        }), 200

    except Exception as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
