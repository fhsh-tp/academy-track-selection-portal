import asyncio
import os
from datetime import datetime
from backend.database import get_db, release_db
from backend.mailer import send_confirmation_email
import psycopg2.extras

# 修正 1: 必須導入 os 模組 (原本漏掉了)
# 修正 2: 統一讀取環境變數，確保與 main.py 一致
DEADLINE_STR = os.environ.get("DEADLINE_DATE", "2026-04-30 23:59:59")

async def send_reminders():
    # 修正 3: 新增時間判斷邏輯
    try:
        deadline_dt = datetime.strptime(DEADLINE_STR, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        # 預防萬一環境變數格式錯誤
        deadline_dt = datetime(2026, 4, 30, 23, 59, 59)

    now = datetime.now()
    days_left = (deadline_dt - now).days

    print(f"⏰ 目前時間: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏳ 距離截止還有: {days_left} 天")

    # 邏輯檢查：只有在剛好剩 3 天時執行 (可視測試需求修改此判斷)
    if days_left != 3:
        print(f"🛑 尚未到達寄信提醒時間 (設定為剩 3 天時寄信)。任務終止。")
        return

    print("🚀 條件達成，開始執行選填提醒任務...")
    
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # 找出所有還沒填寫的學生 (LEFT JOIN 後 s.choice 為空)
        # 注意：這裡的 table 名稱要與 database.py 的 init_db 一致
        cur.execute('''
            SELECT u.student_id, u.email 
            FROM students u 
            LEFT JOIN student_selections s ON u.student_id = s.student_id 
            WHERE s.choice IS NULL AND u.email IS NOT NULL
        ''')
        unsubmitted_users = cur.fetchall()
        cur.close()

        if not unsubmitted_users:
            print("✅ 太棒了！名單內所有學生都已完成填寫。")
            return

        for user in unsubmitted_users:
            print(f"📧 寄送提醒給: {user['student_id']} ({user['email']})")
            # 呼叫 mailer.py 裡的寄信函式
            await send_confirmation_email(
                recipient=user['email'],
                choice="（尚未完成填寫，請於截止日前操作）"
            )
            # 延遲避免被當成垃圾信
            await asyncio.sleep(1)

        print(f"✨ 完成，共寄出了 {len(unsubmitted_users)} 封提醒郵件。")

    except Exception as e:
        print(f"❌ 提醒任務失敗: {e}")
    finally:
        release_db(conn)

if __name__ == "__main__":
    asyncio.run(send_reminders())