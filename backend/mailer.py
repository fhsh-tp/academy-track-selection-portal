import requests
import os
import base64

def send_confirmation_email(recipient, student_name, student_id, choice_text, submit_time, pdf_bytes):
    print(f"DEBUG: 準備觸發寄信流程，目標: {recipient}...", flush=True)
    
    api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("GMAIL_USER")
    
    if not api_key or not sender_email:
        print("ERROR: API Key 或 Email 設定遺失！請檢查 Render 環境變數。", flush=True)
        return False

    try:
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
            "attachment": [{"name": f"{student_name}_同意書.pdf", "content": pdf_base64}]
        }

        print("DEBUG: 正在呼叫 Brevo API...", flush=True)
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            print(f"✅ 成功寄信給 {recipient}!", flush=True)
            return True
        else:
            print(f"❌ 寄信失敗! Code: {response.status_code}, 內容: {response.text}", flush=True)
            return False
            
    except Exception as e:
        print(f"❌ 寄信函式發生例外錯誤: {str(e)}", flush=True)
        return False