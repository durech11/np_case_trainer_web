// Vanilla JS functionality for NP Case Trainer

function applyAutoCollapsePreference() {
    const autoCollapseToggle = document.getElementById("autoCollapseToggle");
    if (!autoCollapseToggle) return;

    const isAuto = localStorage.getItem("autoCollapse") === "true";
    autoCollapseToggle.checked = isAuto;

    if (!isAuto) return;

    const currentStageInput = document.getElementById("currentStageData");
    if (!currentStageInput) return;

    const currentStage = parseInt(currentStageInput.value, 10);
    document.querySelectorAll(".stage-accordion").forEach((el) => {
        const stageNum = parseInt(el.dataset.stage, 10);
        if (stageNum !== currentStage) {
            el.removeAttribute("open");
        } else {
            el.setAttribute("open", "");
        }
    });
}

function bindAutoCollapseToggle() {
    const autoCollapseToggle = document.getElementById("autoCollapseToggle");
    if (!autoCollapseToggle || autoCollapseToggle.dataset.bound === "true") return;

    autoCollapseToggle.dataset.bound = "true";
    autoCollapseToggle.addEventListener("change", (e) => {
        localStorage.setItem("autoCollapse", e.target.checked);
        applyAutoCollapsePreference();
    });
}

function setBusyState(form, isBusy) {
    const controls = form.querySelectorAll("button, input, select, textarea");
    controls.forEach((el) => {
        if (el.tagName === "BUTTON") {
            el.disabled = isBusy;
        }
    });
    form.classList.toggle("is-submitting", isBusy);
}

function updateFlagButtonAppearance(button, isFlagged) {
    if (!button) return;
    button.classList.toggle("is-flagged", isFlagged);
    button.setAttribute("aria-pressed", isFlagged ? "true" : "false");
    button.setAttribute("title", isFlagged ? "Unmark red flag" : "Mark as red flag");
}

function replaceTargetsFromResponse(doc, selectors) {
    let replacedAny = false;
    selectors.forEach((selector) => {
        const currentEl = document.querySelector(selector);
        const nextEl = doc.querySelector(selector);
        if (currentEl && nextEl) {
            currentEl.replaceWith(nextEl);
            replacedAny = true;
        }
    });
    return replacedAny;
}

async function submitSessionForm(form) {
    const shell = document.getElementById("sessionPageShell");
    if (!shell) {
        form.submit();
        return;
    }

    const enhanceMode = form.dataset.enhance || "session-action";
    const submitButton = form.querySelector('[type="submit"]');
    const swapSelectors = (form.dataset.swap || "").split(",").map((item) => item.trim()).filter(Boolean);

    if (enhanceMode === "flag-toggle" && submitButton) {
        const currentlyFlagged = submitButton.classList.contains("is-flagged");
        updateFlagButtonAppearance(submitButton, !currentlyFlagged);
    }

    setBusyState(form, true);

    try {
        const response = await fetch(form.action, {
            method: "POST",
            body: new FormData(form),
            headers: {
                "X-Requested-With": "fetch",
            },
            credentials: "same-origin",
        });

        if (!response.ok) throw new Error(`Request failed with status ${response.status}`);

        const html = await response.text();
        const doc = new DOMParser().parseFromString(html, "text/html");
        const newShell = doc.getElementById("sessionPageShell");

        if (!newShell) {
            window.location.href = response.url || form.action;
            return;
        }

        const didPartialSwap = swapSelectors.length > 0 && replaceTargetsFromResponse(doc, swapSelectors);

        if (!didPartialSwap) {
            shell.replaceWith(newShell);
        }

        document.title = doc.title;
        history.replaceState({}, "", response.url || window.location.href);
        initializeSessionEnhancements();
        applyAutoCollapsePreference();
    } catch (error) {
        console.error(error);
        if (enhanceMode === "flag-toggle" && submitButton) {
            const optimisticFlagged = submitButton.classList.contains("is-flagged");
            updateFlagButtonAppearance(submitButton, !optimisticFlagged);
        }
        form.submit();
    } finally {
        setBusyState(form, false);
    }
}

function initializeSessionEnhancements() {
    bindAutoCollapseToggle();
    applyAutoCollapsePreference();

    const shell = document.getElementById("sessionPageShell");
    if (!shell || shell.dataset.bound === "true") return;

    shell.dataset.bound = "true";
    shell.addEventListener("submit", (event) => {
        const form = event.target;
        if (!(form instanceof HTMLFormElement)) return;
        if (!form.classList.contains("js-session-form")) return;

        event.preventDefault();
        submitSessionForm(form);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    console.log("NP Case Trainer loaded. Educational use only.");
    initializeSessionEnhancements();
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

window.onclick = function(event) {
    const modal = document.getElementById('glossaryModal');
    if (event.target === modal) {
        closeGlossary();
    }
}
