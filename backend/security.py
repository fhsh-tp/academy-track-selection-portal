import os
import bcrypt
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# 設定
SECRET_KEY = os.environ.get("SECRET_KEY", "your-very-secret-key-12345")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# 使用 bcrypt 直接加密
def get_password_hash(password: str) -> str:
    # bcrypt 需要 bytes，所以要編碼
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

# 使用 bcrypt 直接驗證
def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hash_bytes)

# JWT 部分保持不變
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=1)
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