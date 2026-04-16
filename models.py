from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    duration = Column(Integer)
    priority = Column(String)
    category = Column(String)
    status = Column(String)
    progress = Column(String, default="0%")
    user_id = Column(Integer, ForeignKey("users.id"))  # ✅ ADD THIS