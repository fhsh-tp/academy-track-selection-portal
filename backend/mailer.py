import resend
import os
import io
import base64
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 自動讀取環境變數
resend.api_key = os.getenv("RESEND_API_KEY")

# 註冊中文字體 (確保路徑正確)
font_path = os.path.join(os.getcwd(), "frontend", "NotoSansTC-Regular.ttf")
if os.path.exists(font_path):
    pdfmetrics.registerFont(TTFont('NotoSans', font_path))
else:
    print(f"⚠️ 找不到字體檔: {font_path}, PDF 中文可能顯示異常")

def generate_student_pdf(student_name, student_id, choice_name, submit_time):
    """動態產生 PDF 並回傳位元組內容"""
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    
    # 嘗試使用中文字體
    try:
        p.setFont("NotoSans", 16)
    except:
        p.setFont("Helvetica", 16)

    # 繪製 PDF 內容
    p.drawString(100, 800, "114 學年度高一升高二選填類組確認書")
    p.line(100, 790, 500, 790)
    
    p.drawRightString(500, 785, f"系統寄件時間：{submit_time}")
    p.setFontSize(12)
    p.drawString(100, 750, f"學生姓名：{student_name}")
    p.drawString(100, 730, f"學生學號：{student_id}")
    p.drawString(100, 710, f"選填類組：{choice_name}")
    
    p.drawString(100, 650, "--------------------------------------------------")
    p.drawString(100, 630, "家長簽署專欄：")
    p.drawString(100, 580, "本人已知悉子女之選填結果，並予以同意。")
    p.drawString(100, 530, "學生簽名:____________________  日期:2026 / ___ / ___")
    p.drawString(100, 530, "家長簽名:____________________  日期:2026 / ___ / ___")
    p.drawString(100, 530, "家長電話:____________________  日期:2026 / ___ / ___")
    p.drawString(100, 530, "導師簽名:____________________  日期:2026 / ___ / ___")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer.read()

def send_confirmation_email(recipient: str, student_name: str, student_id: str, choice_name: str, submit_time: str):
    """合併後的單一發信函數"""
    if not resend.api_key:
        print("⚠️ 未設定 RESEND_API_KEY, 無法寄信")
        return

    try:
        # 1. 生成 PDF
        pdf_content = generate_student_pdf(student_name, student_id, choice_name, submit_time)
        encoded_pdf = base64.b64encode(pdf_content).decode()

        # 2. 準備郵件與附件
        params = {
            "from": "noreply@resend.dev",
            "to": recipient,
            "subject": f"【確認書】{student_name} 選組結果 (系統紀錄於 {submit_time})",
            "attachments": [...],
            "html": f"""
                <h3>{student_name} 同學您好：</h3>
                <p>您的選填已於 <strong>{submit_time}</strong> 完成。</p>
                <p>選擇類組：{choice_name}</p>
                <p>請下載附件 PDF 並簽名繳回。</p>
            """
        }
        
        resend.Emails.send(params)
    except Exception as e:
        print(f"❌ 失敗: {e}")