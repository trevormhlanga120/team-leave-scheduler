from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models, database
from .routers import employees, leave
from .seed_data import seed

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Team Leave Scheduler")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employees.router)
app.include_router(leave.router)


@app.on_event("startup")
def on_startup():
    db = database.SessionLocal()
    seed(db)
    db.close()