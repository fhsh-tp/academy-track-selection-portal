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

# PDF 相關
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 導入自訂模組
from backend.mailer import send_confirmation_email, generate_formal_pdf
from backend.database import init_db, init_db_pool, save_choice, get_db, release_db
from backend.security import verify_password, create_access_token, get_current_user, get_password_hash

# --- 全域路徑設定 ---
# 獲取 main.py 所在的絕對目錄 (即 backend/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 獲取專案根目錄 (上一層)
ROOT_DIR = os.path.dirname(BASE_DIR)
# 定義字型路徑
font_path = os.path.join(ROOT_DIR, "frontend", "NotoSansTC-Regular.ttf")

# 註冊字型
if os.path.exists(font_path):
    pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
    print(f"✅ 字型註冊成功: {font_path}")
else:
    print(f"❌ 警告：字型檔未找到，檢查路徑: {font_path}")

# --- 系統設定 ---
DEADLINE = os.environ.get("DEADLINE_DATE", "2026-04-30 23:59:59")
try:
    deadline_dt = datetime.strptime(DEADLINE, "%Y-%m-%d %H:%M:%S")
except:
    deadline_dt = datetime(2026, 4, 30, 23, 59, 59)

scheduler = AsyncIOScheduler()
CHOICE_MAP = {1: "一類組 (文法商數A)", 2: "一類組 (文法商數B)", 3: "二類組 (理工資)", 4: "三類組 (生醫農)"}

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
    if not user or not verify_password(data.password, user['password']): raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    token = create_access_token(data={"sub": user['student_id'], "role": user['role']})
    return {"access_token": token, "role": user['role']}

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
    # ... 處理資料邏輯 ...
    
    print("DEBUG: 進入 submit 處理流程", flush=True)
    
    # 1. 生成 PDF
    pdf_bytes = generate_formal_pdf(name, student_id, choice, time)
    if not pdf_bytes:
        return {"status": "error", "message": "PDF 生成失敗"}
    
    # 2. 直接發送 (拿掉 BackgroundTasks)
    success = send_confirmation_email(email, name, student_id, choice, time, pdf_bytes)
    
    if success:
        return {"status": "success", "message": "郵件已發送"}
    else:
        return {"status": "error", "message": "郵件發送失敗，請查看 Log"}

@app.get("/admin/all")
async def get_all_students(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin": raise HTTPException(status_code=403, detail="權限不足")
    def db_logic():
        conn = get_db()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT u.student_id, u.name, u.email, s.choice, s.updated_at FROM users u LEFT JOIN selections s ON u.student_id = s.student_id WHERE u.role = 'student'")
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
            hashed_pw = get_password_hash(row.get('password', '123456').strip())
            cur.execute("INSERT INTO users (student_id, name, email, password, role) VALUES (%s, %s, %s, %s, 'student') ON CONFLICT (student_id) DO UPDATE SET name = EXCLUDED.name, email = EXCLUDED.email, password = EXCLUDED.password", (row['student_id'], row['name'], row['email'], hashed_pw))
        conn.commit()
        cur.close()
        return {"message": "匯入成功"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"匯入失敗: {str(e)}")
    finally: release_db(conn)

# 靜態檔案路由
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