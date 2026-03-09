import resend
import os

resend.api_key = os.getenv("RESEND_API_KEY")

# 修改參數名稱為 choice_name (字串)
def send_confirmation_email(recipient: str, choice_name: str):
    if not resend.api_key:
        print("⚠️ 未設定 RESEND_API_KEY, 無法寄信")
        return

    try:
        # 【重要】這裡必須修改為你驗證過的網域 Email
        # 例如：noreply@yourdomain.com
        sender_email = "noreply@resend.dev" 
        
        params = {
            "from": sender_email,
            "to": recipient,
            "subject": "114學年度選類組確認信",
            "html": f"""
                <div style="font-family: sans-serif;">
                    <h2>選組結果確認</h2>
                    <p>您好，您:<strong>{choice_name}</strong>已成功完成選填。</p>
                    <p>您的選擇為:<strong>{choice_name}</strong></p>
                    <br>
                    <p style="color: #666; font-size: 0.9em;">本信件為系統自動發送，請勿直接回覆。</p>
                </div>
            """
        }
        
        resend.Emails.send(params)
        print(f"✅ 郵件已發送至 {recipient}")
        
    except Exception as e:
        print(f"❌ 寄信失敗: {e}")