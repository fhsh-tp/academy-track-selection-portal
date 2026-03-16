
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
# 確保指向 frontend/NotoSansTC-Regular.ttf
FONT_PATH = os.path.join(ROOT_DIR, "frontend", "NotoSansTC-Regular.ttf")


# 這裡的名稱 'ChineseFont' 就是之後所有 Style 要用的 fontName
def register_fonts():
    try:
        # 註冊為 'ChineseFont'
        pdfmetrics.registerFont(TTFont('ChineseFont', FONT_PATH))
        print(f"✅ 字型註冊成功: {FONT_PATH}", flush=True)
    except Exception as e:
        print(f"❌ 字型註冊失敗: {e}", flush=True)

register_fonts()

def generate_formal_pdf(student_name, student_id, choice_text, submit_time):
    buffer = io.BytesIO()
    # 設定頁邊距
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=50, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    # 自定義樣式
    title_style = ParagraphStyle('Title', fontName='ChineseFont', fontSize=20, leading=26, alignment=1, spaceAfter=30)
    label_style = ParagraphStyle('Label', fontName='ChineseFont', fontSize=12, leading=18)
    note_style = ParagraphStyle('Note', fontName='ChineseFont', fontSize=11, leading=16)
    
    elements = []

    # 1. 標題
    elements.append(Paragraph("臺北市立復興高級中學", title_style))
    elements.append(Paragraph("114學年度高一升高二學生選擇班群確認表", title_style))
    
    # 2. 學生基本資訊 (無框表格排版)
    info_data = [[f"學號：{student_id}", f"姓名：{student_name}", f"班級座號：(請手寫填寫)"]]
    info_table = Table(info_data, colWidths=[5*cm, 5*cm, 7*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<hr/>", styles['Normal'])) # 分隔線
    elements.append(Spacer(1, 20))

    # 3. 選填結果顯示區
    # 這裡直接用大字體顯示結果，並加框強調
    result_data = [
        ["最終選填結果"],
        [choice_text]
    ]
    result_table = Table(result_data, colWidths=[15*cm], rowHeights=[1*cm, 2*cm])
    result_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont'),
        ('FONTSIZE', (0, 0), (0, 0), 14),
        ('FONTSIZE', (0, 1), (0, 1), 22), # 讓選填結果字體超大
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1.5, colors.black), # 加粗框線
        ('BACKGROUND', (0, 0), (0, 0), colors.whitesmoke), # 標題背景色
    ]))
    elements.append(result_table)
    elements.append(Spacer(1, 10))
    
    # 顯示送出時間
    elements.append(Paragraph(f"系統接收時間：{submit_time}", note_style))
    elements.append(Spacer(1, 40))

    # 4. 簽名區域
    sig_data = [
        [Paragraph("學生簽名:____________________", label_style), Paragraph("導師簽名:____________________", label_style)],
        [Spacer(1, 40), Spacer(1, 40)],
        [Paragraph("家長簽名:____________________", label_style)],
        [Paragraph("家長電話:____________________", label_style)]
    ]
    
    sig_table = Table(sig_data, colWidths=[8.5*cm, 8.5*cm])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(sig_table)
    
    elements.append(Spacer(1, 50))
    
    # 5. 底部說明文字
    footer_notes = [
        "◎ 注意事項：",
        "1. 請於規定時間內(5月4日)前完成簽名，並交回班上的學藝股長彙整。",
        "2. 本表單由系統自動產生，若簽名後欲修改志願，請於截止日前上網修正並重新列印。",
        f"3. 本文件產生於：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    ]
    for note in footer_notes:
        elements.append(Paragraph(note, note_style))

    doc.build(elements)
    return buffer.getvalue()

def send_confirmation_email(recipient, student_name, student_id, choice_text, submit_time, pdf_bytes):
    # --- 關鍵：確保獲取環境變數 ---
    api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("GMAIL_USER")

    if not api_key or not sender_email:
        print("❌ 錯誤：找不到 BREVO_API_KEY 或 GMAIL_USER 環境變數", flush=True)
        return False

    try:
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # 組合郵件內容
        email_content = (
            f"你好 {student_name}，你的志願已送出。\n\n"
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
            "textContent": email_content, # 更新內文
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