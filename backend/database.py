import psycopg2
from psycopg2 import pool
import os
from datetime import datetime
from backend.security import get_password_hash

DATABASE_URL = os.environ.get("DATABASE_URL")
# 使用全域變數存放池，但初始為 None
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
        
        # 1. 建立 users 表 (加入 email 欄位)
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'student',
                email TEXT  -- 新增這一行
            )
        ''')
        
        # 2. 如果欄位已經存在但沒加上去，這行 SQL 可以確保欄位存在
        cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS email TEXT;")

        cur.execute('''
            CREATE TABLE IF NOT EXISTS selections (
                student_id TEXT PRIMARY KEY REFERENCES users(student_id),
                choice INTEGER NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 3. 處理預設帳號 (你可以這裡順便給它們測試信箱)
        admin_pw = get_password_hash("FhCTF")
        cur.execute("""
            INSERT INTO users (student_id, name, password, role, email) 
            VALUES (%s, %s, %s, %s, %s) 
            ON CONFLICT (student_id) DO UPDATE SET email = EXCLUDED.email
        """, ("admin", "系統管理員", admin_pw, "admin", "admin@school.edu"))
        
        test_student_pw = get_password_hash("123456")
        cur.execute("""
            INSERT INTO users (student_id, name, password, role, email) 
            VALUES (%s, %s, %s, %s, %s) 
            ON CONFLICT (student_id) DO UPDATE SET email = EXCLUDED.email
        """, ("114001", "測試同學", test_student_pw, "student", "11430362@fhsh.tp.edu.tw"))
        
        conn.commit()
        cur.close()
    finally:
        release_db(conn)
    print("✅ 資料庫初始化完成。")

def save_choice(student_id, choice):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO selections (student_id, choice, updated_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (student_id) DO UPDATE 
            SET choice = EXCLUDED.choice, updated_at = EXCLUDED.updated_at
        ''', (student_id, choice, datetime.now()))
        conn.commit()
        cur.close()
    finally:
        release_db(conn)