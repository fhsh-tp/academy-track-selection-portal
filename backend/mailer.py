import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def send_confirmation_email(recipient, student_name, student_id, choice_text, submit_time):
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_PASSWORD") # 填入 16 位密碼

    if not gmail_user or not gmail_password:
        return False

    msg = MIMEMultipart()
    msg['From'] = f"教務處選填系統 <{gmail_user}>"
    msg['To'] = recipient
    msg['Subject'] = f"【選填確認書】{student_name} 同學"

    body = f"您好，您已於 {submit_time} 完成選填：{choice_text}。請查收附件 PDF。"
    msg.attach(MIMEText(body, 'plain'))

    # PDF 附加邏輯 (假設你有 generate_pdf)
    try:
        from .pdf_gen import generate_student_pdf
        pdf_content = generate_student_pdf(student_name, student_id, choice_text, submit_time)
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(pdf_content)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{student_id}_confirm.pdf"')
        msg.attach(part)
    except: pass

    try:
        # 使用 587 埠號，這在 Render 上成功率最高
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=20)
        server.starttls() # 必須在 login 前啟動加密
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
        server.quit()
        print(f"✅ 郵件寄送成功: {recipient}")
        return True
    except Exception as e:
        # 這裡的 print 非常重要，出錯時請看 Render Logs 噴出什麼
        print(f"❌ 寄信失敗詳細原因: {str(e)}")
        return False