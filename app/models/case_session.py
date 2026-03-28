from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel

class CaseStudySession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    case_study_id: int = Field(foreign_key="casestudy.id")
    
    status: str = Field(default="not_started") # not_started, in_progress, completed
    current_stage: int = Field(default=1)
    
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None