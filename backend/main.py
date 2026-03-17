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
    deadline_dt = datetime(2026, 4, 30, 23, 59, 59)

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
    print(f"DEBUG: 收到的 email 欄位: {data.get('email')}", flush=True)
    name = data.get("name")
    student_id = data.get("student_id")
    email = data.get("email")
    choice_num = data.get("choice")
    submit_time = data.get("submit_time")
    # 這裡從前端獲取班級座號資訊，若前端無傳入則預設為空字串
    studen_class_num = data.get("student_class_num", "")

    if not email:
        return {"status": "error", "message": "後端沒有收到 email"}

    choice_map = {1: "文法商 (數A課程路徑)", 2: "文法商 (數B課程路徑)", 3: "二類組 (理工資)", 4: "三類組 (生醫農)"}
    choice_text = choice_map.get(int(choice_num), "未知類組")

    # 修正：傳入 5 個參數給 generate_formal_pdf
    pdf_bytes = generate_formal_pdf(name, student_id, student_class_num, int(choice_num), submit_time)
    
    if not pdf_bytes:
        return {"status": "error", "message": "PDF 生成失敗"}

    # 修正：傳入對應參數給 send_confirmation_email
    success = send_confirmation_email(email, name, student_id, student_class_num, choice_text, submit_time, pdf_bytes)
    
    if success:
        return {"status": "success", "message": "申請已送出，確認信已寄至您的信箱"}
    else:
        return {"status": "error", "message": "郵件寄送失敗，請稍後再試"}

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
            # 去除欄位名稱空格，防止 student_class_num 讀不到
            row = {str(k).strip(): str(v).strip() for k, v in row.items() if k}
            
            student_id = row.get('student_id')
            name = row.get('name')
            email = row.get('email')
            class_num = row.get('student_class_num') or row.get('studen_class_num')
            
            print(f"DEBUG: 正在處理: {name} | 座號: {class_num}")
            
            password_val = row.get('password')
            hashed_pw = get_password_hash(str(password_val).strip())

            # 修正：SQL 指令後方必須補上對應的資料參數
            cur.execute("""
                INSERT INTO users (student_id, name, email, student_class_num, password, role) 
                VALUES (%s, %s, %s, %s, %s, 'student') 
                ON CONFLICT (student_id) DO UPDATE SET 
                    name = EXCLUDED.name, 
                    email = EXCLUDED.email, 
                    student_class_num = EXCLUDED.student_class_num,
                    password = EXCLUDED.password
            """, (
                student_id,
                name,
                email,
                class_num,
                hashed_pw
            ))
            
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