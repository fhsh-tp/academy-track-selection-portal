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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- 1. 註冊字型 (確保路徑對應你的資料夾) ---
font_path = os.path.join(BASE_DIR, "fonts", "NotoSansTC-Regular.ttf")
pdfmetrics.registerFont(TTFont('ChineseFont', font_path))


def generate_formal_pdf(student_name, student_id, choice_text, submit_time):
    """
    生成專業且美觀的同意書 PDF。
    """
    buffer = io.BytesIO()
    
    # 使用 SimpleDocTemplate 代替 canvas，方便進行佈局
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=50, leftMargin=50,
        topMargin=50, bottomMargin=50
    )
    
    # 設定樣式集
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='ChineseTitle', fontName='ChineseFont', fontSize=24, leading=28, alignment=1, spaceAfter=20))
    styles.add(ParagraphStyle(name='ChineseHeading', fontName='ChineseFont', fontSize=14, leading=18, spaceAfter=10, textColor=colors.navy))
    styles.add(ParagraphStyle(name='ChineseNormal', fontName='ChineseFont', fontSize=11, leading=16))
    
    # --- PDF 內容構建 ---
    elements = []
    
    # Header: 學校 Logo 和標題
    # 如果有 Logo 圖片可以加在這裡
    # elements.append(Image("path/to/logo.png", width=50, height=50))
    elements.append(Paragraph(f"XXX 臺北市立 XXX 高級中學", styles['ChineseHeading']))
    elements.append(Paragraph("114學年度高中部高二選填類組/志願確認同意書", styles['ChineseTitle']))
    
    # 加入裝飾用的粗線
    line_data = [[""]]
    line_table = Table(line_data, colWidths=[495], rowHeights=[2])
    line_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.navy),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(line_table)
    elements.append(Spacer(1, 25))
    
    # 第一區塊：基本資料
    elements.append(Paragraph("一、 學生基本資料", styles['ChineseHeading']))
    
    data = [
        ['學號', f"{student_id}"],
        ['姓名', f"{student_name}"],
    ]
    
    # 建立正式的表格 (使用 navy 藍框)
    table = Table(data, colWidths=[80, 400])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.navy),
        ('BACKGROUND', (0, 0), (0, -1), colors.aliceblue), # 左側背景色
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    # 第二區塊：選填結果
    elements.append(Paragraph("二、 選填結果確認", styles['ChineseHeading']))
    
    choice_data = [
        ['您已完成 114學年度類組選填', ''],
        ['確認選填結果', f"{choice_text}"],
        ['選填送出時間', f"{submit_time}"],
    ]
    
    choice_table = Table(choice_data, colWidths=[200, 280])
    choice_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('SPAN', (0, 0), (1, 0)), # 合併第一行
        ('GRID', (0, 0), (-1, -1), 0.5, colors.navy),
        ('BACKGROUND', (0, 0), (0, -1), colors.aliceblue),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(choice_table)
    elements.append(Spacer(1, 20))
    
    # 聲明文字
    statement = """
    本人(學生)已充分了解本校114學年度類組選填作業規定,並已與家長/監護人進行充分討論，
    確認上述選填結果無誤。本人承諾將準時於規定期限內完成後續相關手續，並同意以此作為正式選填依據。
    """
    elements.append(Paragraph(statement, styles['ChineseNormal']))
    elements.append(Spacer(1, 40))
    
    # 第三區塊：簽名區 (水平整齊對齊)
    elements.append(Paragraph("三、 簽名確認", styles['ChineseHeading']))
    
    sign_data = [
        ['學生簽名', '家長/監護人簽名', '導師簽名'],
        ['(請親簽)', '(請親簽)', '(請親簽)'],
        ['日期: 年 月 日', '日期: 年 月 日', '日期: 年 月 日']
    ]
    
    # 設定簽名表格 (不使用框線，營造正式感)
    sign_table = Table(sign_data, colWidths=[165, 165, 165], rowHeights=[40, 20, 20])
    sign_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'), # 內容置頂
    ]))
    elements.append(sign_table)
    
    # 開始構建 PDF
    doc.build(elements)
    
    # 取得 PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def send_confirmation_email(recipient, student_name, student_id, choice_text, submit_time, pdf_bytes):
    """
    修改此函式，使其只處理郵件發送，不處理 PDF 生成。
    """
    print(f"DEBUG: 準備觸發寄信流程，目標: {recipient}...", flush=True)
    
    api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("GMAIL_USER")
    
    if not api_key:
        print("🚨 致命錯誤: BREVO_API_KEY 為空值 (None)！", flush=True)
        return False
    elif len(api_key) < 20:
        print(f"🚨 警告: API Key 長度異常，目前長度: {len(api_key)}。請檢查是否貼錯。", flush=True)
        return False
    
    if not sender_email:
        print("ERROR: GMAIL_USER 設定遺失！請檢查 Render 環境變數。", flush=True)
        return False

    try:
        # 直接將記憶體中的 bytes 轉為 base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "api-key": api_key,
            "content-type": "application/json"
        }
        
        payload = {
            "sender": {"email": sender_email, "name": "選填系統"},
            "to": [{"email": recipient}],
            "subject": f"【正式選填確認】{student_name} 同學 - A001選填單",
            "textContent": f"{student_name} 同學您好，您已於 {submit_time} 完成高二志願類組選填 ({choice_text})。\n請下載並親簽附件中的同意書，於規定期限內繳回。",
            "attachment": [
                {
                    "name": f"114_選填類組確認同意書_{student_name}.pdf",
                    "content": pdf_base64
                }
            ]
        }

        print("DEBUG: 正在呼叫 Brevo API...", flush=True)
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            print(f"✅ 成功寄信給 {recipient}!", flush=True)
            return True
        else:
            print(f"❌ 寄信失敗! Code: {response.status_code}, 內容: {response.text}", flush=True)
            return False
            
    except Exception as e:
        print(f"❌ 寄信函式發生例外錯誤: {str(e)}", flush=True)
        return False