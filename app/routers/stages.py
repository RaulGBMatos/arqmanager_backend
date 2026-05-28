from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from ..core.database import get_db
from ..core.deps import get_current_user
from ..models.user import User
from ..models.project import Project
from ..models.stage import Stage
from ..schemas.stage import StageCreate, StageUpdate, StageResponse

router = APIRouter(prefix="/stages", tags=["stages"])


@router.get("/project/{project_id}", response_model=List[StageResponse])
def get_project_stages(
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
    
    stages = db.query(Stage).filter(
        Stage.project_id == project_id
    ).order_by(Stage.order_index).all()
    
    return stages


@router.post("/project/{project_id}", response_model=StageResponse, status_code=status.HTTP_201_CREATED)
def create_stage(
    project_id: int,
    stage_data: StageCreate,
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
    
    new_stage = Stage(**stage_data.model_dump(), project_id=project_id)
    db.add(new_stage)
    db.commit()
    db.refresh(new_stage)
    return new_stage


@router.put("/{stage_id}", response_model=StageResponse)
def update_stage(
    stage_id: int,
    stage_data: StageUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    stage = db.query(Stage).join(Project).filter(
        Stage.id == stage_id,
        Project.user_id == current_user.id
    ).first()
    
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
    
    update_data = stage_data.model_dump(exclude_unset=True)
    
    if update_data.get("status") == "completed" and not stage.completed_at:
        update_data["completed_at"] = date.today()
    elif update_data.get("status") != "completed":
        update_data["completed_at"] = None
    
    for field, value in update_data.items():
        setattr(stage, field, value)
    
    db.commit()
    db.refresh(stage)
    return stage


@router.patch("/{stage_id}/complete", response_model=StageResponse)
def complete_stage(
    stage_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    stage = db.query(Stage).join(Project).filter(
        Stage.id == stage_id,
        Project.user_id == current_user.id
    ).first()
    
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
    
    stage.status = "completed"
    stage.completed_at = date.today()
    db.commit()
    db.refresh(stage)
    return stage


@router.delete("/{stage_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stage(
    stage_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    stage = db.query(Stage).join(Project).filter(
        Stage.id == stage_id,
        Project.user_id == current_user.id
    ).first()
    
    if not stage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )
    
    db.delete(stage)
    db.commit()
    return None
