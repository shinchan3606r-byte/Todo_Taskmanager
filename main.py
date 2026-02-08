from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models
from schemas import TodoUpdate, TodoCreate

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency for db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Post create TODO
@app.post("/todos/", response_model=TodoUpdate)
def create(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = models.Todo(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

# Get all TODOs
@app.get("/todos/", response_model=list[TodoUpdate])
def read_todos(db: Session = Depends(get_db)):
    todos = db.query(models.Todo).all()
    return todos

# Get TODO by ID
@app.get("/todos/{todo_id}", response_model=TodoUpdate)
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

# Put update TODO
@app.put("/todos/{todo_id}", response_model=TodoUpdate)
def update_todo(todo_id: int, updated: TodoCreate, db: Session = Depends(get_db)):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    for key, value in updated.dict().items():
        setattr(db_todo, key, value)
    db.commit()
    db.refresh(db_todo)
    return db_todo

# Delete todo by ID
@app.delete("/todos/{todo_id}") 
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(db_todo)
    db.commit()
    return {"detail": "Todo deleted"}
