from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal, User, PasswordEntry
from models import RegisterModel, LoginModel, PasswordModel
from utils import encrypt_password, decrypt_password
from auth import create_token, admin_required_optional, get_current_user

app = FastAPI()
Base.metadata.create_all(bind=engine)

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# User routes
@app.post("/create-user")
def create_user(user: RegisterModel, token=Depends(admin_required_optional)):
    db = SessionLocal()
    is_first_user = db.query(User).count() == 0
    new_user = User(
        username=user.username,
        password=encrypt_password(user.password),
        is_admin=is_first_user
    )
    db.add(new_user)
    db.commit()
    db.close()
    return {"message": f"User {user.username} created", "is_admin": is_first_user}

@app.post("/login")
def login(user: LoginModel, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if decrypt_password(db_user.password) != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(db_user.username, db_user.is_admin)
    return {"access_token": token}

# Password routes
@app.post("/passwords")
def add_password(entry: PasswordModel, user=Depends(get_current_user), db: Session = Depends(get_db)):
    db_entry = PasswordEntry(
        name=entry.name,
        username=entry.username,
        password=encrypt_password(entry.password),
        owner_id=user.get("sub")
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return {"message": "Password saved"}

@app.get("/passwords")
def get_passwords(user=Depends(get_current_user), db: Session = Depends(get_db)):
    entries = db.query(PasswordEntry).filter(PasswordEntry.owner_id == user.get("sub")).all()
    result = []
    for e in entries:
        result.append({
            "name": e.name,
            "username": e.username,
            "password": decrypt_password(e.password)
        })
    return result