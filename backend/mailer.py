import requests
import os
import base64

def send_confirmation_email(recipient, student_name, student_id, choice_text, submit_time, pdf_bytes):
    api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("GMAIL_USER")
    
    # 直接將記憶體中的 bytes 轉為 base64
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "api-key": api_key,
        "content-type": "application/json"
    }
    
    payload = {
        "sender": {"email": sender_email, "name": "選填系統"},
        "to": [{"email": recipient}],
        "subject": f"【選填確認】{student_name} 同學",
        "textContent": f"{student_name} 同學您好，您已於 {submit_time} 完成選填：{choice_text}。\n請參閱附件中的同意書。",
        "attachment": [
            {
                "name": f"{student_name}_同意書.pdf",
                "content": pdf_base64
            }
        ]
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.status_code == 201