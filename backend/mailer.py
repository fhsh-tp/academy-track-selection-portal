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

# --- 1. 修正字型路徑與註冊名稱 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # backend/
ROOT_DIR = os.path.dirname(BASE_DIR)                  # 專案根目錄
# 確保指向 frontend/NotoSansTC-Regular.ttf
FONT_PATH = os.path.join(ROOT_DIR, "frontend", "NotoSansTC-Regular.ttf")

# 這裡的名稱 'ChineseFont' 就是之後所有 Style 要用的 fontName
try:
    pdfmetrics.registerFont(TTFont('ChineseFont', FONT_PATH))
    print(f"✅ 字型註冊成功: {FONT_PATH}", flush=True)
except Exception as e:
    print(f"❌ 字型註冊失敗: {e}", flush=True)

def generate_formal_pdf(student_name, student_id, choice_text, submit_time):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    
    # --- 2. 修正樣式中的 fontName ---
    # 這裡的 fontName 必須與上面 registerFont 的第一個參數完全一致
    normal_style = ParagraphStyle('Normal', fontName='ChineseFont', fontSize=12, leading=18)
    title_style = ParagraphStyle('Title', fontName='ChineseFont', fontSize=18, leading=22, alignment=1)
    
    elements = []
    elements.append(Paragraph("臺北市立復興高級中學", title_style))
    elements.append(Paragraph("114學年度選填志願確認同意書", title_style))
    elements.append(Spacer(1, 30))
    
    declaration = f"學生 {student_name} (學號: {student_id}) 於 {submit_time} 完成選填，所選類組為：{choice_text}。"
    elements.append(Paragraph(declaration, normal_style))
    elements.append(Spacer(1, 60))
    
    # --- 3. 修正表格內的字型 ---
    data = [["學生簽名", "家長簽名", "導師簽名"], [" ", " ", " "]]
    sig_table = Table(data, colWidths=[160, 160, 160], rowHeights=[30, 80])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont'), # 整個表格都要指定中文字型
        ('LINEBELOW', (0, 1), (0, 1), 1, colors.black),
        ('LINEBELOW', (1, 1), (1, 1), 1, colors.black),
        ('LINEBELOW', (2, 1), (2, 1), 1, colors.black),
    ]))
    elements.append(sig_table)
    
    doc.build(elements)
    return buffer.getvalue()

def send_confirmation_email(recipient, student_name, student_id, choice_text, submit_time, pdf_bytes):
    # ... 寄信部分保持不變，但確保 recipient 是有效字串 ...
    if not recipient or recipient in ["undefined", "null", "None"]:
        print("ERROR: 收件人 email 無效", flush=True)
        return False
    
    # (其餘 Brevo API 代碼)
    api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("GMAIL_USER")
    
    try:
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        payload = {
            "sender": {"email": sender_email, "name": "選填系統"},
            "to": [{"email": recipient}],
            "subject": f"【確認信】{student_name} 的選填結果",
            "textContent": f"你好 {student_name}，你的志願已送出。",
            "attachment": [{"name": "確認書.pdf", "content": pdf_base64}]
        }
        headers = {"api-key": api_key, "content-type": "application/json"}
        response = requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
        return response.status_code == 201
    except Exception as e:
        print(f"❌ 寄信失敗: {e}", flush=True)
        return False
        return False
