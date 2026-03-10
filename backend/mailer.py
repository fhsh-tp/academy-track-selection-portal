import requests
import os
import base64
import io
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# 確保所有函數都有詳細的錯誤輸出
def generate_formal_pdf(student_name, student_id, choice_text, submit_time):
    print("DEBUG: 開始生成 PDF", flush=True)
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        styles = getSampleStyleSheet()
        
        elements = []
        elements.append(Paragraph("臺北市立復興高級中學", styles['Heading1']))
        elements.append(Paragraph("114學年度選填志願確認同意書", styles['Title']))
        elements.append(Spacer(1, 50))
        
        sig_data = [["學生簽名:_________", "家長/監護人簽名:_________", "導師簽名:_________"]]
        sig_table = Table(sig_data, colWidths=[165, 165, 165])
        elements.append(sig_table)
        
        doc.build(elements)
        print("DEBUG: PDF 生成成功", flush=True)
        return buffer.getvalue()
    except Exception as e:
        print(f"DEBUG: PDF 生成失敗: {e}", flush=True)
        return None

def send_confirmation_email(recipient, student_name, student_id, choice_text, submit_time, pdf_bytes):
    print(f"DEBUG: 準備發送郵件給 {recipient}", flush=True)
    api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("GMAIL_USER")
    
    if not api_key or not sender_email:
        print("ERROR: API Key 或 Email 設定遺失！", flush=True)
        return False
        
    try:
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        payload = {
            "sender": {"email": sender_email, "name": "選填系統"},
            "to": [{"email": recipient}],
            "subject": f"【測試】{student_name} 的選填確認",
            "textContent": "測試郵件內容。",
            "attachment": [{"name": "確認書.pdf", "content": pdf_base64}]
        }
        headers = {"api-key": api_key, "content-type": "application/json"}
        
        print("DEBUG: 正在呼叫 Brevo API...", flush=True)
        response = requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
        
        if response.status_code == 201:
            print("✅ 郵件成功發送至 Brevo (Status 201)", flush=True)
            return True
        else:
            print(f"❌ Brevo 拒絕了請求: {response.text}", flush=True)
            return False
    except Exception as e:
        print(f"❌ 寄信程式崩潰: {e}", flush=True)
        return False