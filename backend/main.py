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
    
    # --- 這裡加入偵錯邏輯 ---
    if not user:
        print(f"DEBUG: 找不到學號 {data.student_id}")
        raise HTTPException(status_code=401, detail="學號錯誤")
    
    is_valid = verify_password(data.password, user['password'])
    if not is_valid:
        print(f"DEBUG: 密碼比對失敗，學號: {data.student_id}")
        raise HTTPException(status_code=401, detail="密碼錯誤")
    # -----------------------
    
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

@app.post("/admin-login")
async def admin_login(data: LoginData):
    # 執行管理員身分驗證
    def db_logic():
        conn = get_db()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            # 關鍵：這裡加上 AND role = 'admin'，確保只有管理員能從此處登入
            cur.execute("SELECT * FROM users WHERE student_id = %s AND role = 'admin'", (data.student_id,))
            user = cur.fetchone()
            cur.close()
            return user
        finally:
            release_db(conn)
    
    # 呼叫資料庫邏輯
    user = await asyncio.to_thread(db_logic)
    
    # 檢查帳號是否存在，以及密碼是否正確
    if not user or not verify_password(data.password, user['password']):
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    
    # 生成 Token
    token = create_access_token(data={"sub": user['student_id'], "role": user['role']})
    return {"access_token": token, "role": user['role']}

@app.get("/admin/all")
async def get_all_students(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="權限不足")
        
    def db_logic():
        conn = get_db()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT student_id, name, email FROM users WHERE role = 'student'")
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
            # 修正點：從 CSV 讀取 password 欄位
            raw_pw = row.get('password', 'default_password') 
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
        return {"message": "匯入成功，密碼已依 CSV 設定"}
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