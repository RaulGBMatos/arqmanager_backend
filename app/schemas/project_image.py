from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ProjectImageCreate(BaseModel):
    caption: Optional[str] = None


class ProjectImageResponse(BaseModel):
    id: int
    project_id: int
    image_url: str
    caption: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
