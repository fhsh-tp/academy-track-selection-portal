import os
import psycopg2
import psycopg2.extras
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# 確保這些模組在你的 backend 資料夾下
from backend.database import init_db, save_choice, get_db
from backend.security import verify_password, create_access_token, get_current_user, get_password_hash

app = FastAPI()

# 截止日期
DEADLINE = datetime(2026, 3, 10, 23, 59, 59)

#讀取主目錄
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginData(BaseModel):
    student_id: str
    password: str

class SelectionData(BaseModel):
    choice: int

#管理員改密碼
class PasswordChangeData(BaseModel):
    old_password: str
    new_password: str

@app.on_event("startup")
async def startup():
    init_db()

# --- API 路由 ---

@app.post("/login")
async def login(data: LoginData):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM users WHERE student_id = %s", (data.student_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user or not verify_password(data.password, user['password']):
        raise HTTPException(status_code=401, detail="學號或密碼錯誤")
    
    token = create_access_token(data={"sub": user['student_id'], "role": user['role']})
    return {"access_token": token, "role": user['role']}

@app.post("/submit")
async def submit(data: SelectionData, user: dict = Depends(get_current_user)):
    if datetime.now() > DEADLINE:
        raise HTTPException(status_code=403, detail="選填時間已截止")
    if data.choice not in [1, 2, 3, 4]:
        raise HTTPException(status_code=400, detail="請選擇有效的類組")
    
    save_choice(user['student_id'], data.choice)
    return {"status": "success"}

@app.get("/admin/all")
async def get_all_data(user: dict = Depends(get_current_user)):
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="權限不足")
    
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('''
        SELECT u.student_id, u.name, s.choice, s.updated_at 
        FROM users u LEFT JOIN selections s ON u.student_id = s.student_id
        WHERE u.role = 'student'
    ''')
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res

@app.get("/admin-login")
async def read_admin_login():
    return FileResponse(os.path.join(BASE_DIR, "frontend", "admin-login.html"))

@app.post("/change-password")
async def change_password(data: PasswordChangeData, user: dict = Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # 1. 取得現有使用者資料
    cur.execute("SELECT password FROM users WHERE student_id = %s", (user['student_id'],))
    db_user = cur.fetchone()
    
    # 2. 驗證舊密碼是否正確
    if not db_user or not verify_password(data.old_password, db_user['password']):
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="舊密碼錯誤")
    
    # 3. 加密新密碼並更新
    new_hash = get_password_hash(data.new_password)
    cur.execute("UPDATE users SET password = %s WHERE student_id = %s", (new_hash, user['student_id']))
    
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "密碼修改成功"}

# --- 靜態檔案路由 (一定要放在最後) ---

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(BASE_DIR, "frontend", "index.html"))

@app.get("/login")
async def read_login():
    return FileResponse(os.path.join(BASE_DIR, "frontend", "login.html"))

@app.get("/choose")
async def read_choose():
    return FileResponse(os.path.join(BASE_DIR, "frontend", "choose.html"))

@app.get("/admin")
async def read_admin():
    return FileResponse(os.path.join(BASE_DIR, "frontend", "admin.html"))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "frontend")), name="static")