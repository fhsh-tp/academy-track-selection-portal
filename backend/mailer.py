import requests
import os

def send_confirmation_email(recipient, student_name, student_id, choice_text, submit_time):
    # 從 Render 環境變數讀取 API Key
    api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("GMAIL_USER") # 必須與你在 Brevo 驗證過的寄件者一致
    
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "api-key": api_key,
        "content-type": "application/json"
    }
    
    payload = {
        "sender": {"email": sender_email, "name": "選填系統"},
        "to": [{"email": recipient}],
        "subject": f"【選填確認】{student_name} 同學",
        "textContent": f"{student_name} 同學您好，您已於 {submit_time} 完成選填：{choice_text}。"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            print(f"✅ 郵件成功經由 API 寄出: {recipient}")
            return True
        else:
            print(f"❌ API 寄信失敗 (Code {response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"❌ 網路連線錯誤: {e}")
        return False