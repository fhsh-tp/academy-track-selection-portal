import asyncio
import os
import sys
from datetime import datetime
from backend.database import get_db, release_db
from backend.mailer import send_confirmation_email
import psycopg2.extras

# 確保環境變數讀取正常
DEADLINE_STR = os.environ.get("DEADLINE_DATE")

async def send_reminders():
    print("\n" + "="*50)
    print(f"🕒 [LOG] 自動提醒任務啟動時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 時間邏輯檢查
    try:
        deadline_dt = datetime.strptime(DEADLINE_STR, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print(f"❌ [ERROR] DEADLINE_DATE 格式錯誤: {DEADLINE_STR}")
        return

    now = datetime.now()
    # 使用 total_seconds 換算天數，避免被秒數進位影響判斷
    diff = deadline_dt - now
    days_left = diff.days 

    print(f"📅 [LOG] 截止日期設定: {DEADLINE_STR}")
    print(f"⏳ [LOG] 距離截止還有: {days_left} 天 (精確差值: {diff})")

    # 💡 Debug 技巧：如果你現在要測試，可以暫時把這裡改成 <= 3
    if days_left != 3:
        print(f"🛑 [LOG] 尚未到達 3 天提醒門檻（目前剩 {days_left} 天），任務結束。")
        return

    print("🚀 [LOG] 條件達成！開始與資料庫連線...")
    
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # ⚠️ 這裡最重要：確保 Table 名稱是 users 而不是 students
        print("🔍 [LOG] 正在查詢尚未選填且有 Email 的學生清單...")
        cur.execute('''
            SELECT u.student_id, u.name, u.email, u.student_class_num
            FROM users u 
            LEFT JOIN selections s ON u.student_id = s.student_id 
            WHERE s.choice IS NULL 
              AND u.role = 'student' 
              AND u.email IS NOT NULL
              AND u.email != ''
        ''')
        unsubmitted_users = cur.fetchall()
        cur.close()

        print(f"📊 [LOG] 查詢完成，找到 {len(unsubmitted_users)} 位未填寫學生。")

        if not unsubmitted_users:
            print("✅ [LOG] 沒有需要提醒的對象。")
            return

        # 2. 逐一寄信並記錄狀態
        for i, user in enumerate(unsubmitted_users, 1):
            print(f"📧 [({i}/{len(unsubmitted_users)})] 嘗試寄信至: {user['email']} ({user['name']})")
            
            try:
                # 參數必須與你的 mailer.py 完全對齊
                success = send_confirmation_email(
                    recipient=user['email'],
                    student_name=user['name'],
                    student_id=user['student_id'],
                    student_class_num=user['student_class_num'] or "未設定",
                    choice_text="系統提醒：您尚未完成選填",
                    submit_time="---",
                    pdf_bytes=b"" # 提醒信不附帶 PDF 內容
                )
                
                if success:
                    print(f"   ✔️ [SUCCESS] {user['name']} 寄送成功")
                else:
                    print(f"   ⚠️ [FAILED] {user['name']} 寄送失敗 (API 可能拒絕或 Key 錯誤)")
            except Exception as mail_err:
                print(f"   ❌ [EXCEPTION] 寄信過程出錯: {mail_err}")
            
            # 避免被 API 判定為惡意頻繁寄信
            await asyncio.sleep(1.5)

        print(f"✨ [LOG] 所有提醒任務執行完畢。")

    except Exception as e:
        print(f"💥 [CRITICAL] 資料庫或連線發生重大錯誤: {e}")
    finally:
        if conn:
            release_db(conn)
            print("🔌 [LOG] 資料庫連線已釋放")
    print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(send_reminders())