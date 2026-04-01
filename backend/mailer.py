import requests
import os
import base64
import io
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from datetime import datetime, timedelta

# --- 1. 字型註冊 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
ROOT_DIR = os.path.dirname(BASE_DIR)
FONT_PATH = os.path.join(ROOT_DIR, "frontend", "TW-Kai-98_1.ttf")
FONT_EXTB = os.path.join(ROOT_DIR, "frontend", "TW-Kai-Ext-B-98_1.ttf")

def register_fonts():
    try:
        if os.path.exists(FONT_PATH):
            pdfmetrics.registerFont(TTFont('ChineseFont', FONT_PATH))
            pdfmetrics.registerFont(TTFont('ChineseFont_EXTB', FONT_EXTB))
            print(f"✅ 字型註冊成功: {FONT_PATH}與{FONT_EXTB}", flush=True)
        else:
            print(f"❌ 找不到字型檔: {FONT_PATH}或{FONT_EXTB}", flush=True)
    except Exception as e:
        print(f"❌ 字型註冊失敗: {e}", flush=True)

register_fonts()

# --- 2. PDF 生成函式 ---
def generate_formal_pdf(student_name, student_id, student_class_num, choice_num, submit_time):
    display_submit_time = submit_time
    try:
        # 解析前端傳來的 ISO 格式 (例如 2026-04-01T11:54:53.715Z)
        # 我們取前 19 位字元 "2026-04-01T11:54:53"
        utc_time = datetime.strptime(submit_time[:19], "%Y-%m-%dT%H:%M:%S")
        
        # 強制加上 8 小時轉為台灣時間
        tw_time = utc_time + timedelta(hours=8)
        display_submit_time = tw_time.strftime("%Y/%m/%d %H:%M:%S")
    except Exception as e:
        print(f"⚠️ 時間轉換失敗: {e}")
        display_submit_time = submit_time # 萬一失敗才用原樣

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=30)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', fontName='ChineseFont', fontSize=20, leading=24, alignment=1, spaceAfter=20)
    note_style = ParagraphStyle('Note', fontName='ChineseFont', fontSize=11, leading=16)
    
    # --- 新增：自動偵測並切換字型 ---
    def get_styled_text(text, base_font="ChineseFont", ext_font="ChineseFont_EXTB"):
        """如果字元編碼大於 0xFFFF (如 𦱀)，則切換至擴展字型"""
        styled_text = ""
        for char in text:
            if ord(char) > 0xFFFF:
                styled_text += f'<font name="{ext_font}">{char}</font>'
            else:
                styled_text += char
        return styled_text

    elements = []
    elements.append(Paragraph("臺北市立復興高級中學高一升高二普通班學生選擇班群表", title_style))
    
    # 將姓名轉換為支援 HTML 標籤的 Paragraph 物件
    styled_name = get_styled_text(student_name)
    name_paragraph = Paragraph(f"姓名：{styled_name}", note_style)
    
    # 這裡將原本的字串 f"姓名：{student_name}" 替換為 name_paragraph 物件
    info_data = [[f"班級座號：{student_class_num}", f"學號：{student_id}", name_paragraph]]
    info_table = Table(info_data, colWidths=[6.5*cm, 5*cm, 6*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (1, 0), 'ChineseFont'), # 前兩格維持原樣
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), # 確保 Paragraph 在儲存格內垂直居中
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 15))

    # --- 以下邏輯維持不變 ---
    v1, v2, v3, v4 = "", "", "", ""
    if choice_num == 1: v1 = "V"
    elif choice_num == 2: v2 = "V"
    elif choice_num == 3: v3 = "V"
    elif choice_num == 4: v4 = "V"

    print_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    choice_table_data = [
        ["班群","文法商(數A課程路徑)", "文法商(數B課程路徑)", "理工資班群", "生醫農班群"],
        ["勾選", v1, v2, v3, v4],
        [f"勾選時間：{display_submit_time}", "", "", f"列印時間：{print_time}", ""]
    ]
    
    w = 17.5 * cm / 5
    choice_table = Table(choice_table_data, colWidths=[w, w, w, w, w], rowHeights=[1.2*cm, 1.5*cm, 0.8*cm])
    choice_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont'),
        ('GRID', (0, 0), (-1, 1), 1, colors.black),
        ('BOX', (0, 2), (-1, 2), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('SPAN', (0, 2), (2, 2)),  
        ('SPAN', (3, 2), (4, 2)),  
        ('FONTSIZE', (0, 2), (-1, 2), 9), 
        ('FONTSIZE', (1, 1), (4, 1), 22), 
    ]))
    elements.append(choice_table)
    elements.append(Spacer(1, 35))

    sig_data = [
        [Paragraph("學生簽名：____________________", note_style), Paragraph("導師簽名：____________________", note_style)],
        [Spacer(1, 35), Spacer(1, 35)],
        [Paragraph("家長簽名：____________________", note_style), Paragraph("◎請於5月4日前完成簽名、交給學藝股長彙整。", note_style)],
        [Spacer(1, 35), Spacer(1, 35)],
        [Paragraph("家長電話：____________________", note_style), Paragraph("◎若要更改，請於期限內上網修正，重新列印簽名", note_style)]
    ]
    
    sig_table = Table(sig_data, colWidths=[9*cm, 9*cm])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(sig_table)

    doc.build(elements)
    return buffer.getvalue()

# --- 3. 寄信函式 (含 Debug 邏輯) ---
def send_confirmation_email(recipient, student_name, student_id, student_class_num, choice_text, submit_time, pdf_bytes):
    api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("GMAIL_USER")

    if not api_key or not sender_email:
        print("❌ [MAILER] 錯誤：缺少環境變數", flush=True)
        return False

    try:
        # 判斷是否為「提醒信」模式（當 pdf_bytes 為空時）
        is_reminder = not (pdf_bytes and len(pdf_bytes) > 0)

        if is_reminder:
            # --- 1. 提醒信：標題與格式 ---
            subject = "【重要通知】您的類組尚未選填"
            email_content = (
                f"你好 {student_name}\n"
                f"您的類組尚未選填。\n"
                f"班級座號：{student_class_num}\n"
                f"學號：{student_id}\n"
                f"選填結果：尚未完成填寫。"
            )
        else:
            # --- 2. 確認信：標題與格式 ---
            subject = f"【重要確認信】{student_name} 的選填結果"
            email_content = (
                f"你好 {student_name}，你的志願已送出。\n\n"
                f"班級座號：{student_class_num}\n"
                f"學號：{student_id}\n"
                f"選填結果：{choice_text}\n"
                f"提交時間：{display_submit_time}\n\n"
                "--------------------------------------------------\n"
                "請列印附件「選擇班群表」，經學生、家長與導師簽名，5月4日(一)前交給學藝股長。\n"
                "【家中無印表機者歡迎至註冊組借電腦列印】"
            )

        payload = {
            "sender": {"email": sender_email, "name": "復興高中選填系統"},
            "to": [{"email": recipient}],
            "subject": subject,
            "textContent": email_content
        }
        
        # 只有在「非提醒信」（即確認信）模式下，才掛載 PDF 附件
        if not is_reminder:
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            payload["attachment"] = [{
                "name": f"{student_id}_確認書.pdf", 
                "content": pdf_base64
            }]
        
        headers = {
            "api-key": api_key, 
            "content-type": "application/json",
            "accept": "application/json"
        }
        
        response = requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
        
        if response.status_code not in [201, 202]:
            print(f"❌ [MAILER] API 失敗！對象: {student_name}, 狀態碼: {response.status_code}", flush=True)
            print(f"❌ [MAILER] 錯誤詳情: {response.text}", flush=True)
            return False
            
        return True
            
    except Exception as e:
        print(f"❌ [MAILER] 執行異常: {str(e)}", flush=True)
        return False