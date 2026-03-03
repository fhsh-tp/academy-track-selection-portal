# import_students.py
import csv
import psycopg2
import os
from backend.security import get_password_hash 

DATABASE_URL = os.environ.get("DATABASE_URL")

def import_students():
    # 建立連線
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # 讀取 CSV
    with open('students.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # --- 關鍵修正：加上 .strip() ---
            raw_password = row['password'].strip() 
            hashed_pw = get_password_hash(raw_password) 
            
            # 存入資料庫 (使用 upsert 邏輯)
            cur.execute("""
                INSERT INTO users (student_id, name, password, role, email) 
                VALUES (%s, %s, %s, 'student', %s) 
                ON CONFLICT (student_id) DO UPDATE SET 
                password = EXCLUDED.password,
                name = EXCLUDED.name,
                email = EXCLUDED.email
            """, (row['student_id'], row['name'], hashed_pw, row['email']))
            print(f"✅ 已處理學生: {row['name']} (加密完畢)")
            
    conn.commit()
    cur.close()
    conn.close()
    print("🎉 資料庫已全面同步完成！")

if __name__ == "__main__":
    import_students()