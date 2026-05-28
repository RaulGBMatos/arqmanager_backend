from sqlalchemy import Column, String, Text, Date, ForeignKey, Integer, Enum
import enum
from .base import BaseModel


class StageStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Stage(BaseModel):
    __tablename__ = "stages"
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(StageStatus), default=StageStatus.PENDING, nullable=False)
    expected_date = Column(Date, nullable=True)
    completed_at = Column(Date, nullable=True)
    responsible = Column(String, nullable=True)
    order_index = Column(Integer, default=0, nullable=False)
