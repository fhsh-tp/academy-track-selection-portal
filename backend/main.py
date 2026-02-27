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
from backend.security import verify_password, create_access_token, get_current_user

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

# --- 靜態檔案路由 (一定要放在最後) ---

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(BASE_DIR, "frontend", "index.html"))

@app.get("/{file_name}")
async def serve_file(file_name: str):
    return FileResponse(os.path.join(BASE_DIR, "frontend", file_name))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "frontend")), name="static")