import requests
import os
import base64
import io
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from datetime import datetime

# --- 1. 修正字型路徑與註冊名稱 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
ROOT_DIR = os.path.dirname(BASE_DIR)
FONT_PATH = os.path.join(ROOT_DIR, "frontend", "NotoSansTC-Regular.ttf")

def register_fonts():
    try:
        pdfmetrics.registerFont(TTFont('ChineseFont', FONT_PATH))
        print(f"✅ 字型註冊成功: {FONT_PATH}", flush=True)
    except Exception as e:
        print(f"❌ 字型註冊失敗: {e}", flush=True)

register_fonts()

def generate_formal_pdf(student_name, student_id, studen_class_num, choice_num, submit_time):
    # 確保參數包含 studen_class_num 並顯示在資訊列
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=30)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', fontName='ChineseFont', fontSize=20, leading=24, alignment=1, spaceAfter=20)
    info_style = ParagraphStyle('Info', fontName='ChineseFont', fontSize=12)
    note_style = ParagraphStyle('Note', fontName='ChineseFont', fontSize=11, leading=16)
    
    elements = []

    # 1. 標題
    elements.append(Paragraph("臺北市立復興高級中學高一升高二普通班學生選擇班群表", title_style))
    
    # 2. 學生資訊列 (包含班級座號)
    info_data = [[f"班級座號：{studen_class_num}", f"學號：{student_id}", f"姓名：{student_name}"]]
    info_table = Table(info_data, colWidths=[6*cm, 5*cm, 6*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 15))

    # 3. 選填表格 (自動畫勾)
    v1, v2, v3, v4 = "", "", "", ""
    if choice_num == 1: v1 = "V"
    elif choice_num == 2: v2 = "V"
    elif choice_num == 3: v3 = "V"
    elif choice_num == 4: v4 = "V"

    choice_table_data = [
        ["班群", "文法商(數A課程路徑)", "文法商(數B課程路徑)", "理工資班群", "生醫農班群"],
        ["勾選", v1, v2, v3, v4],
        [f"勾選時間：{submit_time}", "", "", "", f"列印時間：{datetime.now().strftime('%Y/%m/%d %H:%M:%S')}"]
    ]
    
    w = 17.5 * cm / 5
    choice_table = Table(choice_table_data, colWidths=[w, w, w, w, w], rowHeights=[1.2*cm, 1.5*cm, 0.8*cm])
    
    choice_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont'),
        ('GRID', (0, 0), (-1, 1), 1, colors.black),
        ('BOX', (0, 2), (-1, 2), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('SPAN', (0, 2), (3, 2)), 
        ('FONTSIZE', (1, 1), (4, 1), 22), 
    ]))
    elements.append(choice_table)
    
    elements.append(Spacer(1, 30))

    # 4. 簽名區域與右側注意事項
    sig_data = [
        [Paragraph("學生簽名：____________________", note_style), Paragraph("導師簽名：____________________", note_style)],
        [Spacer(1, 35), Spacer(1, 35)],
        [Paragraph("家長簽名：____________________", note_style), Paragraph("◎請於5月5日前完成簽名、交給學藝股長彙整。", note_style)],
        [Spacer(1, 35), Spacer(1, 35)],
        [Paragraph("家長電話：____________________", note_style), Paragraph("◎若更改選擇，請於期限內上網修正，重新列印簽名", note_style)]
    ]
    
    sig_table = Table(sig_data, colWidths=[9*cm, 9*cm])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(sig_table)

    doc.build(elements)
    return buffer.getvalue()

def send_confirmation_email(recipient, student_name, student_id, studen_class_num, choice_text, submit_time, pdf_bytes):
    # 確保參數包含 studen_class_num 並獲取環境變數
    api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("GMAIL_USER")

    if not api_key or not sender_email:
        print("❌ 錯誤：找不到 BREVO_API_KEY 或 GMAIL_USER 環境變數", flush=True)
        return False

    try:
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        email_content = (
            f"你好 {student_name}，你的志願已送出。\n\n"
            f"班級座號：{studen_class_num}\n"
            f"學號：{student_id}\n"
            f"選填結果：{choice_text}\n"
            f"提交時間：{submit_time}\n\n"
            "--------------------------------------------------\n"
            "⚠️ 重要提醒：\n"
            "【不要】點擊郵件的「Unsubscribe (取消訂閱)」。\n"
            "若誤按取消訂閱，系統將無法再寄送任何選填確認信或重要通知給你。\n"
            "--------------------------------------------------\n"
            "請查看附件中的 PDF 確認書。"
        )

        payload = {
            "sender": {"email": sender_email, "name": "復興高中選填系統"},
            "to": [{"email": recipient}],
            "subject": f"【重要確認信】{student_name} 的選填結果",
            "textContent": email_content,
            "attachment": [{"name": f"{student_id}_確認書.pdf", "content": pdf_base64}]
        }
        
        headers = {"api-key": api_key, "content-type": "application/json"}
        response = requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
        
        if response.status_code == 201:
            print(f"✅ 郵件成功寄出至: {recipient}", flush=True)
            return True
        else:
            print(f"❌ Brevo 報錯: {response.text}", flush=True)
            return False
            
    except Exception as e:
        print(f"❌ 寄信發生異常: {e}", flush=True)
        return False