GLOSSARY = {
    "lisinopril": "An ACE inhibitor commonly used to treat hypertension and heart failure. It works by relaxing blood vessels.",
    "atorvastatin": "A statin medication used to prevent cardiovascular disease by lowering cholesterol and stabilizing plaques.",
    "metformin": "A first-line oral antidiabetic drug for Type 2 Diabetes that decreases hepatic glucose production.",
    "troponin i": "A cardiac enzyme that is a highly specific marker for myocardial injury or infarction.",
    "creatinine": "A waste product from muscle breakdown, used to measure kidney function (GFR).",
    "potassium": "An essential electrolyte; abnormal levels can cause dangerous cardiac arrhythmias.",
    "ldl cholesterol": "Low-density lipoprotein, often called 'bad' cholesterol. A major contributor to atherosclerotic plaque.",
    "hemoglobin a1c": "A blood test that measures average blood glucose levels over the past 2-3 months.",
    "electrocardiogram (ecg)": "A non-invasive test that records the electrical activity of the heart.",
    "chest x-ray": "A common imaging test used to evaluate the lungs, heart, and chest wall.",
    "stable angina pectoris": "Predictable chest pain or pressure that occurs with exertion and is relieved by rest or nitroglycerin.",
    "acute coronary syndrome (unstable angina / nstemi)": "A medical emergency representing acute myocardial ischemia. Pain may occur at rest.",
    "gastroesophageal reflux disease (gerd)": "A digestive disorder where stomach acid irritates the esophageal lining, often mimicking chest pain."
}

def get_definition(term: str) -> dict | None:
    term_lower = term.lower().strip()
    # Direct match
    if term_lower in GLOSSARY:
        return {"term": term, "definition": GLOSSARY[term_lower]}
    
    # Partial match fallback
    for key, definition in GLOSSARY.items():
        if term_lower in key or key in term_lower:
            return {"term": key.title(), "definition": definition}
            
    return None