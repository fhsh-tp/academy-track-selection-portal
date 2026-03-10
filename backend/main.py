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

from reportlab.pdfgen import canvas

# 導入自訂模組
from backend.mailer import send_confirmation_email
from backend.database import init_db, init_db_pool, save_choice, get_db, release_db
from backend.security import verify_password, create_access_token, get_current_user, get_password_hash

# --- 全域設定 ---
# 增加預設值，避免環境變數沒抓到時崩潰
DEADLINE = os.environ.get("DEADLINE_DATE", "2026-04-30 23:59:59")
try:
    deadline_dt = datetime.strptime(DEADLINE, "%Y-%m-%d %H:%M:%S")
except:
    deadline_dt = datetime(2026, 4, 30, 23, 59, 59)

scheduler = AsyncIOScheduler()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHOICE_MAP = {
    1: "一類組 (文法商數A)",
    2: "一類組 (文法商數B)",
    3: "二類組 (理工資)",
    4: "三類組 (生醫農)"
}

# --- 生命周期管理 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 系統啟動中...")
    init_db_pool()
    init_db()
    scheduler.start()
    yield
    print("🛑 系統關閉中...")
    if scheduler.running:
        scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 資料模型 ---
class LoginData(BaseModel):
    student_id: str
    password: str

class SelectionData(BaseModel):
    choice: int

# --- API 路由 ---

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
    return {"access_token": token, "role": user['role']}

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
        raise HTTPException(status_code=401, detail="密碼錯誤")
    
    token = create_access_token(data={"sub": user['student_id'], "role": user['role']})
    return {"access_token": token, "role": user['role']}

@app.post("/submit") 
async def submit_choice(
    data: SelectionData,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)):

    # 1. 檢查期限
    if datetime.now() > deadline_dt:
        raise HTTPException(status_code=403, detail="選填期限已過")
    
    student_id = current_user.get('student_id') or current_user.get('sub') 
    if not student_id:
        raise HTTPException(status_code=401, detail="無效的使用者身分")
        
    submit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    choice_name = CHOICE_MAP.get(data.choice, "未知類組")

    # 2. 獲取使用者資料
    def get_user_info():
        conn = get_db()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT email, name FROM users WHERE student_id = %s", (student_id,))
            return cur.fetchone()
        finally:
            release_db(conn)

    user_info = await asyncio.to_thread(get_user_info)
    if not user_info:
        raise HTTPException(status_code=404, detail="找不到使用者資料")

    # 3. 儲存到資料庫
    await asyncio.to_thread(save_choice, student_id, data.choice)
    
    # 4. 生成 PDF (記憶體內)
    def generate_pdf_in_memory(name, sid, choice):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 750, f"姓名: {name}")
        p.drawString(100, 730, f"學號: {sid}")
        p.drawString(100, 710, f"選填結果: {choice}")
        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer.getvalue()

    pdf_data = generate_pdf_in_memory(user_info['name'], student_id, choice_name)

    # 5. 背景寄信 (將 PDF bytes 傳入)
    if user_info and user_info.get('email'):
        background_tasks.add_task(
            send_confirmation_email, 
            user_info['email'], 
            user_info['name'], 
            student_id, 
            choice_name,
            submit_time,
            pdf_data # 這裡傳入剛生成的 PDF bytes
        )
    
    return {"status": "success", "message": "選填成功！確認信將發送至您的信箱。"}

@app.get("/admin/all")
async def get_all_students(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="權限不足")
    def db_logic():
        conn = get_db()
        try:
            query = """
                SELECT u.student_id, u.name, u.email, s.choice, s.updated_at 
                FROM users u 
                LEFT JOIN selections s ON u.student_id = s.student_id 
                WHERE u.role = 'student'
            """
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(query)
            return cur.fetchall()
        finally:
            release_db(conn)
    return await asyncio.to_thread(db_logic)

@app.post("/admin/import-students")
async def import_students(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="權限不足")
    
    content = await file.read()
    stream = io.StringIO(content.decode('utf-8'))
    reader = csv.DictReader(stream)
    
    conn = get_db()
    try:
        cur = conn.cursor()
        for row in reader:
            raw_pw = row.get('password', '123456').strip() 
            hashed_pw = get_password_hash(raw_pw) 
            cur.execute("""
                INSERT INTO users (student_id, name, email, password, role) 
                VALUES (%s, %s, %s, %s, 'student') 
                ON CONFLICT (student_id) DO UPDATE SET 
                name = EXCLUDED.name, email = EXCLUDED.email, password = EXCLUDED.password
            """, (row['student_id'], row['name'], row['email'], hashed_pw))
        conn.commit()
        cur.close()
        return {"message": "匯入成功"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"匯入失敗: {str(e)}")
    finally:
        release_db(conn)

# --- 靜態檔案路由 ---
@app.api_route("/", methods=["GET", "HEAD"], response_class=FileResponse)
async def read_index(): 
    return os.path.join(BASE_DIR, "frontend", "index.html")

@app.get("/login", response_class=FileResponse)
async def read_login(): 
    return os.path.join(BASE_DIR, "frontend", "login.html")

@app.get("/choose", response_class=FileResponse)
async def read_choose(): 
    return os.path.join(BASE_DIR, "frontend", "choose.html")

@app.get("/admin", response_class=FileResponse)
async def read_admin(): 
    return os.path.join(BASE_DIR, "frontend", "admin.html")

@app.get("/admin-login", response_class=FileResponse)
async def read_admin_login(): 
    return os.path.join(BASE_DIR, "frontend", "admin-login.html")

# 掛載靜態資料夾 (放在所有路由最後面)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "frontend")), name="static")