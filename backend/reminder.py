# backend/reminder.py
import asyncio
from backend.database import get_db, release_db
from backend.mailer import send_confirmation_email
import psycopg2.extras

async def send_reminders():
    print("🚀 開始執行選填提醒任務...")
    conn = get_db()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # 找出所有還沒填寫的學生 (LEFT JOIN 後 s.choice 為空)
        cur.execute('''
            SELECT u.student_id, u.email 
            FROM users u 
            LEFT JOIN selections s ON u.student_id = s.student_id 
            WHERE s.choice IS NULL AND u.role = 'student' AND u.email IS NOT NULL
        ''')
        unsubmitted_users = cur.fetchall()
        cur.close()

        for user in unsubmitted_users:
            print(f"📧 寄送提醒給: {user['student_id']} ({user['email']})")
            await send_confirmation_email(
                recipient=user['email'],
                choice="（請儘速完成選填）"
            )
            # 為了避免寄太快被郵件服務擋掉，稍微延遲一下
            await asyncio.sleep(1)

        print(f"✅ 完成，共寄出了 {len(unsubmitted_users)} 封提醒郵件。")

    except Exception as e:
        print(f"❌ 提醒任務失敗: {e}")
    finally:
        release_db(conn)

if __name__ == "__main__":
    asyncio.run(send_reminders())