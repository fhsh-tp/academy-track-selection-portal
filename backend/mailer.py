import requests
import os
import base64
import io
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# 註冊中文字型 (確保 NotoSansTC-Regular.ttf 在專案根目錄或指定路徑)
# 如果檔案在其他資料夾，請修改路徑，例如 'backend/NotoSansTC-Regular.ttf'
try:
    pdfmetrics.registerFont(TTFont('backend', 'NotoSansTC-Regular.ttf'))
except Exception as e:
    print(f"DEBUG: 字型註冊失敗: {e}", flush=True)

def generate_formal_pdf(student_name, student_id, choice_text, submit_time):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    
    # 建立中文字型樣式
    normal_style = ParagraphStyle('Normal', fontName='NotoSans', fontSize=12, leading=18)
    title_style = ParagraphStyle('Title', fontName='NotoSans', fontSize=18, leading=22, alignment=1)
    
    elements = []
    elements.append(Paragraph("臺北市立復興高級中學", title_style))
    elements.append(Paragraph("114學年度選填志願確認同意書", title_style))
    elements.append(Spacer(1, 30))
    
    declaration = f"學生 {student_name} (學號: {student_id}) 於 {submit_time} 完成選填，所選類組為：{choice_text}。"
    elements.append(Paragraph(declaration, normal_style))
    elements.append(Spacer(1, 60))
    
    # 簽名表格
    data = [["學生簽名", "家長簽名", "導師簽名"], [" ", " ", " "]]
    sig_table = Table(data, colWidths=[160, 160, 160], rowHeights=[30, 50])
    sig_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 1), (0, 1), 1, colors.black),
        ('LINEBELOW', (1, 1), (1, 1), 1, colors.black),
        ('LINEBELOW', (2, 1), (2, 1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'NotoSans'),
    ]))
    elements.append(sig_table)
    
    doc.build(elements)
    return buffer.getvalue()

def send_confirmation_email(recipient, student_name, student_id, choice_text, submit_time, pdf_bytes):
    # 【關鍵除錯】如果 recipient 是空的，這裡會印出來
    print(f"DEBUG: 準備發送給收件人: '{recipient}'", flush=True)
    
    if not recipient or recipient == "undefined" or recipient == "null":
        print("ERROR: 收件人 email 為空或格式錯誤！", flush=True)
        return False

    api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("GMAIL_USER")
    
    try:
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        payload = {
            "sender": {"email": sender_email, "name": "選填系統"},
            "to": [{"email": recipient}], # 這邊務必確保 recipient 是字串
            "subject": f"【確認信】{student_name} 的選填結果",
            "textContent": f"你好 {student_name}，你的志願已送出。",
            "attachment": [{"name": "確認書.pdf", "content": pdf_base64}]
        }
        
        headers = {"api-key": api_key, "content-type": "application/json"}
        response = requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
        
        if response.status_code == 201:
            return True
        else:
            print(f"❌ Brevo 錯誤內容: {response.text}", flush=True)
            return False
    except Exception as e:
        print(f"❌ 寄信失敗: {e}", flush=True)
        return False
