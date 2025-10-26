import os
from sqlalchemy import create_engine, Column, String, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Determine DB folder and make sure it exists
db_path = os.getenv("DATABASE_URL", "sqlite:///./data/cybervault.db")
# Extract relative path from sqlite URL
if db_path.startswith("sqlite:///"):
    folder = os.path.dirname(db_path.replace("sqlite:///", ""))
    os.makedirs(folder, exist_ok=True)

engine = create_engine(db_path, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    is_admin = Column(Boolean, default=False)

class PasswordEntry(Base):
    __tablename__ = "passwords"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    username = Column(String)
    password = Column(String)
    owner_id = Column(Integer)

Base.metadata.create_all(bind=engine)
