from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .core.database import engine, Base
from .routers import auth_router, projects_router, stages_router, files_router, notes_router
from .core.config import settings
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Architecture Project Management API",
    description="API for managing architecture projects",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

upload_dir = settings.UPLOAD_DIR
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(stages_router)
app.include_router(files_router)
app.include_router(notes_router)


@app.get("/")
def root():
    return {"message": "Architecture Project Management API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
