import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
from backend.security import get_password_hash

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

def init_db():
    conn = get_db()
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
    
    # --- 初始資料插入 (要在建立表之後) ---
    
    # 建立預設管理員
    admin_pw = get_password_hash("FhCTF")
    cur.execute('''
        INSERT INTO users (student_id, name, password, role)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (student_id) DO NOTHING
    ''', ("admin", "系統管理員", admin_pw, "admin"))
    
    # 建立測試學生
    test_student_pw = get_password_hash("123456")
    cur.execute('''
        INSERT INTO users (student_id, name, password, role)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (student_id) DO NOTHING
    ''', ("114001", "測試同學", test_student_pw, "student"))
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ 資料庫初始化完成，初始帳號已建立。")

def save_choice(student_id, choice):
    conn = get_db()
    cur = conn.cursor()
    # 需求 9: ON CONFLICT 做更新 (Upsert)
    cur.execute('''
        INSERT INTO selections (student_id, choice, updated_at)
        VALUES (%s, %s, %s)
        ON CONFLICT (student_id) DO UPDATE 
        SET choice = EXCLUDED.choice, updated_at = EXCLUDED.updated_at
    ''', (student_id, choice, datetime.now()))
    conn.commit()
    cur.close()
    conn.close()

def import_students(student_list):
    """
    student_list 格式範例: 
    [{"id": "114001", "name": "張小明", "password": "出生日期1205"}, ...]
    """
    conn = get_db()
    cur = conn.cursor()
    
    for student in student_list:
        hashed_pw = get_password_hash(student['password']) # 每個人的密碼都獨立加密
        cur.execute('''
            INSERT INTO users (student_id, name, password, role)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (student_id) DO NOTHING
        ''', (student['id'], student['name'], hashed_pw, 'student'))
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ 成功匯入 {len(student_list)} 名學生資料")