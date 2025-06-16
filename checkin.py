import requests
import json
import os

if __name__ == '__main__':
    bot_token = os.environ.get("BOT_TOKEN", "")
    chat_id = os.environ.get("CHAT_ID", "")

    title = ""
    success, fail, repeats = 0, 0, 0
    context = ""

    cookies = os.environ.get("COOKIES", []).split("&")
    if cookies and cookies[0] != "":

        check_in_url = "https://glados.space/api/user/checkin"
        status_url = "https://glados.space/api/user/status"

        referer = 'https://glados.space/console/checkin'
        origin = "https://glados.space"
        useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
        payload = {
            'token': 'glados.one'
        }

        for cookie in cookies:
            checkin = requests.post(check_in_url, headers={'cookie': cookie, 'referer': referer, 'origin': origin,
                                    'user-agent': useragent, 'content-type': 'application/json;charset=UTF-8'}, data=json.dumps(payload))
            state = requests.get(status_url, headers={
                                'cookie': cookie, 'referer': referer, 'origin': origin, 'user-agent': useragent})

            message_status = ""
            points = 0
            message_days = ""

            if checkin.status_code == 200:
                result = checkin.json()
                check_result = result.get('message')
                points = result.get('points')

                result = state.json()
                leftdays = int(float(result['data']['leftDays']))
                email = result['data']['email']

                print(check_result)
                if "Checkin! Got" in check_result:
                    success += 1
                    message_status = "签到成功，会员点数 + " + str(points)
                elif "Checkin Repeats!" in check_result:
                    repeats += 1
                    message_status = "重复签到，明天再来"
                else:
                    fail += 1
                    message_status = "签到失败，请检查..."

                if leftdays is not None:
                    message_days = f"{leftdays} 天"
                else:
                    message_days = "error"
            else:
                email = ""
                message_status = "签到请求URL失败, 请检查..."
                message_days = "error"

            context += "账号: " + email + ", P: " + str(points) +", 剩余: " + message_days + " | "

        title = f'Glados, 成功{success},失败{fail},重复{repeats}'
        print("Send Content:" + "\n", context)

    else:
        title = f'# 未找到 cookies!'

    print("bot_token:", bot_token)
    print("chat_id:", chat_id)
    print("cookies:", cookies)

    if not bot_token or not chat_id:
        print("Telegram BOT_TOKEN or CHAT_ID not set. Not pushing.")
    else:
        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        message_text = title + "\n" + context
        payload = {
            'chat_id': chat_id,
            'text': message_text
        }
        try:
            response = requests.post(telegram_url, data=payload)
            response.raise_for_status()
            print("Telegram message sent successfully.")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send Telegram message: {e}")
