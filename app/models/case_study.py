from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel
import json

class CaseStudy(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    case_id: str = Field(index=True, unique=True)
    title: str
    specialty: Optional[str] = None
    difficulty: Optional[str] = None
    summary: Optional[str] = None
    raw_json: str  # Stores the full structured JSON of the case
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def data(self) -> dict:
        return json.loads(self.raw_json)