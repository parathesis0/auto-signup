import argparse
import hmac
import hashlib
import json
import os
import time
import uuid
import sys

try:
    from curl_cffi import requests as http

    _USE_CURL_CFFI = True
except ImportError:
    import requests as http

    _USE_CURL_CFFI = False

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


def _post(url, headers, json_data):
    if _USE_CURL_CFFI:
        return http.post(url, headers=headers, json=json_data, impersonate="chrome")
    return http.post(url, headers=headers, json=json_data)


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
        resp = _post(LOGIN_URL, DEFAULT_HEADERS, payload)
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
                except Exception:
                    pass

            return token, sign_key
        else:
            print(f"Login failed: {res_json.get('message')}")
            return None, None
    except Exception as e:
        print(f"Login Error: {e}")
        return None, None


def check_in(token, sign_key, status="在校", city=None, district=None, reason=None):
    if not token or not sign_key:
        return False, "Missing Token or Sign Key"

    method = "POST"
    url_path = "/api/attendance/check-in"

    if status == "不在校":
        payload = {
            "status": "不在校",
            "off_campus_city": city or "",
            "off_campus_district": district or "",
            "off_campus_reason": reason or "",
        }
    else:
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
        resp = _post(CHECKIN_URL, headers, payload)
        res_json = resp.json()
        if res_json.get("code") == 200:
            return True, "Success"
        else:
            return False, str(res_json)
    except Exception as e:
        return False, str(e)


def load_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    default_cfg = {
        "username": "",
        "password": "",
        "city": "",
        "district": "",
        "reason": ""
    }
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(default_cfg, f, indent=4, ensure_ascii=False)
    return default_cfg


def main():
    cfg = load_config()

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", default=cfg.get("username"))
    parser.add_argument("-p", "--password", default=cfg.get("password"))
    parser.add_argument(
        "-s", "--status", choices=["在校", "不在校"], default="在校",
        help="签到状态（默认：在校）",
    )
    parser.add_argument("--city", default=cfg.get("city"), help="不在校时的城市")
    parser.add_argument("--district", default=cfg.get("district"), help="不在校时的区县")
    parser.add_argument("--reason", default=cfg.get("reason"), help="不在校原因")
    parser.add_argument("--no-output", action="store_true")
    args = parser.parse_args()

    if not args.username or not args.password:
        print("请在 config.json 中填写 username 和 password，或通过 -u / -p 参数传入")
        return 1

    if args.status == "不在校" and not (args.city and args.district and args.reason):
        print("不在校签到需要提供 --city、--district 和 --reason")
        return 1

    token, sign_key = login(args.username, args.password)
    if not token:
        if not args.no_output:
            print("Login Process Failed")
        return 1

    success, msg = check_in(
        token, sign_key, args.status, args.city, args.district, args.reason
    )
    if not args.no_output:
        print(msg)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
