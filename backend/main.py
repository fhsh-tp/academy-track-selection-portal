import os
import asyncio
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import csv
import io
from pathlib import Path

# 導入自訂模組
from backend.mailer import send_confirmation_email, generate_formal_pdf
from backend.database import init_db, init_db_pool, get_db, release_db
from backend.security import verify_password, create_access_token, get_current_user, get_password_hash

# --- 路徑設定 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
font_path = os.path.join(BASE_DIR, "static", "TW-Kai-98_1.ttf")

# --- 系統設定 ---
DEADLINE = os.environ.get("DEADLINE_DATE")

def is_deadline():
    now = datetime.now(timezone(timedelta(hours=8)))
    deadline_dt = datetime.strptime(DEADLINE, "%Y-%m-%d %H:%M:%S%z")

    if now > deadline_dt:
        raise HTTPException(404, {"message": "shutdown..."})

CHOICE_MAP = {1: "(文法商數A)", 2: "(文法商數B)", 3: "理工資", 4: "生醫農"}

# --- 生命周期管理 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 系統啟動中...")
    init_db_pool()
    init_db()
    yield
    print("🛑 系統關閉中...")

# 設定 origin
origins = []
prod_domain = os.getenv("PROD_DOMAIN")
mode = os.getenv("FASTAPI_APP_ENVIRONMENT") or "dev"

if prod_domain:
    origins.append(prod_domain)
if mode != "prod":
    origins.append("localhost")
    origins.append("localhost:8000")
    origins.append("*.orb.local")

app = FastAPI(lifespan=lifespan, dependencies=[Depends(is_deadline)])
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["GET", "POST"], allow_headers=["*"])

# Binding static directory
app.mount("/static", StaticFiles(directory=Path('backend/static')), name="static")

# --- 模型 ---
class LoginData(BaseModel): 
    student_id: str
    password: str

class SelectionData(BaseModel):
    choice: int

# --- API 路由 ---
@app.get("/auth")
async def nginx_auth_middleware(user=Depends(get_current_user)):
    response = Response(200)
    response.headers['X-User-ID'] = user.get("student_id")
    response.headers['X-User-Role'] = user.get("role")
    return response

@app.get('/admin-auth')
async def nginx_admin_auth_middleware(user=Depends(get_current_user)):
    if user.get('role') == 'admin':
        response = Response(200)
        response.headers['X-User-ID'] = user.get("student_id")
        response.headers['X-User-Role'] = user.get("role")
        return response
    raise HTTPException(401, detail="Unauthorized")

@app.post("/login")
async def login(data: LoginData):
    def db_logic():
        conn = get_db()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT * FROM users WHERE student_id = %s", (data.student_id,))
            return cur.fetchone()
        finally: 
            release_db(conn)
    user = await asyncio.to_thread(db_logic)
    if not user or not verify_password(data.password, user['password']): 
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    token = create_access_token(data={"sub": user['student_id'], "role": user['role']})
    return {
        "access_token": token, 
        "role": user['role'],
        "name": user['name'],        
        "email": user['email'],      
        "student_id": user['student_id'],
        "student_class_num": user.get('student_class_num', "未填寫") 
    }

@app.post("/admin-login")
async def admin_login(data: LoginData):
    def db_logic():
        conn = get_db()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT * FROM users WHERE student_id = %s", (data.student_id,))
            return cur.fetchone()
        finally: 
            release_db(conn)
    user = await asyncio.to_thread(db_logic)
    if not user or user.get('role') != 'admin': 
        raise HTTPException(status_code=403, detail="權限不足")
    if not verify_password(data.password, user['password']): 
        raise HTTPException(status_code=401, detail="帳號密碼錯誤")
    token = create_access_token(data={"sub": user['student_id'], "role": user['role']})
    return {"access_token": token, "role": user['role']}

@app.post("/submit")
async def submit(data: dict, user=Depends(get_current_user)):
    # 1. 取得資料
    student_id = data.get("student_id")
    
    # 增加 token 與 student_id 之間，確認身分
    if user.get("student_id") != student_id:
        raise HTTPException(403, detail="被禁止的操作")
    
    name = data.get("name")
    email = data.get("email")
    choice_num = data.get("choice")
    submit_time = data.get("submit_time")
    student_class_num = data.get("student_class_num", "")

    if not email:
        return {"status": "error", "message": "後端沒有收到 email"}

    # 2. 【關鍵】寫入資料庫，管理員才看得到
    def db_save():
        conn = get_db()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO selections (student_id, choice, updated_at)
                VALUES (%s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (student_id) 
                DO UPDATE SET choice = EXCLUDED.choice, updated_at = CURRENT_TIMESTAMP
            """, (student_id, choice_num))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"❌ 資料庫儲存失敗: {e}")
            return False
        finally:
            release_db(conn)

    db_success = await asyncio.to_thread(db_save)
    if not db_success:
        raise HTTPException(status_code=500, detail="資料庫紀錄失敗")

    # 3. 寄信與產生 PDF
    choice_map = {1: "文法商 (數A課程路徑)", 2: "文法商 (數B課程路徑)", 3: "理工資", 4: "生醫農"}
    choice_text = choice_map.get(int(choice_num), "未知類組")

    pdf_bytes = generate_formal_pdf(name, student_id, student_class_num, int(choice_num), submit_time)
    
    if not pdf_bytes:
        return {"status": "error", "message": "PDF 生成失敗"}

    success = await send_confirmation_email(email, name, student_id, student_class_num, choice_text, submit_time, pdf_bytes)
    
    if success:
        return {"status": "success", "message": "申請已送出，確認信已寄達"}
    else:
        return {"status": "error", "message": "郵件寄送失敗，但資料已存檔"}

@app.get("/admin/all")
async def get_all_students(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin": 
        raise HTTPException(status_code=403, detail="權限不足")
    def db_logic():
        conn = get_db()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("""
                SELECT 
                    u.student_id, 
                    u.name, 
                    u.email, 
                    u.student_class_num, 
                    s.choice, 
                    TO_CHAR(s.updated_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Taipei', 'YYYY/MM/DD HH24:MI:SS') as updated_at 
                FROM users u 
                LEFT JOIN selections s ON u.student_id = s.student_id 
                WHERE u.role = 'student'
            """)
            return cur.fetchall()
        finally: 
            release_db(conn)
    return await asyncio.to_thread(db_logic)

@app.post("/admin/import-students")
async def import_students(file: UploadFile = File(...), user=Depends(get_current_user)):
    if user.get("role") != 'admin':
        raise HTTPException(403, detail="沒有權限操作")
    content = await file.read()
    conn = get_db()
    try:
        # 1. 處理編碼 (解決生僻字與 BOM 問題)
        try:
            decoded_content = content.decode('big5-hkscs')
        except:
            # utf-8-sig 會自動移除 Excel 產生的 BOM (\ufeff)
            decoded_content = content.decode('utf-8-sig', errors='replace')

        stream = io.StringIO(decoded_content.replace('\r\n', '\n'))
        reader = csv.DictReader(stream)
        
        # 2. 強制清理欄位標題 (移除所有空格並轉小寫)
        if reader.fieldnames:
            reader.fieldnames = [fn.strip().lower() for fn in reader.fieldnames]
        
        cur = conn.cursor()
        success_count = 0
        
        for row in reader:
            # 3. 清理每一列的資料：確保抓取的 Key 都有 strip()，且 Value 也要 strip()
            # 這樣就算 CSV 裡寫 " 112001 "，也會變成 "112001"
            name = (row.get('name') or row.get('姓名') or "").strip()
            sid = (row.get('student_id') or row.get('學號') or "").strip()
            # 自訂密碼抓取與清理
            raw_password = (row.get('password') or row.get('密碼') or sid).strip()
            
            cnum = (row.get('student_class_num') or row.get('class_num') or row.get('班級座號') or "").strip()
            email = (row.get('email') or row.get('電子信箱') or "").strip()

            if name and sid:
                # 這裡只加密清理過後的乾淨字串
                hashed_pw = get_password_hash(raw_password)
                
                cur.execute("""
                    INSERT INTO users (student_id, name, password, role, email, student_class_num)
                    VALUES (%s, %s, %s, 'student', %s, %s)
                    ON CONFLICT (student_id) 
                    DO UPDATE SET 
                        name = EXCLUDED.name,
                        password = EXCLUDED.password,
                        email = EXCLUDED.email,
                        student_class_num = EXCLUDED.student_class_num
                """, (sid, name, hashed_pw, email if email else None, cnum if cnum else None))
                success_count += 1
        
        conn.commit()
        cur.close()
        print(f"✅ 成功匯入 {success_count} 筆資料 (含密碼加密)", flush=True)
        return {"status": "success", "message": f"成功匯入 {success_count} 筆學生資料"}

    except Exception as e:
        if conn: 
            conn.rollback()
        print(f"❌ 匯入失敗: {str(e)}", flush=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn: 
            release_db(conn)
# --- main.py 新增路由 ---

@app.post("/admin/send-reminders")
async def api_send_reminders(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="權限不足")
    
    # 修正這裡：改用 student_id 或 name，或是用 .get() 避免崩潰
    admin_name = current_user.get("name")
    admin_id = current_user.get("student_id", "Unknown")
    
    print("\n" + "="*30)
    print(f"📣 [ADMIN] 管理員 {admin_name} ({admin_id}) 觸發了手動提醒信功能")
    print(f"🕒 時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    conn = None
    try:
        conn = get_db()
        # 使用 RealDictCursor 讓結果變成字典，方便存取
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # 2. 查詢未選填且有 Email 的學生名單
        # 注意：確保 Table 名稱與你的 database.py 一致 (這裡是 users 和 selections)
        sql_query = '''
            SELECT u.student_id, u.name, u.email, u.student_class_num
            FROM users u 
            LEFT JOIN selections s ON u.student_id = s.student_id 
            WHERE s.choice IS NULL 
              AND u.role = 'student' 
              AND u.email IS NOT NULL 
              AND u.email != ''
        '''
        print("🔍 正在查詢未選填名單...")
        cur.execute(sql_query)
        unsubmitted_users = cur.fetchall()
        cur.close()

        print(f"📊 找到 {len(unsubmitted_users)} 位未選填學生。")

        if not unsubmitted_users:
            return {"status": "success", "message": "目前所有學生都已完成選填，無需寄信。"}

        # 3. 逐一寄信
        success_count = 0
        fail_count = 0
        
        print("🚀 開始寄送郵件...")
        for i, user in enumerate(unsubmitted_users, 1):
            print(f"📧 [({i}/{len(unsubmitted_users)})] 嘗試寄送至: {user['email']} ({user['name']})")
            
            try:
                # 呼叫 mailer.py 的寄信函式 (確保參數對齊)
                # 提醒信不需要 PDF，pdf_bytes 傳入空的 bytes (b"")
                success = await send_confirmation_email(
                    recipient=user['email'],
                    student_name=user['name'],
                    student_id=user['student_id'],
                    student_class_num=user['student_class_num'] or "未設定",
                    choice_text="系统提醒：您尚未完成志願選填",
                    submit_time="--- (手動提醒) ---",
                    pdf_bytes=b""
                )
                
                if success:
                    print(f"   ✔️ [SUCCESS] {user['name']} 寄送成功")
                    success_count += 1
                else:
                    print(f"   ⚠️ [FAILED] {user['name']} 寄送失敗 (API 可能拒絕)")
                    fail_count += 1
                    
            except Exception as mail_err:
                print(f"   ❌ [EXCEPTION] 寄信過程出錯: {mail_err}")
                fail_count += 1
            
            # 延遲 1.2 秒，避免被郵件伺服器判定為垃圾郵件或觸發 Brevo 的頻率限制
            await asyncio.sleep(1.2)

        print(f"✨ 任務完成。成功: {success_count} 封, 失敗: {fail_count} 封。")
        print("="*30 + "\n")
        
        return {
            "status": "success", 
            "message": f"提醒信寄送完畢。成功: {success_count} 封，失敗: {fail_count} 封。",
            "details": {
                "total_found": len(unsubmitted_users),
                "success": success_count,
                "failed": fail_count
            }
        }

    except Exception as e:
        print(f"💥 [CRITICAL] 提醒任務發生重大錯誤: {e}")
        raise HTTPException(status_code=500, detail=f"系統錯誤: {str(e)}")
    finally:
        if conn:
            release_db(conn)
            print("🔌 資料庫連線已釋放")
