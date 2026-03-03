import os
import bcrypt
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

# --- 設定 ---
load_dotenv()
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- 核心：使用 Bcrypt 加密與驗證 ---
def get_password_hash(password: str) -> str:
    """將明文轉為 Bcrypt 雜湊"""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        pwd_bytes = plain_password.encode('utf-8')
        hash_bytes = hashed_password.encode('utf-8')
        result = bcrypt.checkpw(pwd_bytes, hash_bytes)
        
        if not result:
            print("DEBUG: bcrypt.checkpw 回傳了 False")
            
        return result
    except Exception as e:
        print(f"DEBUG: 驗證時發生例外: {e}")
        return False

# --- JWT 驗證部分 ---
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        student_id: str = payload.get("sub")
        role: str = payload.get("role")
        if student_id is None:
            raise HTTPException(status_code=401, detail="無效驗證")
        return {"student_id": student_id, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="驗證失敗")