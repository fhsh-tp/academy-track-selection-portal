import requests
import os
import base64
import io
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

def generate_formal_pdf(student_name, student_id, choice_text, submit_time):
    print("DEBUG: 開始生成正式確認書 PDF (含底線簽名欄)", flush=True)
    try:
        buffer = io.BytesIO()
        # 設定頁邊距
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        styles = getSampleStyleSheet()
        
        # 定義一個正式的樣式
        formal_style = ParagraphStyle(
            'Formal', parent=styles['Normal'], fontSize=12, leading=18, spaceAfter=10
        )
        
        elements = []
        
        # 1. 標題與學校名稱
        elements.append(Paragraph("臺北市立復興高級中學", styles['Title']))
        elements.append(Paragraph("114學年度選填志願確認同意書", styles['Heading2']))
        elements.append(Spacer(1, 30))
        
        # 2. 學生選填資訊聲明
        declaration = f"""
        茲證明學生 <b>{student_name}</b> (學號: {student_id}) 於 <b>{submit_time}</b> 
        完成選填志願申請，所選類組為：<b>{choice_text}</b>。
        <br/><br/>
        本人及家長已詳閱選填須知，確認上述志願為學生意願，並同意由校方據此辦理後續分發事宜。
        """
        elements.append(Paragraph(declaration, formal_style))
        elements.append(Spacer(1, 60)) # 留白讓簽名欄往下移
        
        # 3. 簽名欄位表格 (含底線設計)
        # 資料結構：第一行是標題，第二行是預留簽名空間
        data = [
            ["學生簽名", "家長/監護人簽名", "導師簽名"],
            [" ", " ", " "] # 這一行將被加上底線
        ]
        
        # 設定欄寬 (160 * 3 = 480，接近 A4 可用寬度)
        sig_table = Table(data, colWidths=[160, 160, 160], rowHeights=[30, 50])
        
        # 定義表格樣式
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1, -1), 'LEFT'),      # 文字靠左
            ('VALIGN', (0,0), (-1, -1), 'BOTTOM'),   # 文字貼近底部 (配合底線)
            ('FONTNAME', (0,0), (-1, 0), 'Helvetica-Bold'), # 標題粗體
            ('FONTSIZE', (0,0), (-1, -1), 12),
            
            # 【關鍵修改】：只在第二行 (簽名空間) 的下方加上底線
            # 參數說明: (起始欄, 起始列), (結束欄, 結束列), 線寬, 顏色
            ('LINEBELOW', (0, 1), (0, 1), 1, colors.black), # 學生簽名底線
            ('LINEBELOW', (1, 1), (1, 1), 1, colors.black), # 家長簽名底線
            ('LINEBELOW', (2, 1), (2, 1), 1, colors.black), # 導師簽名底線
            
            # 調整間距，讓底線看起來更自然
            ('BOTTOMPADDING', (0, 1), (-1, 1), 5), 
        ]))
        
        elements.append(sig_table)
        elements.append(Spacer(1, 40))
        
        # 4. 日期欄位
        elements.append(Paragraph("日期：_______年______月______日", formal_style))
        elements.append(Spacer(1, 20))
        
        # 5. 提示文字
        elements.append(Paragraph("※ 請務必列印本確認書並經各方簽名後，繳交回教務處。", styles['Italic']))
        
        doc.build(elements)
        print("DEBUG: 正式 PDF 生成成功 (含底線)", flush=True)
        return buffer.getvalue()
    except Exception as e:
        print(f"DEBUG: PDF 生成失敗: {e}", flush=True)
        return None

def send_confirmation_email(recipient, student_name, student_id, choice_text, submit_time, pdf_bytes):
    api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("GMAIL_USER")
    
    try:
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # --- 這裡客製化郵件內容 ---
        email_content = f"""
        親愛的同學 {student_name} 您好：

        您的選填志願申請已送出，詳細資訊如下：
        - 學號: {student_id}
        - 選擇類組: {choice_text}
        - 提交時間: {submit_time}

        隨信附件為您的「志願選填確認同意書」，請下載並列印後，由學生、家長與導師完成簽名。

        復興高中選填系統
        """
        
        payload = {
            "sender": {"email": sender_email, "name": "復興高中選填系統"},
            "to": [{"email": recipient}],
            "subject": f"【確認信】{student_name} - 選填結果確認",
            "textContent": email_content,
            "attachment": [{"name": "志願確認同意書.pdf", "content": pdf_base64}]
        }
        
        headers = {"api-key": api_key, "content-type": "application/json"}
        response = requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
        
        if response.status_code == 201:
            return True
        else:
            print(f"❌ Brevo 錯誤: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 寄信程式崩潰: {e}")
        return False