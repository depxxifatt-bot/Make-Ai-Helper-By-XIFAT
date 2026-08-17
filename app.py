import os
from flask import Flask, request, jsonify
from flask_cors import CORS

# আপনার আগের জেনারেট করা প্রোটোবাফ মডিউলটি ইমপোর্ট করুন
import follow_pb2

app = Flask(__name__)
CORS(app)  # Telegram Mini App থেকে Cross-Origin রিকোয়েস্ট অনুমতির জন্য

# Access Token ফাইল পড়ার হেল্পার ফাংশন
def load_access_tokens(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        # খালি লাইন ছাড়া বাকি টোকেন/ক্রেডেনশিয়াল রিটার্ন করবে
        return [line.strip() for line in f.readlines() if line.strip()]

# ফলো সেন্ড করার মেইন লজিক ফংশন
def send_follow_request(target_uid, token):
    """
    এখানে আপনার মূল গেম সার্ভারে রিকোয়েস্ট পাঠানোর লজিকটি বসবে।
    follow_pb2 ব্যবহার করে গেম সার্ভারের সকেটে রিকোয়েস্ট যাবে।
    """
    try:
        # Protobuf Message তৈরি
        req = follow_pb2.CSFollowReq()
        req.target_id = int(target_uid)
        
        # TODO: আপনার আসল সকেট/HTTP নেটওয়ার্ক লাইব্রেরি (যেমন asyncio/requests) 
        # দিয়ে টোকেন সহ গেম সার্ভারে ডেটা পাঠান।
        
        # সফল হলে True রিটার্ন করবে
        return True
    except Exception as e:
        print(f"Error sending follow: {e}")
        return False

@app.route("/send-follow", methods=["POST"])
def handle_send_follow():
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "Invalid request payload"}), 400

    target_uid = data.get("uid")
    region = data.get("region")

    if not target_uid or not region:
        return jsonify({"success": False, "message": "UID and Region are required"}), 400

    # রিজিয়ন অনুযায়ী টেক্সট ফাইল সিলেক্ট করা
    if region.upper() == "BD":
        token_file = "bd-access.txt"
    elif region.upper() == "IND":
        token_file = "ind-access.txt"
    else:
        return jsonify({"success": False, "message": "Unsupported Region"}), 400

    # টোকেন লোড করা
    tokens = load_access_tokens(token_file)
    if not tokens:
        return jsonify({"success": False, "message": f"No active tokens found in {token_file}"}), 500

    successful_sends = 0

    # প্রতিটি টোকেন ব্যবহার করে ফলো রিকোয়েস্ট পাঠানো
    for token in tokens:
        success = send_follow_request(target_uid, token)
        if success:
            successful_sends += 1

    return jsonify({
        "success": True,
        "sent_count": successful_sends,
        "message": f"Successfully processed {successful_sends} follows."
    })

if __name__ == "__main__":
    # সার্ভার রান করার অংশ
    app.run(host="0.0.0.0", port=5000, debug=True)
