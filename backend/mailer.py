import resend
import os
import io
import base64
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 自動讀取環境變數
resend.api_key = os.getenv("RESEND_API_KEY")

# 註冊中文字體 (確保路徑正確)
font_path = os.path.join(os.getcwd(), "frontend", "NotoSansTC-Regular.ttf")
if os.path.exists(font_path):
    pdfmetrics.registerFont(TTFont('NotoSans', font_path))
else:
    print(f"⚠️ 找不到字體檔: {font_path}, PDF 中文可能顯示異常")

def generate_student_pdf(student_name, student_id, choice_name, submit_time):
    """動態產生 PDF 並回傳位元組內容"""
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    
    # 嘗試使用中文字體
    try:
        p.setFont("NotoSans", 16)
    except:
        p.setFont("Helvetica", 16)

    # --- 繪製 PDF 內容 ---
    p.drawString(100, 800, "114 學年度高一升高二選填類組確認書")
    p.line(100, 790, 500, 790)
    
    p.setFontSize(10)
    p.drawRightString(500, 795, f"系統收件時間：{submit_time}")
    
    p.setFontSize(12)
    p.drawString(100, 750, f"學生姓名：{student_name}")
    p.drawString(100, 730, f"學生學號：{student_id}")
    p.drawString(100, 710, f"選填類組：{choice_name}")
    
    p.drawString(100, 650, "--------------------------------------------------")
    p.drawString(100, 630, "簽署專欄：")
    p.setFontSize(11)
    p.drawString(100, 610, "本人已知悉子女之選填結果，並予以同意。")
    
    # --- 修正簽名欄位座標 (避免重疊) ---
    p.drawString(100, 560, "學生簽名：____________________  日期：2026 / ___ / ___")
    p.drawString(100, 530, "家長簽名：____________________  日期：2026 / ___ / ___")
    p.drawString(100, 500, "家長電話：____________________")
    p.drawString(100, 450, "導師簽名：____________________  日期：2026 / ___ / ___")
    
    p.setFontSize(9)
    p.setFillAlpha(0.5) # 設定稍微透明，像是浮水印
    p.drawString(100, 100, f"本文件由選填系統自動產生，防偽校驗碼：{base64.b64encode(student_id.encode()).decode()[:10]}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer.read()

def send_confirmation_email(recipient: str, student_name: str, student_id: str, choice_name: str, submit_time: str):
    """合併後的單一發信函數"""
    if not resend.api_key:
        print("⚠️ 未設定 RESEND_API_KEY, 無法寄信")
        return

    try:
        # 1. 生成 PDF
        pdf_content = generate_student_pdf(student_name, student_id, choice_name, submit_time)
        encoded_pdf = base64.b64encode(pdf_content).decode()

        # 2. 準備郵件與附件
        # 確保 attachments 是一個乾淨的 list，沒有 Ellipsis (...)
        params = {
            "from": "onboarding@resend.dev", # 尚未驗證網域前通常用這個
            "to": recipient,
            "subject": f"【確認書】{student_name} 選組結果 (系統紀錄於 {submit_time})",
            "attachments": [
                {
                    "content": encoded_pdf,
                    "filename": f"{student_id}_{student_name}_同意書.pdf",
                }
            ],
            "html": f"""
                <div style="font-family: sans-serif; line-height: 1.6;">
                    <h3>{student_name} 同學您好：</h3>
                    <p>您的選填已於 <strong>{submit_time}</strong> 完成。</p>
                    <p>選擇類組：<span style="color: #e74c3c; font-weight: bold;">{choice_name}</span></p>
                    <br>
                    <p>請下載附件中的專屬 PDF 同意書，列印後由本人及家長簽名，並於指定日期前繳回教務處。</p>
                    <p style="color: #666; font-size: 0.8em;">(本郵件由系統自動發出，請勿直接回覆)</p>
                </div>
            """
        }
        
        resend.Emails.send(params)
        print(f"✅ 成功為 {student_name} 寄出 PDF 郵件")
    except Exception as e:
        print(f"❌ 郵件發送過程出錯: {e}")