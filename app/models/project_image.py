from sqlalchemy import Column, String, ForeignKey, Text, Integer
from .base import BaseModel


class ProjectImage(BaseModel):
    __tablename__ = "project_images"
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    image_url = Column(String, nullable=False)
    caption = Column(Text, nullable=True)
