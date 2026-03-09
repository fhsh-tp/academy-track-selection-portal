import psycopg2
from psycopg2 import pool
import os
from datetime import datetime
from backend.security import get_password_hash

# 1. 取得環境變數
DATABASE_URL = os.environ.get("DATABASE_URL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# 2. 全域連線池變數
db_pool = None

def init_db_pool():
    global db_pool
    if db_pool is None:
        try:
            print("正在建立資料庫連線池...")
            # minconn=1: 平時保留一個，maxconn=20: 巔峰時期允許 20 個連線同時作業
            # 這對 Supabase 或 Zeabur 的免費版來說是個安全的範圍
            db_pool = psycopg2.pool.ThreadedConnectionPool(
                1, 20, DATABASE_URL, sslmode='require'
            )
            print("✅ 資料庫連線池建立成功 (Max: 20)")
        except Exception as e:
            print(f"❌ 資料庫連線池建立失敗: {e}")
            raise e

def get_db():
    if db_pool is None:
        init_db_pool()
    return db_pool.getconn()

def release_db(conn):
    if db_pool:
        db_pool.putconn(conn)

# 初始化資料庫表格
def init_db():
    conn = get_db()
    try:
        cur = conn.cursor()
        # 建立表格
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'student',
                email TEXT
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS selections (
                student_id TEXT PRIMARY KEY REFERENCES users(student_id),
                choice INTEGER NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 處理管理員帳號
        if ADMIN_PASSWORD:
            admin_pw = get_password_hash(ADMIN_PASSWORD)
            cur.execute("""
                INSERT INTO users (student_id, name, password, role, email) 
                VALUES (%s, %s, %s, 'admin', %s) 
                ON CONFLICT (student_id) DO UPDATE SET password = EXCLUDED.password
            """, ("admin", "系統管理員", admin_pw, "admin@school.edu"))
        
        conn.commit()
        cur.close()
        print("✅ 資料庫結構初始化完成。")
    finally:
        release_db(conn)

def save_choice(student_id, choice):
    conn = get_db()
    try:
        cur = conn.cursor()
        # 使用 PostgreSQL 的 UPSERT 語法，防止重複寫入導致的錯誤
        cur.execute("""
            INSERT INTO selections (student_id, choice, updated_at)
            VALUES (%s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (student_id) 
            DO UPDATE SET 
                choice = EXCLUDED.choice,
                updated_at = CURRENT_TIMESTAMP
        """, (student_id, choice))
        conn.commit()
        cur.close()
        print(f"✅ 成功儲存學生 {student_id} 的選項")
    except Exception as e:
        conn.rollback()
        print(f"❌ 儲存選項時發生錯誤: {e}")
        raise e
    finally:
        release_db(conn)