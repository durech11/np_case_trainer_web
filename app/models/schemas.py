from pydantic import BaseModel, Field
from typing import List, Optional

class Demographics(BaseModel):
    age: int
    gender: str
    ethnicity: Optional[str] = None
    occupation: Optional[str] = None

class Vitals(BaseModel):
    bp: str
    hr: int
    rr: int
    temp: str
    spo2: str
    weight: Optional[str] = None
    height: Optional[str] = None

class ModelContent(BaseModel):
    differential_diagnosis: List[str]
    soap_note: str
    assessment_and_plan: str

class CaseStudySchema(BaseModel):
    case_id: str
    title: str
    specialty: str
    difficulty: str
    summary: str
    
    patient_demographics: Demographics
    chief_complaint: str
    hpi: str
    
    pmh: List[str] = Field(default_factory=list)
    psh: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    family_history: List[str] = Field(default_factory=list)
    social_history: List[str] = Field(default_factory=list)
    
    ros: List[str] = Field(default_factory=list)
    physical_exam: List[str] = Field(default_factory=list)
    
    vitals: Vitals
    
    labs: List[str] = Field(default_factory=list)
    imaging: List[str] = Field(default_factory=list)
    
    red_flags: List[str] = Field(default_factory=list)
    teaching_points: List[str] = Field(default_factory=list)
    
    model_answers: ModelContent
