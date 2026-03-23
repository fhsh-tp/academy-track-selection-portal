import asyncio
import os
from datetime import datetime
from backend.database import get_db, release_db
from backend.mailer import send_confirmation_email
import psycopg2.extras

# 統一截止日期設定
DEADLINE_STR = os.environ.get("DEADLINE_DATE")

async def send_reminders():
    try:
        deadline_dt = datetime.strptime(DEADLINE_STR, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        deadline_dt = datetime(2026, 5, 4, 23, 59, 59)

    now = datetime.now()
    # 計算天數差距
    diff = deadline_dt - now
    days_left = diff.days

    print(f"⏰ 目前時間: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏳ 距離截止還有: {days_left} 天")

    # 💡 為了測試，你可以先註解掉下面這兩行，確保程式一定會執行
    # if days_left != 3:
    #     print(f"🛑 尚未到達剩餘 3 天的提醒時間。")

    print("🚀 開始執行選填提醒任務...")
    
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # 【修正 1】使用正確的資料表名稱 users 與 selections
        cur.execute('''
            SELECT u.student_id, u.name, u.email, u.student_class_num
            FROM users u 
            LEFT JOIN selections s ON u.student_id = s.student_id 
            WHERE s.choice IS NULL AND u.role = 'student' AND u.email IS NOT NULL
        ''')
        unsubmitted_users = cur.fetchall()
        cur.close()

        if not unsubmitted_users:
            print("✅ 所有學生都已完成填寫，無需寄信。")
            return

        for user in unsubmitted_users:
            print(f"📧 準備寄送提醒給: {user['name']} ({user['email']})")
            
            # 【修正 2】參數必須完整對應 mailer.py 的定義
            # 提醒信不需要 PDF，但函式定義需要，所以傳入空的 bytes 或 None 並修改 mailer 判斷
            success = send_confirmation_email(
                recipient=user['email'],
                student_name=user['name'],
                student_id=user['student_id'],
                student_class_num=user['student_class_num'] or "未設定",
                choice_text="尚未選填",
                submit_time="---",
                pdf_bytes=b"" # 傳送空的內容避免噴錯
            )
            
            if success:
                print(f"✔️ {user['name']} 寄送成功")
            else:
                print(f"❌ {user['name']} 寄送失敗")
            
            await asyncio.sleep(1) # 避免被系統判斷為垃圾郵件

        print(f"✨ 任務完成，共處理了 {len(unsubmitted_users)} 筆資料。")

    except Exception as e:
        print(f"❌ 提醒任務失敗: {e}")
    finally:
        release_db(conn)

if __name__ == "__main__":
    asyncio.run(send_reminders())