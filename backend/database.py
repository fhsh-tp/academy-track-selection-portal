import psycopg2
from psycopg2 import pool
import os
from .security import get_password_hash # 確保路徑正確

DATABASE_URL = os.environ.get("DATABASE_URL")
db_pool = None

def init_db_pool():
    global db_pool
    if db_pool is None:
        try:
            # Render 免費版建議設 1-15 個連線，既能應付大流量又不會超出資料庫限制
            db_pool = psycopg2.pool.ThreadedConnectionPool(1, 15, DATABASE_URL, sslmode='require')
            print("✅ 資料庫連線池建立成功")
        except Exception as e:
            print(f"❌ 連線池建立失敗: {e}")
            raise e

def get_db():
    if db_pool is None: init_db_pool()
    return db_pool.getconn()

def release_db(conn):
    if db_pool: db_pool.putconn(conn)

def save_choice(student_id, choice):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO selections (student_id, choice, updated_at)
            VALUES (%s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (student_id) 
            DO UPDATE SET choice = EXCLUDED.choice, updated_at = CURRENT_TIMESTAMP
        """, (student_id, choice))
        conn.commit()
        cur.close()
    finally:
        release_db(conn)

def init_db():
    conn = get_db()
    try:
        cur = conn.cursor()
        # 1. 建立基礎表格
        cur.execute("CREATE TABLE IF NOT EXISTS users (student_id TEXT PRIMARY KEY, name TEXT NOT NULL, password TEXT NOT NULL, role TEXT DEFAULT 'student', email TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS selections (student_id TEXT PRIMARY KEY REFERENCES users(student_id), choice INTEGER NOT NULL, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        
        # 2. 【新增】自動檢查並補上班級座號欄位
        cur.execute("""
            DO $$ 
            BEGIN 
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                            WHERE table_name='users' AND column_name='student_class_num') THEN
                    ALTER TABLE users ADD COLUMN student_class_num TEXT;
                END IF;
            END $$;
        """)

        # 3. 管理員邏輯
        admin_pw = os.getenv("ADMIN_PASSWORD")
        if admin_pw:
            hashed_pw = get_password_hash(admin_pw)
            cur.execute("INSERT INTO users (student_id, name, password, role) VALUES ('admin', '管理員', %s, 'admin') ON CONFLICT DO NOTHING", (hashed_pw,))
        
        conn.commit()
        cur.close()
        print("✅ 資料庫初始化與欄位檢查完成")
    except Exception as e:
        print(f"❌ 資料庫初始化失敗: {e}")
        conn.rollback()
    finally:
        release_db(conn)