from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ProjectFileResponse(BaseModel):
    id: int
    project_id: int
    file_name: str
    file_url: str
    file_type: str
    file_size: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
