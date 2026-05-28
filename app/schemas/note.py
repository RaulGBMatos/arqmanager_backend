from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class NoteBase(BaseModel):
    content: str = Field(..., min_length=1)


class NoteCreate(NoteBase):
    pass


class NoteUpdate(NoteBase):
    content: Optional[str] = Field(None, min_length=1)


class NoteResponse(NoteBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
