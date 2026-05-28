from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
from ..core.database import get_db
from ..core.deps import get_current_user
from ..core.config import settings
from ..models.user import User
from ..models.project import Project
from ..models.project_file import ProjectFile
from ..models.project_image import ProjectImage
from ..schemas.project_file import ProjectFileResponse
from ..schemas.project_image import ProjectImageCreate, ProjectImageResponse

router = APIRouter(prefix="/files", tags=["files"])


def get_file_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[1].lower() if "." in filename else ""


def is_image_file(filename: str) -> bool:
    image_extensions = {"jpg", "jpeg", "png", "gif", "webp", "svg"}
    return get_file_extension(filename) in image_extensions


def ensure_upload_dir():
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "covers"), exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "images"), exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "files"), exist_ok=True)


@router.post("/projects/{project_id}/upload-cover", response_model=dict)
async def upload_cover(
    project_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if not is_image_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    ensure_upload_dir()
    
    file_extension = get_file_extension(file.filename)
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, "covers", unique_filename)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    file_url = f"/uploads/covers/{unique_filename}"
    project.cover_image_url = file_url
    db.commit()
    
    return {"url": file_url}


@router.post("/projects/{project_id}/images", response_model=ProjectImageResponse)
async def upload_image(
    project_id: int,
    file: UploadFile = File(...),
    caption: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if not is_image_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    ensure_upload_dir()
    
    file_extension = get_file_extension(file.filename)
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, "images", unique_filename)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    file_url = f"/uploads/images/{unique_filename}"
    
    new_image = ProjectImage(
        project_id=project_id,
        image_url=file_url,
        caption=caption
    )
    db.add(new_image)
    db.commit()
    db.refresh(new_image)
    
    return new_image


@router.post("/projects/{project_id}/files", response_model=ProjectFileResponse)
async def upload_file(
    project_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    ensure_upload_dir()
    
    file_extension = get_file_extension(file.filename)
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, "files", unique_filename)
    
    content = await file.read()
    file_size = len(content)
    
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    file_url = f"/uploads/files/{unique_filename}"
    
    new_file = ProjectFile(
        project_id=project_id,
        file_name=file.filename,
        file_url=file_url,
        file_type=file_extension,
        file_size=file_size
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    
    return new_file


@router.get("/projects/{project_id}/images", response_model=List[ProjectImageResponse])
def get_project_images(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    images = db.query(ProjectImage).filter(
        ProjectImage.project_id == project_id
    ).order_by(ProjectImage.created_at.desc()).all()
    
    return images


@router.get("/projects/{project_id}/files", response_model=List[ProjectFileResponse])
def get_project_files(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    files = db.query(ProjectFile).filter(
        ProjectFile.project_id == project_id
    ).order_by(ProjectFile.created_at.desc()).all()
    
    return files


@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    image = db.query(ProjectImage).join(Project).filter(
        ProjectImage.id == image_id,
        Project.user_id == current_user.id
    ).first()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    db.delete(image)
    db.commit()
    return None


@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    file = db.query(ProjectFile).join(Project).filter(
        ProjectFile.id == file_id,
        Project.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    db.delete(file)
    db.commit()
    return None
