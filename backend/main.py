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

print("--- 系統啟動偵錯 ---")
print(f"DEBUG: RESEND_API_KEY 是否存在: {os.environ.get('RESEND_API_KEY') is not None}")
print(f"DEBUG: ADMIN_PASSWORD 是否存在: {os.environ.get('ADMIN_PASSWORD') is not None}")
print("-------------------")

# 導入你的自訂模組
from backend.mailer import send_confirmation_email
from backend.database import init_db, init_db_pool, save_choice, get_db, release_db
from backend.security import verify_password, create_access_token, get_current_user, get_password_hash

# --- 1. 全域設定 ---
scheduler = AsyncIOScheduler()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- 2. 生命周期管理 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    init_db_pool()
    init_db()
    yield
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

# --- 3. 模型與路由 ---
class LoginData(BaseModel):
    student_id: str
    password: str

class SelectionData(BaseModel):
    choice: int

class PasswordChangeData(BaseModel):
    old_password: str
    new_password: str

@app.get("/ping")
async def ping(): return {"status": "ok"}

@app.post("/login")
async def login(data: LoginData):
    def db_logic():
        conn = get_db()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT * FROM users WHERE student_id = %s", (data.student_id,))
            user = cur.fetchone()
            cur.close()
            return user
        finally:
            release_db(conn)
    
    user = await asyncio.to_thread(db_logic)
    if not user or not verify_password(data.password, user['password']):
        raise HTTPException(status_code=401, detail="學號或密碼錯誤")
    
    token = create_access_token(data={"sub": user['student_id'], "role": user['role']})
    return {"access_token": token, "role": user['role']}

@app.post("/submit")
async def submit(data: SelectionData, background_tasks: BackgroundTasks, user: dict = Depends(get_current_user)):
    # 存檔至 selections 表
    await asyncio.to_thread(save_choice, user['student_id'], data.choice)
    
    # 取得 Email 寄確認信
    def get_user_email():
        conn = get_db()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT email FROM users WHERE student_id = %s", (user['student_id'],))
            row = cur.fetchone()
            return row['email'] if row else None
        finally:
            release_db(conn)

    email = await asyncio.to_thread(get_user_email)
    if email:
        background_tasks.add_task(send_confirmation_email, email, data.choice)
        
    return {"status": "success"}

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
            sid, name, email = row['student_id'], row['name'], row['email']
            default_pw = get_password_hash("default_password") 
            
            # 關鍵修正：確保 ON CONFLICT 時也更新 password
            cur.execute("""
                INSERT INTO users (student_id, name, email, password, role)
                VALUES (%s, %s, %s, %s, 'student')
                ON CONFLICT (student_id) 
                DO UPDATE SET 
                    name = EXCLUDED.name, 
                    email = EXCLUDED.email,
                    password = EXCLUDED.password
            """, (sid, name, email, default_pw))
        
        conn.commit()
        cur.close()
        return {"message": "匯入成功"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"匯入失敗: {str(e)}")
    finally:
        release_db(conn)

# --- 靜態檔案路由 (其餘 API 路由略，保持你原本的結構即可) ---
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