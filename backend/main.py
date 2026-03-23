import os
import asyncio
import psycopg2
import psycopg2.extras
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import csv
import io

# 導入自訂模組
from backend.mailer import send_confirmation_email, generate_formal_pdf
from backend.database import init_db, init_db_pool, get_db, release_db
from backend.security import verify_password, create_access_token, get_current_user, get_password_hash

# --- 路徑設定 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)                  # 專案根目錄
font_path = os.path.join(ROOT_DIR, "frontend", "NotoSansTC-Regular.ttf")

# --- 系統設定 ---
DEADLINE = os.environ.get("DEADLINE_DATE", "2026-04-30 23:59:59")
try:
    deadline_dt = datetime.strptime(DEADLINE, "%Y-%m-%d %H:%M:%S")
except:
    deadline_dt = datetime(2026, 3, 26, 12, 30, 00)

scheduler = AsyncIOScheduler()
CHOICE_MAP = {1: "一類組 (文法商數A)", 2: "一類組 (文法商數B)", 3: "理工資", 4: "生醫農"}

# --- 生命周期管理 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 系統啟動中...")
    init_db_pool()
    init_db()
    scheduler.start()
    yield
    print("🛑 系統關閉中...")
    if scheduler.running: scheduler.shutdown()

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- 模型 ---
class LoginData(BaseModel): student_id: str; password: str
class SelectionData(BaseModel): choice: int

# --- API 路由 ---
@app.post("/login")
async def login(data: LoginData):
    def db_logic():
        conn = get_db()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT * FROM users WHERE student_id = %s", (data.student_id,))
            return cur.fetchone()
        finally: release_db(conn)
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
        finally: release_db(conn)
    user = await asyncio.to_thread(db_logic)
    if not user or user.get('role') != 'admin': raise HTTPException(status_code=403, detail="權限不足")
    if not verify_password(data.password, user['password']): raise HTTPException(status_code=401, detail="密碼錯誤")
    token = create_access_token(data={"sub": user['student_id'], "role": user['role']})
    return {"access_token": token, "role": user['role']}

@app.post("/submit")
async def submit(data: dict):
    # 1. 取得資料
    name = data.get("name")
    student_id = data.get("student_id")
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
    choice_map = {1: "文法商 (數A課程路徑)", 2: "文法商 (數B課程路徑)", 3: "二類組 (理工資)", 4: "三類組 (生醫農)"}
    choice_text = choice_map.get(int(choice_num), "未知類組")

    pdf_bytes = generate_formal_pdf(name, student_id, student_class_num, int(choice_num), submit_time)
    
    if not pdf_bytes:
        return {"status": "error", "message": "PDF 生成失敗"}

    success = send_confirmation_email(email, name, student_id, student_class_num, choice_text, submit_time, pdf_bytes)
    
    if success:
        return {"status": "success", "message": "申請已送出，確認信已寄達"}
    else:
        return {"status": "error", "message": "郵件寄送失敗，但資料已存檔"}

@app.get("/admin/all")
async def get_all_students(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin": raise HTTPException(status_code=403, detail="權限不足")
    def db_logic():
        conn = get_db()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT u.student_id, u.name, u.email, u.student_class_num, s.choice, s.updated_at FROM users u LEFT JOIN selections s ON u.student_id = s.student_id WHERE u.role = 'student'")
            return cur.fetchall()
        finally: release_db(conn)
    return await asyncio.to_thread(db_logic)

@app.post("/admin/import-students")
async def import_students(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin": raise HTTPException(status_code=403, detail="權限不足")
    content = await file.read()
    stream = io.StringIO(content.decode('utf-8'))
    reader = csv.DictReader(stream)
    conn = get_db()
    try:
        cur = conn.cursor()
        for row in reader:
            row = {str(k).strip(): str(v).strip() for k, v in row.items() if k}
            
            student_id = row.get('student_id')
            name = row.get('name')
            email = row.get('email')
            # 統一使用 student_class_num
            student_class_num = row.get('student_class_num', "").strip()
            if not student_class_num:
                print(f"⚠️ 學生 {name} 缺少班級座號，跳過匯入")
                continue
            
            print(f"DEBUG: 正在處理: {name} | 座號: {student_class_num}") # 這裡要改成 student_class_num
            
            password_val = row.get('password')
            hashed_pw = get_password_hash(str(password_val).strip())

            cur.execute("""
                INSERT INTO users (student_id, name, email, student_class_num, password, role) 
                VALUES (%s, %s, %s, %s, %s, 'student') 
                ON CONFLICT (student_id) DO UPDATE SET 
                    student_class_num = EXCLUDED.student_class_num,
                    password = EXCLUDED.password
            """, (student_id, name, email, student_class_num, hashed_pw))
            
        conn.commit()
        cur.close()
        print("✅ 資料匯入並提交成功")
        return {"message": "匯入成功"}
    except Exception as e:
        conn.rollback()
        print(f"❌ 匯入出錯: {str(e)}")
        raise HTTPException(status_code=400, detail=f"匯入失敗: {str(e)}")
    finally: release_db(conn)
@app.api_route("/", methods=["GET", "HEAD"], response_class=FileResponse)
async def read_index(): return os.path.join(ROOT_DIR, "frontend", "index.html")
@app.get("/login", response_class=FileResponse)
async def read_login(): return os.path.join(ROOT_DIR, "frontend", "login.html")
@app.get("/choose", response_class=FileResponse)
async def read_choose(): return os.path.join(ROOT_DIR, "frontend", "choose.html")
@app.get("/admin", response_class=FileResponse)
async def read_admin(): return os.path.join(ROOT_DIR, "frontend", "admin.html")
@app.get("/admin-login", response_class=FileResponse)
async def read_admin_login(): return os.path.join(ROOT_DIR, "frontend", "admin-login.html")
app.mount("/static", StaticFiles(directory=os.path.join(ROOT_DIR, "frontend")), name="static")