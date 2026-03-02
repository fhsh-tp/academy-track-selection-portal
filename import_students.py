import csv
import psycopg2
import os
from backend.security import get_password_hash 
# 確保你從環境變數讀取資料庫連結
DATABASE_URL = os.environ.get("DATABASE_URL")

def import_students():
    # 建立連線
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # 讀取 CSV
    with open('students.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # 1. 把明文密碼變成雜湊
            hashed_pw = get_password_hash(row['password'])
            
            # 2. 存入資料庫
            cur.execute("""
                INSERT INTO users (student_id, name, password, role, email) 
                VALUES (%s, %s, %s, 'student', %s) 
                ON CONFLICT (student_id) DO UPDATE SET 
                password = EXCLUDED.password, 
                name = EXCLUDED.name,
                email = EXCLUDED.email
            """, (row['student_id'], row['name'], hashed_pw, row['email']))
            print(f"✅ 已匯入學生: {row['name']}")
            
    conn.commit()
    cur.close()
    conn.close()
    print("🎉 所有學生資料皆已成功儲存到雲端資料庫！")

if __name__ == "__main__":
    import_students()