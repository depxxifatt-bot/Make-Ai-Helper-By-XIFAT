import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

# ১. Flask অ্যাপ সেটআপ
app = Flask(__name__)
CORS(app)  # Telegram Mini App থেকে CORS পারমিশনের জন্য

# ২. Environment Variables ও চ্যানেল ইউজারনেম সেটআপ
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Render Environment Variables থেকে টোকেন নিবে
CHANNEL_USERNAME = "@XIF4Tofficial"      # 🔴 আপনার নির্দিষ্ট টেলিগ্রাম চ্যানেল ইউজারনেম

# ৩. প্রোটোবাফ মডিউল ইমপোর্ট
import follow_pb2


# হেল্পার ফাংশন: ফাইল থেকে টোকেন লোড করা
def load_access_tokens(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]


# হেল্পার ফাংশন: টেলিগ্রাম চ্যানেল সদস্যপদ চেক করা
def check_channel_membership(user_id):
    if not BOT_TOKEN or not user_id:
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
    params = {"chat_id": CHANNEL_USERNAME, "user_id": user_id}

    try:
        response = requests.get(url, params=params, timeout=5).json()
        if response.get("ok"):
            status = response["result"]["status"]
            # সদস্য, এডমিন বা ক্রিয়েটর হলে ট্রু রিটার্ন করবে
            return status in ["member", "administrator", "creator"]
        return False
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False


# হেল্পার ফাংশন: গেম সার্ভারে ফলো রিকোয়েস্ট পাঠানো
def send_follow_request(target_uid, token):
    try:
        req = follow_pb2.CSFollowReq()
        req.target_id = int(target_uid)

        # TODO: আপনার নেটওয়ার্ক সকেট বা API দিয়ে টোকেন সহ ডাটা গেম সার্ভারে সরবরি পাঠান।
        return True
    except Exception as e:
        print(f"Error sending follow for UID {target_uid}: {e}")
        return False


# ------------------ ROUTES ------------------


# ৪. হোম রুট (Render 404 Error ঠেকানোর জন্য)
@app.route("/", methods=["GET"])
def home():
    return (
        jsonify(
            {"status": "online", "message": "Xerox Follow Bot Server is Running!"}
        ),
        200,
    )


# ৫. মূল ফলো সেন্ড করার API রুট
@app.route("/send-follow", methods=["POST"])
def handle_send_follow():
    data = request.json
    if not data:
        return (
            jsonify({"success": False, "message": "Invalid request payload!"}),
            400,
        )

    target_uid = data.get("uid")
    region = data.get("region")
    telegram_user_id = data.get("user_id")  # ফ্রন্টএন্ড থেকে প্রাপ্ত ইউজারের Telegram ID

    if not target_uid or not region:
        return (
            jsonify(
                {"success": False, "message": "UID and Region are required!"}
            ),
            400,
        )

    # 🔴 ১. চ্যানেল সাবস্ক্রিপশন চেক (@XIF4Tofficial)
    if not telegram_user_id or not check_channel_membership(telegram_user_id):
        return (
            jsonify(
                {
                    "success": False,
                    "must_join": True,
                    "channel_link": "https://t.me/XIF4Tofficial",
                    "message": "You must join our Telegram channel first!",
                }
            ),
            403,
        )

    # 🔴 ২. রিজিয়ন অনুযায়ী টেক্সট ফাইল নির্ধারণ
    if region.upper() == "BD":
        token_file = "bd-access.txt"
    elif region.upper() == "IND":
        token_file = "ind-access.txt"
    else:
        return (
            jsonify({"success": False, "message": "Unsupported Region!"}),
            400,
        )

    # 🔴 ৩. ফাইল থেকে টোকেন লোড করা
    tokens = load_access_tokens(token_file)
    if not tokens:
        return (
            jsonify(
                {
                    "success": False,
                    "message": f"No active tokens found for {region}!",
                }
            ),
            500,
        )

    # 🔴 ৪. ফলো পাঠানোর প্রসেস চালানো
    successful_sends = 0
    for token in tokens:
        success = send_follow_request(target_uid, token)
        if success:
            successful_sends += 1

    return jsonify(
        {
            "success": True,
            "sent_count": successful_sends,
            "message": f"Successfully processed {successful_sends} follows.",
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
