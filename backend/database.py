import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
from backend.security import get_password_hash

DATABASE_URL = os.environ.get("DATABASE_URL")

# 初始化連線池
# minconn=1: 最少保持 1 個連線
# maxconn=20: 最多擴展到 20 個連線 (Render 免費版 Postgres 通常支援 20-50 連線，設 20 很安全)
try:
    db_pool = psycopg2.pool.ThreadedConnectionPool(1, 20, DATABASE_URL, sslmode='require')
    print("✅ 資料庫連線池建立成功")
except Exception as e:
    print(f"❌ 資料庫連線池建立失敗: {e}")

def get_db():
    """從連線池取得一個連線"""
    return db_pool.getconn()

def release_db(conn):
    """將連線歸還給連線池"""
    db_pool.putconn(conn)

def init_db():
    conn = get_db()
    try:
        cur = conn.cursor()
        # 1. 建立學生帳號表
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'student'
            )
        ''')
        # 2. 建立志願紀錄表
        cur.execute('''
            CREATE TABLE IF NOT EXISTS selections (
                student_id TEXT PRIMARY KEY REFERENCES users(student_id),
                choice INTEGER NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 建立預設管理員與測試學生
        admin_pw = get_password_hash("FhCTF")
        cur.execute('''
            INSERT INTO users (student_id, name, password, role)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (student_id) DO NOTHING
        ''', ("admin", "系統管理員", admin_pw, "admin"))
        
        test_student_pw = get_password_hash("123456")
        cur.execute('''
            INSERT INTO users (student_id, name, password, role)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (student_id) DO NOTHING
        ''', ("114001", "測試同學", test_student_pw, "student"))
        
        conn.commit()
        cur.close()
    finally:
        release_db(conn) # 務必歸還！
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
        release_db(conn) # 務必歸還！

def import_students(student_list):
    conn = get_db()
    try:
        cur = conn.cursor()
        for student in student_list:
            hashed_pw = get_password_hash(student['password'])
            cur.execute('''
                INSERT INTO users (student_id, name, password, role)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (student_id) DO NOTHING
            ''', (student['id'], student['name'], hashed_pw, 'student'))
        conn.commit()
        cur.close()
    finally:
        release_db(conn)
    print(f"✅ 成功匯入 {len(student_list)} 名學生資料")