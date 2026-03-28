from typing import Optional
from sqlmodel import Field, SQLModel
import json

class Case(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    data_json: str  # Stores the full structured JSON of the case

    @property
    def data(self) -> dict:
        return json.loads(self.data_json)
