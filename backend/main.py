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

# 導入你的自訂模組
from backend.mailer import send_confirmation_email
from backend.database import init_db, init_db_pool, save_choice, get_db, release_db
from backend.security import verify_password, create_access_token, get_current_user, get_password_hash

# --- 1. 全域設定 ---
# 從環境變數讀取截止日期，若未設定則預設為 2026-04-30
DEADLINE = os.environ.get("DEADLINE_DATE", "2026-04-30 23:59:59")
deadline_dt = datetime.strptime(DEADLINE, "%Y-%m-%d %H:%M:%S")

scheduler = AsyncIOScheduler()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- 2. 生命周期管理 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 系統啟動中...")
    scheduler.start()
    init_db_pool()
    init_db()
    yield
    print("🛑 系統關閉中...")
    try:
        if scheduler.running:
            scheduler.shutdown()
    except Exception:
        pass

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. 資料模型 ---
class LoginData(BaseModel):
    student_id: str
    password: str

class SelectionData(BaseModel):
    choice: int

# --- 4. API 路由 ---

@app.get("/ping")
async def ping(): 
    return {"status": "ok"}

@app.post("/login")
async def login(data: LoginData):
    def db_logic():
        conn = get_db()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT * FROM users WHERE student_id = %s", (data.student_id,))
            user = cur.fetchone()
            return user
        finally:
            release_db(conn)
    
    user = await asyncio.to_thread(db_logic)
    
    if not user:
        raise HTTPException(status_code=401, detail="學號錯誤")
    
    # 驗證密碼
    if not verify_password(data.password, user['password']):
        raise HTTPException(status_code=401, detail="密碼錯誤")
    
    # 簽發 Token，sub 存放學號
    token = create_access_token(data={"sub": user['student_id'], "role": user['role']})
    return {"access_token": token, "role": user['role']}

@app.post("/submit") 
async def submit_choice(
    data: SelectionData, 
    background_tasks: BackgroundTasks, 
    current_user: dict = Depends(get_current_user)
):
    # 1. 時間檢查
    if datetime.now() > deadline_dt:
        raise HTTPException(status_code=403, detail="選填期限已過")
    
    # 修正點：從 current_user 獲取 'student_id' 而非 'sub'
    student_id = current_user['student_id'] 
    
    # 2. 存檔
    await asyncio.to_thread(save_choice, student_id, data.choice)
    
    # 3. 寄送確認信
    def get_user_email():
        conn = get_db()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            # 使用修正後的 student_id
            cur.execute("SELECT email FROM users WHERE student_id = %s", (student_id,))
            row = cur.fetchone()
            return row['email'] if row else None
        finally:
            release_db(conn)

    email = await asyncio.to_thread(get_user_email)
    if email:
        background_tasks.add_task(send_confirmation_email, email, data.choice)
        
    return {"status": "success"}

@app.get("/admin/all")
async def get_all_students(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="權限不足")
        
    def db_logic():
        conn = get_db()
        try:
            # 修正：使用 LEFT JOIN 串接 users 與 selections 表
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
            # 修正：加上 .strip() 防止隱形空白造成的密碼錯誤
            raw_pw = row.get('password', '123456').strip() 
            hashed_pw = get_password_hash(raw_pw) 
            
            cur.execute("""
                INSERT INTO users (student_id, name, email, password, role)
                VALUES (%s, %s, %s, %s, 'student')
                ON CONFLICT (student_id) 
                DO UPDATE SET 
                    name = EXCLUDED.name, 
                    email = EXCLUDED.email,
                    password = EXCLUDED.password
            """, (row['student_id'], row['name'], row['email'], hashed_pw))
        
        conn.commit()
        cur.close()
        return {"message": "匯入成功"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"匯入失敗: {str(e)}")
    finally:
        release_db(conn)

# --- 靜態路由 ---
@app.api_route("/", methods=["GET", "HEAD"])
async def read_index(): return FileResponse(os.path.join(BASE_DIR, "frontend", "index.html"))
@app.get("/login")
async def read_login(): return FileResponse(os.path.join(BASE_DIR, "frontend", "login.html"))
@app.get("/choose")
async def read_choose(): return FileResponse(os.path.join(BASE_DIR, "frontend", "choose.html"))
@app.get("/admin")
async def read_admin(): return FileResponse(os.path.join(BASE_DIR, "frontend", "admin.html"))
@app.get("/admin-login")
async def read_admin_login(): return FileResponse(os.path.join(BASE_DIR, "frontend", "admin-login.html"))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "frontend")), name="static")