import argparse
import hmac
import hashlib
import time
import uuid
from curl_cffi import requests

BASE_DOMAIN = "sincst.cn"
BASE_URL = f"https://{BASE_DOMAIN}"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
CHECKIN_URL = f"{BASE_URL}/api/attendance/check-in"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Origin": f"https://{BASE_DOMAIN}",
    "Referer": f"https://{BASE_DOMAIN}/login",
    "Content-Type": "application/json",
}


def generate_signature(method, url_path, sign_key, params=None):
    timestamp = str(int(time.time() * 1000))
    nonce = uuid.uuid4().hex[:10]

    full_path = "/api" + url_path.split("/api")[-1]

    query_string = ""
    if params:
        sorted_keys = sorted(params.keys())
        query_string = "&".join([f"{k}={params[k]}" for k in sorted_keys])

    sign_str = f"{method.upper()}\n{full_path}\n{query_string}\n{timestamp}\n{nonce}"

    signature = hmac.new(
        sign_key.encode("utf-8"), sign_str.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    return signature, timestamp, nonce


def login(username, password):
    payload = {"student_no": username, "password": password}
    try:
        resp = requests.post(
            LOGIN_URL, headers=DEFAULT_HEADERS, json=payload, impersonate="chrome"
        )
        res_json = resp.json()
        if res_json.get("code") == 200:
            data = res_json.get("data", {})
            token = data.get("token")
            sign_key = data.get("sign_key")

            if not sign_key and token:
                import base64, json

                try:
                    payload_part = token.split(".")[1]
                    decoded = base64.b64decode(
                        payload_part + "=" * (-len(payload_part) % 4)
                    )
                    sign_key = json.loads(decoded).get("sign_key")
                except:
                    pass

            return token, sign_key
        else:
            print(f"Login failed: {res_json.get('message')}")
            return None, None
    except Exception as e:
        print(f"Login Error: {e}")
        return None, None


def check_in(token, sign_key):
    if not token or not sign_key:
        return False, "Missing Token or Sign Key"

    method = "POST"
    url_path = "/api/attendance/check-in"
    payload = {"status": "在校"}

    signature, timestamp, nonce = generate_signature(method, url_path, sign_key)

    headers = DEFAULT_HEADERS.copy()
    headers.update(
        {
            "Authorization": f"Bearer {token}",
            "X-Timestamp": timestamp,
            "X-Nonce": nonce,
            "X-Sign": signature,
            "Referer": f"https://{BASE_DOMAIN}/group/today",
        }
    )

    try:
        resp = requests.post(
            CHECKIN_URL, headers=headers, json=payload, impersonate="chrome"
        )
        res_json = resp.json()
        if res_json.get("code") == 200:
            return True, "Success"
        else:
            return False, str(res_json)
    except Exception as e:
        return False, str(e)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", required=True)
    parser.add_argument("-p", "--password", required=True)
    parser.add_argument("--no-output", action="store_true")
    args = parser.parse_args()

    token, sign_key = login(args.username, args.password)
    if not token:
        if not args.no_output:
            print("Login Process Failed")
        return 1

    success, msg = check_in(token, sign_key)
    if not args.no_output:
        print(msg)

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
