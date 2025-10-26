import os
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException, Header
from database import SessionLocal, User

JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"

def admin_required_optional(authorization: str = Header(None)):
    from database import SessionLocal, User
    db = SessionLocal()
    user_count = db.query(User).count()
    db.close()
    if user_count == 0:
        # Allow first user to be created and make him admin
        return True
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required")
        # if an admin has been created then authorization is required

def create_token(username: str, is_admin: bool):
    payload = {
        "sub": username,
        "admin": is_admin,
        "exp": datetime.now(timezone(timedelta(hours=1))) + timedelta(hours=2)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(authorization: str = Header(...)):
    """Extract user from Authorization header"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    return payload

def admin_required(user=Depends(get_current_user)):
    """Ensure the user is an admin"""
    if not user.get("admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user