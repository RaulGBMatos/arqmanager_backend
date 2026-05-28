from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from ..core.deps import get_current_user
from ..models.user import User
from ..models.project import Project
from ..models.stage import Stage
from ..schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse

router = APIRouter(prefix="/projects", tags=["projects"])


def calculate_project_progress(project_id: int, db: Session) -> float:
    stages = db.query(Stage).filter(Stage.project_id == project_id).all()
    if not stages:
        return 0.0
    completed = sum(1 for stage in stages if stage.status == "completed")
    return round((completed / len(stages)) * 100, 2)


@router.get("", response_model=List[ProjectListResponse])
def get_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    search: Optional[str] = None,
    status_filter: Optional[str] = None
):
    query = db.query(Project).filter(Project.user_id == current_user.id)
    
    if search:
        query = query.filter(
            (Project.name.ilike(f"%{search}%")) |
            (Project.client_name.ilike(f"%{search}%"))
        )
    
    if status_filter:
        query = query.filter(Project.status == status_filter)
    
    projects = query.order_by(Project.created_at.desc()).all()
    
    result = []
    for project in projects:
        stages = db.query(Stage).filter(Stage.project_id == project.id).all()
        completed_stages = sum(1 for s in stages if s.status == "completed")
        progress = calculate_project_progress(project.id, db)
        
        project_dict = {
            "id": project.id,
            "user_id": project.user_id,
            "name": project.name,
            "client_name": project.client_name,
            "description": project.description,
            "location": project.location,
            "start_date": project.start_date,
            "deadline_date": project.deadline_date,
            "status": project.status,
            "cover_image_url": project.cover_image_url,
            "progress": progress,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "stages_count": len(stages),
            "completed_stages_count": completed_stages
        }
        result.append(ProjectListResponse(**project_dict))
    
    return result


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_project = Project(**project_data.model_dump(), user_id=current_user.id)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    new_project.progress = 0.0
    return new_project


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
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
    
    project.progress = calculate_project_progress(project_id, db)
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
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
    
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    project.progress = calculate_project_progress(project_id, db)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
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
    
    db.delete(project)
    db.commit()
    return None
