from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", Fernet.generate_key().decode())

app = FastAPI(title="CyberVault API")

# In-memory storage (Gonna fix later)
users = {}
passwords = {}

# Encryption key
cipher = Fernet(SECRET_KEY.encode())

# Models
class RegisterModel(BaseModel):
    username: str
    password: str

class LoginModel(BaseModel):
    username: str
    password: str

class PasswordModel(BaseModel):
    name: str
    password: str

# Routes
@app.post("/register")
def register(user: RegisterModel):
    if user.username in users:
        raise HTTPException(status_code=400, detail="User already exists")
    users[user.username] = user.password
    passwords[user.username] = []
    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: LoginModel):
    if user.username not in users or users[user.username] != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful"}

@app.post("/passwords/{username}")
def add_password(username: str, entry: PasswordModel):
    if username not in users:
        raise HTTPException(status_code=401, detail="Invalid user")
    encrypted = cipher.encrypt(entry.password.encode()).decode()
    passwords[username].append({"name": entry.name, "password": encrypted})
    return {"message": "Password stored"}

@app.get("/passwords/{username}")
def get_passwords(username: str):
    if username not in users:
        raise HTTPException(status_code=401, detail="Invalid user")
    decrypted = [
        {"name": p["name"], "password": cipher.decrypt(p["password"].encode()).decode()}
        for p in passwords[username]
    ]
    return {"passwords": decrypted}
