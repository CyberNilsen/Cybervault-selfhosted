from pydantic import BaseModel

class RegisterModel(BaseModel):
    username: str
    password: str

class LoginModel(BaseModel):
    username: str
    password: str

class PasswordModel(BaseModel):
    name: str
    username: str
    password: str