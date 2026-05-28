from sqlalchemy import Column, Text, ForeignKey, Integer
from .base import BaseModel


class Note(BaseModel):
    __tablename__ = "notes"
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    content = Column(Text, nullable=False)
