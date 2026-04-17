#!/bin/python3

import argparse
from requests import post

auth_url = 'http://121.40.111.236:3033/api/auth/login'
checkin_url = 'http://121.40.111.236:3033/api/attendance/check-in'

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:149.0) Gecko/20100101 Firefox/149.0',
           'Accept': 'application/json, text/plain, */*',
           'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,zh-HK;q=0.7,en-US;q=0.6,en;q=0.5',
           'Connection': 'close',
           'Origin': 'http://121.40.111.236:3033',
           'Referer': 'http://121.40.111.236:3033/login',
           'Priority': 'u=0'
        }

payload = {"status":"在校","_fp":{"page_stay_ms":4862,"mouse_points":[{"x":744,"y":178,"t":1776407442452},{"x":743,"y":179,"t":1776407442602},{"x":743,"y":179,"t":1776407442757},{"x":743,"y":179,"t":1776407442907},{"x":743,"y":182,"t":1776407443057},{"x":743,"y":182,"t":1776407443207},{"x":743,"y":182,"t":1776407443358},{"x":709,"y":197,"t":1776407443508},{"x":513,"y":246,"t":1776407443658},{"x":484,"y":247,"t":1776407443829},{"x":481,"y":254,"t":1776407443991},{"x":465,"y":314,"t":1776407444141},{"x":465,"y":315,"t":1776407444292},{"x":465,"y":315,"t":1776407444443},{"x":465,"y":315,"t":1776407444593},{"x":465,"y":315,"t":1776407444743},{"x":465,"y":315,"t":1776407444894},{"x":465,"y":315,"t":1776407445043},{"x":465,"y":315,"t":1776407445194},{"x":465,"y":315,"t":1776407445344},{"x":465,"y":315,"t":1776407445494},{"x":465,"y":315,"t":1776407445645},{"x":465,"y":315,"t":1776407445795},{"x":465,"y":315,"t":1776407445946},{"x":487,"y":369,"t":1776407446096},{"x":502,"y":427,"t":1776407446247},{"x":506,"y":458,"t":1776407446396},{"x":510,"y":466,"t":1776407446547},{"x":510,"y":466,"t":1776407446698},{"x":510,"y":466,"t":1776407446848}],"click_offset_x":-8.4,"click_offset_y":1.2,"screen_resolution":"1536x864","timezone_offset":-480,"browser_lang":"zh-CN","touch_points":1,"has_mouse":1}}

def auth(username : str, password : str):
    global auth_url, headers
    resp = post(auth_url, headers=headers, json={"student_no": username, "password": password})
    data = resp.json().get("data")
    if data is None:
        return None
    return data.get("token")

def auth_name(username : str, name : str):
    global auth_url, headers
    resp = post(auth_url, headers=headers, json={"student_no": username, "name": name})
    data = resp.json().get("data")
    if data is None:
        return None
    return data.get("token")

def checkin(token : str):
    global checkin_url, headers
    from time import sleep, time
    from random import randint
    page_stay_ms = randint(4000, 6000)
    payload["_fp"]["page_stay_ms"] = page_stay_ms
    delta = int(round(time() * 1000)) - payload["_fp"]["mouse_points"]
    for i in payload["_fp"]["mouse_points"]:
        i['t'] += delta
    sleep(page_stay_ms)
    ret, exception = 0, ''
    auth_headers = headers.copy()
    auth_headers['Authorization'] = f"Bearer {token}"
    resp = post(checkin_url, headers=auth_headers, json=payload)
    if resp.json().get("code") != 200:
        ret = 1
        exception = str(resp.json())
    return ret, exception

def main():
    parser = argparse.ArgumentParser(
        description="Please provide your credential in arguments."
    )
    parser.add_argument("-u", dest="username", type=str, help="Your student number")
    parser.add_argument("-p", dest="password", type=str, help="Your password")
    parser.add_argument("-n", dest="name", type=str, help="Your name")
    parser.add_argument('--no-output', dest='stdnull', action='store_true', help="Disable any outputs")

    args = parser.parse_args()

    if args.username is None or (args.password is None and args.name is None):
        parser.print_help()
        return -2

    if args.password: token = auth(args.username, args.password)
    else: token = auth_name(args.username, args.name)
    if token is None:
        if not args.stdnull: print("Login failed")
        return -1

    result, exception = checkin(token)
    if result:
        if not args.stdnull: print(f"Auto-check-in failed, error response: {exception}")
        return -1
    if not args.stdnull: print("Success")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
