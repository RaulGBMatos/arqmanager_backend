from sqlalchemy import Column, String, ForeignKey, Integer
from .base import BaseModel


class ProjectFile(BaseModel):
    __tablename__ = "project_files"
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)
