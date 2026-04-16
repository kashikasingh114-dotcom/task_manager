from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi import Query
from database import engine, Base, SessionLocal
from models import User, Task
from ai_logic import analyze_task

app = FastAPI()

# ------------------------
# CORS
# ------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# ------------------------
# DB SESSION
# ------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------------
# MODELS
# ------------------------
class UserRequest(BaseModel):
    username: str
    password: str

class TaskRequest(BaseModel):
    title: str
    duration: int
    user_id: int

class ProgressUpdate(BaseModel):
    progress: str   # ✅ FIXED (was query param before)

# ------------------------
# SIGNUP
# ------------------------
@app.post("/signup")
def signup(data: UserRequest, db: Session = Depends(get_db)):

    existing = db.query(User).filter(User.username == data.username).first()

    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        username=data.username.strip(),
        password=data.password.strip()
    )

    db.add(user)
    db.commit()

    return {"message": "User created"}

# ------------------------
# LOGIN
# ------------------------
@app.post("/login")
def login(data: UserRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(
        User.username == data.username.strip(),
        User.password == data.password.strip()
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "message": "Login success",
        "user_id": user.id
    }

# ------------------------
# ADD TASK
# ------------------------
@app.post("/add-task")
def add_task(data: TaskRequest, db: Session = Depends(get_db)):

    title = data.title.strip()

    if not title:
        raise HTTPException(status_code=400, detail="Task cannot be empty")

    if data.duration <= 0:
        raise HTTPException(status_code=400, detail="Duration must be > 0")

    ai = analyze_task(title)

    task = Task(
        title=title,
        duration=data.duration,
        priority=ai["priority"],
        category=ai["category"],
        status="pending",
        user_id=data.user_id
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "task": task.title,
        "duration": task.duration,
        "priority": task.priority,
        "category": task.category
    }

# ------------------------
# GET TASKS
# ------------------------
@app.get("/tasks/{user_id}")
def get_tasks(user_id: int, db: Session = Depends(get_db)):
    tasks= db.query(Task).filter(Task.user_id == user_id).all()
    return [
        {
            "id": t.id,
            "title": t.title,
            "duration": t.duration,
            "priority": t.priority,
            "category": t.category,
            "status": t.status
        }
        for t in tasks
    ]
# ------------------------
# MARK DONE
# ------------------------
from fastapi import Body

@app.put("/task-progress/{task_id}")
def progress(
    task_id: int,
    data: dict = Body(...),   # ✅ FORCE JSON BODY
    db: Session = Depends(get_db)
):
    print("RAW DATA:", data)  # 👈 debug

    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Not found")

    task.progress = str(data.get("progress", 0))  # ✅ safe
    db.commit()

    return {"message": "saved"}

# ------------------------
# DELETE
# ------------------------
@app.delete("/task/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):

    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Not found")

    db.delete(task)
    db.commit()

    return {"message": "deleted"}

# ------------------------
# PROGRESS (FIXED)
# ------------------------
@app.put("/task-progress/{task_id}")
def progress(task_id: int, data: ProgressUpdate, db: Session = Depends(get_db)):

    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Not found")

    task.progress = data.progress
    db.commit()

    return {"message": "saved"}