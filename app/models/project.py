from sqlalchemy import Column, String, Text, Date, ForeignKey, Integer, Enum
import enum
from .base import BaseModel


class ProjectStatus(str, enum.Enum):
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Project(BaseModel):
    __tablename__ = "projects"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    client_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    deadline_date = Column(Date, nullable=True)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNING, nullable=False)
    cover_image_url = Column(String, nullable=True)
