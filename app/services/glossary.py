from pydantic import BaseModel
from typing import Optional, List

class ReferenceEntry(BaseModel):
    term: str
    category: str
    definition: str
    clinical_pearl: str
    interpretation: Optional[str] = None
    tags: List[str] = []

REFERENCE_DATA = [
    ReferenceEntry(
        term="Lisinopril",
        category="Medication",
        definition="An ACE inhibitor commonly used to treat hypertension and heart failure. It works by relaxing blood vessels.",
        clinical_pearl="Watch for a dry, hacking cough which is a common side effect. Can also cause hyperkalemia.",
        tags=["Cardiology", "Antihypertensive"]
    ),
    ReferenceEntry(
        term="Atorvastatin",
        category="Medication",
        definition="A statin medication used to prevent cardiovascular disease by lowering cholesterol and stabilizing plaques.",
        clinical_pearl="Monitor for myopathy and check liver function tests if hepatotoxicity is suspected.",
        tags=["Cardiology", "Lipid-lowering"]
    ),
    ReferenceEntry(
        term="Metformin",
        category="Medication",
        definition="A first-line oral antidiabetic drug for Type 2 Diabetes that decreases hepatic glucose production.",
        clinical_pearl="Must be held before contrast imaging to prevent lactic acidosis. GI upset is common initially.",
        tags=["Endocrinology", "Diabetes"]
    ),
    ReferenceEntry(
        term="Troponin I",
        category="Lab",
        definition="A cardiac enzyme that is a highly specific marker for myocardial injury or infarction.",
        clinical_pearl="Serial troponins are required, as a single negative test early in symptom onset does not definitively rule out ACS.",
        interpretation="Elevated levels indicate myocardial necrosis.",
        tags=["Cardiology", "Biomarker"]
    ),
    ReferenceEntry(
        term="Creatinine",
        category="Lab",
        definition="A waste product from muscle breakdown, used to measure kidney function (GFR).",
        clinical_pearl="A doubling of serum creatinine implies a 50% reduction in GFR.",
        tags=["Nephrology", "Renal"]
    ),
    ReferenceEntry(
        term="Potassium",
        category="Lab",
        definition="An essential intracellular electrolyte.",
        clinical_pearl="Both hyperkalemia and hypokalemia can cause fatal cardiac arrhythmias.",
        interpretation="Abnormal levels require prompt correction and ECG monitoring.",
        tags=["Electrolytes"]
    ),
    ReferenceEntry(
        term="LDL Cholesterol",
        category="Lab",
        definition="Low-density lipoprotein, often called 'bad' cholesterol. A major contributor to atherosclerotic plaque.",
        clinical_pearl="In high-risk patients (like those with established CAD), the target LDL is often < 70 mg/dL.",
        tags=["Cardiology", "Lipids"]
    ),
    ReferenceEntry(
        term="Hemoglobin A1c",
        category="Lab",
        definition="A blood test that measures average blood glucose levels over the past 2-3 months.",
        clinical_pearl="An A1c of 6.5% or higher on two separate occasions is diagnostic for diabetes.",
        interpretation="Elevated levels indicate poor glycemic control.",
        tags=["Endocrinology", "Diabetes"]
    ),
    ReferenceEntry(
        term="Electrocardiogram (ECG)",
        category="Imaging",
        definition="A non-invasive test that records the electrical activity of the heart.",
        clinical_pearl="The primary tool for diagnosing STEMI. Compare to previous ECGs if available.",
        tags=["Cardiology", "Diagnostics"]
    ),
    ReferenceEntry(
        term="Chest X-Ray",
        category="Imaging",
        definition="A common imaging test used to evaluate the lungs, heart, and chest wall.",
        clinical_pearl="Excellent for detecting pulmonary edema (heart failure), pneumonia, or pneumothorax.",
        tags=["Pulmonology", "Radiology"]
    ),
    ReferenceEntry(
        term="Stable Angina Pectoris",
        category="Diagnosis",
        definition="Predictable chest pain or pressure that occurs with exertion and is relieved by rest or nitroglycerin.",
        clinical_pearl="Usually indicates significant fixed epicardial coronary artery stenosis (>70%).",
        tags=["Cardiology", "CAD"]
    ),
    ReferenceEntry(
        term="Acute Coronary Syndrome (Unstable Angina / NSTEMI)",
        category="Diagnosis",
        definition="A spectrum of conditions compatible with acute myocardial ischemia/infarction. Pain may occur at rest.",
        clinical_pearl="Always treat as a medical emergency. Administer Aspirin immediately unless contraindicated.",
        tags=["Cardiology", "Emergency"]
    ),
    ReferenceEntry(
        term="Gastroesophageal Reflux Disease (GERD)",
        category="Diagnosis",
        definition="A digestive disorder where stomach acid irritates the esophageal lining, often mimicking chest pain.",
        clinical_pearl="A common 'mimic' of cardiac chest pain, but true cardiac causes must be ruled out first.",
        tags=["Gastroenterology"]
    ),
    ReferenceEntry(
        term="Hypertension",
        category="Diagnosis",
        definition="Chronically elevated blood pressure.",
        clinical_pearl="The 'silent killer'. Long-term uncontrolled HTN leads to LVH, stroke, and kidney disease.",
        tags=["Cardiology"]
    ),
    ReferenceEntry(
        term="Hyperlipidemia",
        category="Diagnosis",
        definition="Abnormally high concentration of fats or lipids in the blood.",
        clinical_pearl="Primary driver of atherosclerosis. Treat according to ASCVD risk scores, not just isolated numbers.",
        tags=["Cardiology"]
    ),
    ReferenceEntry(
        term="Type 2 Diabetes Mellitus",
        category="Diagnosis",
        definition="A chronic condition characterized by insulin resistance and relative insulin deficiency.",
        clinical_pearl="Cardiovascular disease is the leading cause of morbidity and mortality in these patients.",
        tags=["Endocrinology"]
    )
]

def get_definition(term: str) -> dict | None:
    term_lower = term.lower().strip()
    
    # 1. Exact Match
    for entry in REFERENCE_DATA:
        if entry.term.lower() == term_lower:
            return entry.model_dump()
            
    # 2. Partial Match (e.g., 'ecg' finds 'Electrocardiogram (ECG)')
    for entry in REFERENCE_DATA:
        if term_lower in entry.term.lower() or entry.term.lower() in term_lower:
            return entry.model_dump()
            
    return None