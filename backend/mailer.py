import os
import io
import aiosmtplib
from email.message import EmailMessage
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from datetime import datetime, timedelta, timezone

from backend.utils import email_sender

# --- 1. 字型註冊 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
FONT_PATH = os.path.join(BASE_DIR, "static", "TW-Kai-98_1.ttf")
FONT_EXTB = os.path.join(BASE_DIR, "static", "TW-Kai-Ext-B-98_1.ttf")

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
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=30)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', fontName='ChineseFont', fontSize=20, leading=24, alignment=1, spaceAfter=20)
    note_style = ParagraphStyle('Note', fontName='ChineseFont', fontSize=11, leading=16)

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

    styled_name = get_styled_text(student_name)
    name_paragraph = Paragraph(f"姓名：{styled_name}", note_style)

    info_data = [[f"班級座號：{student_class_num}", f"學號：{student_id}", name_paragraph]]
    info_table = Table(info_data, colWidths=[6.5*cm, 5*cm, 6*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (1, 0), 'ChineseFont'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 15))

    v1, v2, v3, v4 = "", "", "", ""
    if choice_num == 1: v1 = "V"
    elif choice_num == 2: v2 = "V"
    elif choice_num == 3: v3 = "V"
    elif choice_num == 4: v4 = "V"

    print_time = datetime.now(timezone(timedelta(hours=8))).strftime('%Y/%m/%d %H:%M:%S')
    choice_table_data = [
        ["班群","文法商(數A課程路徑)", "文法商(數B課程路徑)", "理工資班群", "生醫農班群"],
        ["勾選", v1, v2, v3, v4],
        [f"勾選時間：{print_time}", "", "", f"列印時間：{print_time}", ""]
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

# --- 3. 寄信函式 (aiosmtplib + Google Workspace SMTP Relay) ---
async def send_confirmation_email(recipient, student_name, student_id, student_class_num, choice_text, submit_time, pdf_bytes):
    smtp_host = os.getenv("SMTP_HOST", "smtp-relay.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not smtp_user or not smtp_password:
        print("❌ [MAILER] 錯誤：缺少 SMTP_USER 或 SMTP_PASSWORD 環境變數", flush=True)
        return False

    try:
        try:
            dt_utc = datetime.strptime(submit_time[:19], "%Y-%m-%dT%H:%M:%S")
            clean_time = (dt_utc + timedelta(hours=8)).strftime('%Y/%m/%d %H:%M:%S')
        except Exception:
            clean_time = submit_time

        is_reminder = not (pdf_bytes and len(pdf_bytes) > 0)

        if is_reminder:
            subject = "【重要通知】您的類組尚未選填"
            text_content = (
                f"你好 {student_name}\n"
                f"您的類組尚未選填。\n"
                f"班級座號：{student_class_num}\n"
                f"學號：{student_id}\n"
                f"選填結果：尚未完成填寫。"
            )
        else:
            subject = f"【重要確認信】{student_name} 的選填結果"
            text_content = (
                f"你好 {student_name}，你的志願已送出。\n\n"
                f"班級座號：{student_class_num}\n"
                f"學號：{student_id}\n"
                f"選填結果：{choice_text}\n"
                f"提交時間：{clean_time}\n\n"
                "--------------------------------------------------\n"
                "請列印附件「選擇班群表」，經學生、家長與導師簽名，5月4日(一)前交給學藝股長。\n"
                "【家中無印表機者歡迎至註冊組借電腦列印】"
            )
        
        html_content = text_content.replace("\n", "<br>")

        if is_reminder:
            # 寄送未選填提醒信 (無附件)
            success = await email_sender.send_email(
                to=recipient,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            return success
        else:
            # 寄送選填確認信 (有附件，直接傳入檔名與 byte 資料的 Tuple)
            success = await email_sender.send_email(
                to=recipient,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                attachments=[(f"{student_id}_確認書.pdf", pdf_bytes)]
            )
            return success

    except Exception as e:
        print(f"❌ [MAILER] 執行異常: {str(e)}", flush=True)
        return False
