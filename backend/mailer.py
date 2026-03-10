import requests
import os
import base64
import io
from datetime import datetime

# 進階 PDF 製作
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# --- 關鍵修正：路徑設定 ---
# 取得目前這個檔案 (mailer.py) 的絕對路徑
current_dir = os.path.dirname(os.path.abspath(__file__))

def generate_formal_pdf(student_name, student_id, choice_text, submit_time):
    # ... (你的 generate_formal_pdf 內容保持不變，直接貼在這裡) ...
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=50, leftMargin=50,
        topMargin=50, bottomMargin=50
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='ChineseTitle', fontName='ChineseFont', fontSize=24, leading=28, alignment=1, spaceAfter=20))
    styles.add(ParagraphStyle(name='ChineseHeading', fontName='ChineseFont', fontSize=14, leading=18, spaceAfter=10, textColor=colors.navy))
    styles.add(ParagraphStyle(name='ChineseNormal', fontName='ChineseFont', fontSize=11, leading=16))
    
    elements = []
    elements.append(Paragraph(f"XXX 臺北市立 XXX 高級中學", styles['ChineseHeading']))
    elements.append(Paragraph("114學年度高中部高二選填類組/志願確認同意書", styles['ChineseTitle']))
    
    line_table = Table([[""]], colWidths=[495], rowHeights=[2])
    line_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.navy)]))
    elements.append(line_table)
    elements.append(Spacer(1, 25))
    
    elements.append(Paragraph("一、 學生基本資料", styles['ChineseHeading']))
    data = [['學號', f"{student_id}"], ['姓名', f"{student_name}"]]
    table = Table(data, colWidths=[80, 400])
    table.setStyle(TableStyle([('FONTNAME', (0, 0), (-1, -1), 'ChineseFont'), ('GRID', (0, 0), (-1, -1), 0.5, colors.navy)]))
    elements.append(table)
    
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("二、 選填結果確認", styles['ChineseHeading']))
    choice_data = [['確認選填結果', f"{choice_text}"], ['選填送出時間', f"{submit_time}"]]
    choice_table = Table(choice_data, colWidths=[200, 280])
    choice_table.setStyle(TableStyle([('FONTNAME', (0, 0), (-1, -1), 'ChineseFont'), ('GRID', (0, 0), (-1, -1), 0.5, colors.navy)]))
    elements.append(choice_table)
    
    doc.build(elements)
    return buffer.getvalue()

def send_confirmation_email(recipient, student_name, student_id, choice_text, submit_time, pdf_bytes):
    # ... (你的 send_confirmation_email 內容保持不變，直接貼在這裡) ...
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
            "subject": f"【選填確認】{student_name}",
            "textContent": f"{student_name} 您好，請查收附件。",
            "attachment": [{"name": "同意書.pdf", "content": pdf_base64}]
        }
        headers = {"api-key": api_key, "content-type": "application/json"}
        response = requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
        return response.status_code == 201
    except Exception as e:
        print(f"ERROR: {e}", flush=True)
        return False