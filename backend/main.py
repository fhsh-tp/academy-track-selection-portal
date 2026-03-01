import os
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import psycopg2
import psycopg2.extras
from backend.mailer import send_confirmation_email

# 導入你的後端模組
from backend.database import init_db, init_db_pool, save_choice, get_db, release_db
from backend.security import verify_password, create_access_token, get_current_user, get_password_hash

# --- 啟動與關閉的生命週期管理 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. 伺服器啟動時：初始化資料庫連線池與表格
    print("🚀 伺服器啟動中...")
    try:
        init_db_pool() # 建立連線池 (不會在 import 時發生，現在才執行)
        init_db()      # 初始化表格
        print("✅ 資料庫系統準備就緒")
    except Exception as e:
        print(f"⚠️ 資料庫啟動失敗: {e}")
    
    yield  # 應用程式開始運行
    
    # 2. 伺服器關閉時 (若有需要)
    print("🛑 伺服器關閉中...")

app = FastAPI(lifespan=lifespan)

# --- 設定 ---
DEADLINE = datetime(2026, 3, 10, 23, 59, 59)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
async def submit(
    data: SelectionData, 
    background_tasks: BackgroundTasks,  # 1. 注入 BackgroundTasks
    user: dict = Depends(get_current_user)
):
    if datetime.now() > DEADLINE:
        raise HTTPException(status_code=403, detail="選填時間已截止")
    if data.choice not in [1, 2, 3, 4]:
        raise HTTPException(status_code=400, detail="請選擇有效的類組")
    
    # 執行資料庫寫入
    await asyncio.to_thread(save_choice, user['student_id'], data.choice)
    
    # 2. 將寄信任務加入排程
    # 假設你的 user 物件裡有 email 欄位
    user_email = user.get('email') 
    
    # 如果資料庫裡找不到 email，這裡給一個備用邏輯或檢查
    if user_email:
        background_tasks.add_task(
            send_confirmation_email, 
            recipient=user_email, 
            choice=data.choice
        )
    else:
        print(f"⚠️ 使用者 {user['student_id']} 沒有 Email，跳過寄信流程")
        
    return {"status": "success"}

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
                cur.close()
                return "FAIL"
            
            new_hash = get_password_hash(data.new_password)
            cur.execute("UPDATE users SET password = %s WHERE student_id = %s", (new_hash, user['student_id']))
            conn.commit()
            cur.close()
            return "SUCCESS"
        finally:
            release_db(conn)

    result = await asyncio.to_thread(db_logic)
    if result == "FAIL":
        raise HTTPException(status_code=400, detail="舊密碼錯誤")
    return {"message": "密碼修改成功"}

# --- 靜態檔案 ---
@app.api_route("/", methods=["GET", "HEAD"])
async def read_index(): return FileResponse(os.path.join(BASE_DIR, "frontend", "index.html"))
@app.get("/login")
async def read_login(): return FileResponse(os.path.join(BASE_DIR, "frontend", "login.html"))
@app.get("/choose")
async def read_choose(): return FileResponse(os.path.join(BASE_DIR, "frontend", "choose.html"))
@app.get("/admin")
async def read_admin(): return FileResponse(os.path.join(BASE_DIR, "frontend", "admin.html"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "frontend")), name="static")