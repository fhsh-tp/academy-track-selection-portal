import os
import asyncio
import psycopg2
import psycopg2.extras
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# 導入你的自訂模組
from backend.mailer import send_confirmation_email
from backend.database import init_db, init_db_pool, save_choice, get_db, release_db
from backend.security import verify_password, create_access_token, get_current_user, get_password_hash

# --- 1. 全域設定與排程器 ---
scheduler = AsyncIOScheduler()
DEADLINE = datetime(2026, 3, 10, 23, 59, 59)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- 2. 自動提醒邏輯 (資料庫撈人 + 寄信) ---
async def check_and_send_reminders():
    print("⏰ 觸發自動提醒檢查程序...")
    target_date = datetime(2026, 3, 7).date() # 設定提醒日 (截止前72小時)
    
    # 只在目標當天執行
    if datetime.now().date() == target_date:
        def fetch_unsubmitted_users():
            conn = get_db()
            try:
                cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                # 撈出尚未選填的學生
                cur.execute('''
                    SELECT u.student_id, u.email 
                    FROM users u 
                    LEFT JOIN selections s ON u.student_id = s.student_id 
                    WHERE s.choice IS NULL AND u.role = 'student' AND u.email IS NOT NULL
                ''')
                return cur.fetchall()
            finally:
                release_db(conn)

        users = await asyncio.to_thread(fetch_unsubmitted_users)
        
        for user in users:
            print(f"📧 寄送提醒郵件給: {user['student_id']}")
            await send_confirmation_email(
                recipient=user['email'],
                choice="您尚未完成選填，請儘速處理"
            )
            await asyncio.sleep(1) # 避免寄信過快被擋
    else:
        print(f"⏳ 今天不是提醒日，跳過任務。")

# --- 3. 生命周期管理 (啟動/關閉) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 啟動時執行
    print("🚀 伺服器啟動中...")
    try:
        init_db_pool() 
        init_db()      
        # 設定排程：每天早上 08:00 檢查一次
        scheduler.add_job(check_and_send_reminders, 'cron', hour=8, minute=0)
        scheduler.start()
        print("✅ 資料庫與排程系統準備就緒")
    except Exception as e:
        print(f"⚠️ 啟動失敗: {e}")
    
    yield 
    
    # 關閉時執行
    scheduler.shutdown()
    print("🛑 伺服器關閉中...")

app = FastAPI(lifespan=lifespan)

# --- 中介軟體設定 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic 模型 ---
class LoginData(BaseModel):
    student_id: str
    password: str

class SelectionData(BaseModel):
    choice: int

class PasswordChangeData(BaseModel):
    old_password: str
    new_password: str

# --- API 路由 ---
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
    # ... (前面的檢查邏輯) ...
    
    # 步驟 1: 存檔
    await asyncio.to_thread(save_choice, user['student_id'], data.choice)
    
    # 步驟 2: 從 DB 補撈 Email，因為 JWT 不包含 Email
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
    
    # 步驟 3: 檢查信箱並觸發背景任務
    if email:
        print(f"DEBUG: 準備將郵件背景任務加入排程，寄給: {email}") 
        background_tasks.add_task(send_confirmation_email, email, data.choice)
    else:
        # 如果這裡印出來，代表該學生資料庫裡沒存信箱
        print(f"DEBUG: 該使用者 ({user['student_id']}) 資料庫中沒有 email")
        
    return {"status": "success"}

@app.post("/admin-login")
async def admin_login(data: LoginData):
    # 重用之前的 db_logic，或者直接呼叫邏輯
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
    
    # 這裡額外檢查：如果不是 admin 角色，拒絕登入
    if not user or not verify_password(data.password, user['password']):
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="此入口僅限管理員")
        
    token = create_access_token(data={"sub": user['student_id'], "role": user['role']})
    return {"access_token": token, "role": user['role']}

@app.get("/admin/all")
async def get_all_data(user: dict = Depends(get_current_user)):
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="權限不足")
    def db_logic():
        conn = get_db()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute('''
                SELECT u.student_id, u.name, s.choice, s.updated_at 
                FROM users u LEFT JOIN selections s ON u.student_id = s.student_id
                WHERE u.role = 'student'
            ''')
            res = cur.fetchall()
            cur.close()
            return res
        finally:
            release_db(conn)
    return await asyncio.to_thread(db_logic)

@app.post("/change-password")
async def change_password(data: PasswordChangeData, user: dict = Depends(get_current_user)):
    def db_logic():
        conn = get_db()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT password FROM users WHERE student_id = %s", (user['student_id'],))
            db_user = cur.fetchone()
            if not db_user or not verify_password(data.old_password, db_user['password']):
                return "FAIL"
            new_hash = get_password_hash(data.new_password)
            cur.execute("UPDATE users SET password = %s WHERE student_id = %s", (new_hash, user['student_id']))
            conn.commit()
            return "SUCCESS"
        finally:
            release_db(conn)
    result = await asyncio.to_thread(db_logic)
    if result == "FAIL": raise HTTPException(status_code=400, detail="舊密碼錯誤")
    return {"message": "密碼修改成功"}

# --- 靜態檔案路由 ---
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