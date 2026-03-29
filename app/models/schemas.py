from pydantic import BaseModel, Field
from typing import List, Optional, Dict

# --- Nested Models for Structured Data ---

class PatientDemographics(BaseModel):
    age: int
    gender: str
    ethnicity: Optional[str] = None
    occupation: Optional[str] = None

class MedicationItem(BaseModel):
    name: str
    dose: str
    frequency: str

class VitalSigns(BaseModel):
    bp: str
    hr: int
    rr: int
    temp: str
    spo2: str
    weight: Optional[str] = None
    height: Optional[str] = None

class LabResult(BaseModel):
    name: str
    value: str
    unit: str
    flag: Optional[str] = None  # e.g., "High", "Low", "Normal"
    reference_range: Optional[str] = None
    interpretation: str

class ImagingStudy(BaseModel):
    type: str  # e.g., "Chest X-Ray", "Electrocardiogram (ECG)"
    summary: str
    interpretation: str

class ExamFinding(BaseModel):
    system: str
    finding: str

class TeachingPoint(BaseModel):
    point: str
    explanation: str

class ModelDifferentialItem(BaseModel):
    diagnosis: str
    rationale: str

class ModelSOAP(BaseModel):
    subjective: str
    objective: str
    assessment: str
    plan: str

class ModelAssessmentPlan(BaseModel):
    problem: str
    plan: str

# --- Main Case Study Schema ---

class CaseStudySchema(BaseModel):
    # Metadata
    case_id: str
    title: str
    specialty: str
    difficulty: int = Field(ge=1, le=5)
    summary: str
    
    # Presentation
    patient_demographics: PatientDemographics
    chief_complaint: str
    hpi: str
    
    # History
    pmh: List[str] = Field(default_factory=list)
    psh: List[str] = Field(default_factory=list)
    medications: List[MedicationItem] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    family_history: List[str] = Field(default_factory=list)
    social_history: List[str] = Field(default_factory=list)
    
    # Review of Systems
    ros: Dict[str, List[str]] = Field(default_factory=dict)

    # Physical Exam
    physical_exam: List[ExamFinding] = Field(default_factory=list)
    vitals: VitalSigns
    
    # Diagnostics
    labs: List[LabResult] = Field(default_factory=list)
    imaging: List[ImagingStudy] = Field(default_factory=list)
    
    # Educational Content
    red_flags: List[str] = Field(default_factory=list)
    teaching_points: List[TeachingPoint] = Field(default_factory=list)
    
    # Model Answers
    model_differential: List[ModelDifferentialItem] = Field(default_factory=list)
    model_soap: ModelSOAP
    model_assessment_plan: List[ModelAssessmentPlan] = Field(default_factory=list)
