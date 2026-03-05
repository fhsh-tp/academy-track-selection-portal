import psycopg2
from psycopg2 import pool
import os
from datetime import datetime
from backend.security import get_password_hash

DATABASE_URL = os.environ.get("DATABASE_URL")
db_pool = None

def init_db_pool():
    global db_pool
    if db_pool is None:
        try:
            print("正在建立資料庫連線池...")
            # 限制 maxconn 為 15，避免超出免費版 Postgres 的連線限制
            db_pool = psycopg2.pool.ThreadedConnectionPool(1, 15, DATABASE_URL, sslmode='require')
            print("✅ 資料庫連線池建立成功")
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

def init_db():
    conn = get_db()
    try:
        cur = conn.cursor()
        
        # 1. 建立表格結構
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
        
        # 2. 僅保留系統必要的管理員帳號
        raw_admin_pw = os.getenv("ADMIN_PASSWORD")
        if not raw_admin_pw:
            print("⚠️ 警告：未設定 ADMIN_PASSWORD 環境變數，管理員登入將失效")
        else:
            admin_pw = get_password_hash(raw_admin_pw)
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
    """
    將學生的選擇存入 selections 表格，若已選擇則更新
    """
    conn = get_db()
    try:
        cur = conn.cursor()
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