import time
import hmac
import base64
import hashlib
import json
 
ZEGOCLOUD_APP_ID = 1622896018  # Your actual App ID
ZEGOCLOUD_SERVER_SECRET = 'd1aca3225a6c2beb1cee97e67bfe71f2'  # Your actual Server Secret
 
def generate_token(user_id, effective_time=3600):
    expire_time = int(time.time()) + effective_time
    payload = {
        "app_id": ZEGOCLOUD_APP_ID,
        "user_id": user_id,
        "nonce": int(time.time() * 1000),
        "expired": expire_time
    }
 
    json_str = json.dumps(payload, separators=(',', ':'))
    signature = hmac.new(ZEGOCLOUD_SERVER_SECRET.encode(), json_str.encode(), hashlib.sha256).digest()
    token = base64.b64encode(signature + json_str.encode()).decode()
    return token