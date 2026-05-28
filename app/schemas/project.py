from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from ..models.project import ProjectStatus


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    client_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    deadline_date: Optional[date] = None
    status: ProjectStatus = ProjectStatus.PLANNING


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    client_name: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[ProjectStatus] = None


class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    cover_image_url: Optional[str] = None
    progress: float = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectListResponse(ProjectResponse):
    stages_count: int = 0
    completed_stages_count: int = 0
