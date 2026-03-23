import sys
import os
import csv
import psycopg2
from datetime import datetime

# 直接把你的 Render 外部連線字串貼在這裡
DB_URL = "postgresql://fhsh:Fgvh3yDCaOrV4LrDAztVUUUYcT8GQZ4G@dpg-d6gg350gjchc73c4hrgg-a.singapore-postgres.render.com/class_selection_5i5q"

# 確保能抓到 backend 裡的工具
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from backend.security import get_password_hash
except ImportError:
    print("❌ 找不到 backend 資料夾，請確保 reset.py 放在專案根目錄。")
    sys.exit(1)

def main():
    print(f"🌐 正在連線至 Render 資料庫...")
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        confirm = input("⚠️  確定要清空 Render 資料庫並重新匯入『有座號』的資料嗎？(y/N): ")
        if confirm.lower() != 'y': return

        # 1. 清空
        print("🧹 正在清空舊資料...")
        cur.execute("TRUNCATE TABLE selections, users RESTART IDENTITY CASCADE;")
        conn.commit()

        # 2. 檢查 CSV
        csv_file = "students.csv"
        if not os.path.exists(csv_file):
            print(f"❌ 錯誤：在目前資料夾找不到 {csv_file}")
            return

        # 3. 讀取並過濾
        print(f"🔍 讀取 {csv_file} 並過濾垃圾中...")
        success_count = 0
        with open(csv_file, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sid = (row.get('學號') or row.get('student_id', '')).strip()
                name = (row.get('姓名') or row.get('name', '')).strip()
                class_num = (row.get('班級座號') or row.get('student_class_num', '')).strip()
                email = (row.get('email', '')).strip()

                # 【核心過濾】座號空白或包含「未」的全部砍掉
                if not class_num or "未" in class_num:
                    continue

                cur.execute("""
                    INSERT INTO users (student_id, name, email, student_class_num, password, role)
                    VALUES (%s, %s, %s, %s, %s, 'student')
                    ON CONFLICT (student_id) DO NOTHING
                """, (sid, name, email, class_num, get_password_hash("123456")))
                success_count += 1

        conn.commit()
        print(f"✅ 成功！已匯入 {success_count} 筆乾淨資料。那些沒座號的垃圾已經被排除了。")

    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
    finally:
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    main()