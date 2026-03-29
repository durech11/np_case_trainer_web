// Vanilla JS functionality for NP Case Trainer
document.addEventListener("DOMContentLoaded", () => {
    console.log("NP Case Trainer loaded. Educational use only.");
});

function showGlossary(term) {
    const modal = document.getElementById('glossaryModal');
    const termEl = document.getElementById('glossaryTerm');
    const categoryEl = document.getElementById('glossaryCategory');
    const defEl = document.getElementById('glossaryDefinition');
    const pearlBox = document.getElementById('glossaryPearlBox');
    const pearlEl = document.getElementById('glossaryPearl');
    const interpBox = document.getElementById('glossaryInterpretationBox');
    const interpEl = document.getElementById('glossaryInterpretation');
    
    // Reset state
    termEl.innerText = term;
    categoryEl.style.display = 'none';
    pearlBox.style.display = 'none';
    interpBox.style.display = 'none';
    defEl.innerHTML = '<em>Loading...</em>';
    modal.style.display = 'flex';
    
    fetch(`/api/glossary/${encodeURIComponent(term)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Term not found');
            }
            return response.json();
        })
        .then(data => {
            // Data maps to ReferenceEntry schema
            termEl.innerText = data.term;
            defEl.innerText = data.definition;
            
            if (data.category) {
                categoryEl.innerText = data.category;
                categoryEl.style.display = 'inline-block';
            }
            
            if (data.clinical_pearl) {
                pearlEl.innerText = data.clinical_pearl;
                pearlBox.style.display = 'block';
            }
            
            if (data.interpretation) {
                interpEl.innerText = data.interpretation;
                interpBox.style.display = 'block';
            }
        })
        .catch(err => {
            defEl.innerText = "No detailed reference available for this term yet.";
        });
}

function closeGlossary() {
    document.getElementById('glossaryModal').style.display = 'none';
}

// Close modal when clicking outside of it
window.onclick = function(event) {
    const modal = document.getElementById('glossaryModal');
    if (event.target === modal) {
        closeGlossary();
    }
}