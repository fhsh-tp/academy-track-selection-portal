# import_students.py
import csv
import psycopg2
import os
from backend.security import get_password_hash # 務必使用這裡的函數

DATABASE_URL = os.environ.get("DATABASE_URL")

def import_students():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    with open('students.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # 這裡一定是用新的 werkzeug 生成的雜湊
            hashed_pw = get_password_hash(row['password']) 
            
            cur.execute("""
                INSERT INTO users (student_id, name, password, role, email) 
                VALUES (%s, %s, %s, 'student', %s) 
                ON CONFLICT (student_id) DO UPDATE SET 
                password = EXCLUDED.password
            """, (row['student_id'], row['name'], hashed_pw, row['email']))
            print(f"✅ 已處理學生: {row['name']}")
            
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    import_students()