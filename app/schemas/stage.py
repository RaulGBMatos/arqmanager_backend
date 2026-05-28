from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from ..models.stage import StageStatus


class StageBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: StageStatus = StageStatus.PENDING
    expected_date: Optional[date] = None
    responsible: Optional[str] = None


class StageCreate(StageBase):
    order_index: int = 0


class StageUpdate(StageBase):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[StageStatus] = None
    order_index: Optional[int] = None


class StageResponse(StageBase):
    id: int
    project_id: int
    completed_at: Optional[date] = None
    order_index: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
