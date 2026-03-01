import resend
import os

# 自動讀取剛剛在 Render 設定的環境變數
resend.api_key = os.getenv("RESEND_API_KEY")

async def send_confirmation_email(recipient: str, choice: int):
    # 檢查是否有 API Key
    if not resend.api_key:
        print("⚠️ 未設定 RESEND_API_KEY,無法寄信")
        return

    try:
        # 準備郵件內容
        params = {
            "from": "onboarding@resend.dev", # Resend 免費版預設發信位址
            "to": recipient,
            "subject": "選填成功通知",
            "html": f"<p>您好，您已成功完成選填。您的選擇為：<strong>{choice}</strong></p>"
        }
        
        # 發送請求
        resend.Emails.send(params)
        print(f"✅ 郵件已發送至 {recipient}")
        
    except Exception as e:
        print(f"❌ 寄信失敗: {e}")