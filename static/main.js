// Vanilla JS functionality for NP Case Trainer
document.addEventListener("DOMContentLoaded", () => {
    console.log("NP Case Trainer loaded. Educational use only.");
});

function showGlossary(term) {
    const modal = document.getElementById('glossaryModal');
    const termEl = document.getElementById('glossaryTerm');
    const defEl = document.getElementById('glossaryDefinition');
    
    termEl.innerText = term;
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
            defEl.innerText = data.definition;
        })
        .catch(err => {
            defEl.innerText = "No definition available for this term yet.";
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