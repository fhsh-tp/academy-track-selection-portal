import os
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from werkzeug.security import generate_password_hash, check_password_hash

# --- 設定 ---
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- 核心：密碼加密與驗證 ---
# 使用 werkzeug 處理，這比手動用 bcrypt 更安全且不容易出錯
def get_password_hash(password: str) -> str:
    """將明文轉為雜湊，存入資料庫時使用"""
    return generate_password_hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """驗證明文密碼是否與資料庫雜湊相符"""
    return check_password_hash(hashed_password, plain_password)

# --- JWT 驗證部分 ---
def create_access_token(data: dict):
    to_encode = data.copy()
    # 使用 timezone.utc 避免時區警告
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