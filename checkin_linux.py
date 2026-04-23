import argparse
import hmac
import hashlib
import time
import uuid
import requests

# 配置信息
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
    """
    对应 JS 中的 ra(e) 函数
    """
    timestamp = str(int(time.time() * 1000))
    # 生成随机 nonce (JS 是 Math.random().toString(36).slice(2))
    nonce = uuid.uuid4().hex[:10]

    # 构造待签名字符串 C
    # 格式: Method + \n + FullPath + \n + QueryString + \n + Timestamp + \n + Nonce
    # 注意: url_path 必须以 /api 开头且处理掉末尾斜杠
    full_path = "/api" + url_path.split("/api")[-1]

    # 排序参数
    query_string = ""
    if params:
        sorted_keys = sorted(params.keys())
        query_string = "&".join([f"{k}={params[k]}" for k in sorted_keys])

    sign_str = f"{method.upper()}\n{full_path}\n{query_string}\n{timestamp}\n{nonce}"

    # HmacSHA256 签名
    signature = hmac.new(
        sign_key.encode("utf-8"), sign_str.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    return signature, timestamp, nonce


def login(username, password):
    payload = {"student_no": username, "password": password}
    try:
        resp = requests.post(LOGIN_URL, headers=DEFAULT_HEADERS, json=payload)
        res_json = resp.json()
        if res_json.get("code") == 200:
            data = res_json.get("data", {})
            # 这里的 sign_key 通常在登录返回的 data 字段中
            token = data.get("token")
            sign_key = data.get("sign_key")  # 请确认登录返回的字段名是否为 sign_key

            # 如果接口没直接给 sign_key，可能需要从 jwt 里的 payload 解码（你抓包的 jwt 里有它）
            if not sign_key and token:
                import base64, json

                try:
                    payload_part = token.split(".")[1]
                    # 补齐 padding
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

    # 准备请求
    method = "POST"
    url_path = "/api/attendance/check-in"
    payload = {"status": "在校"}

    # 生成签名 Header
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
        resp = requests.post(CHECKIN_URL, headers=headers, json=payload)
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
