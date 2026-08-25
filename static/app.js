// State Management
let state = {
    candidates: [],
    activeCandidateId: null,
    activeTab: 'keywords',
    keywordCategoryFilter: 'all',
    currentAnalysis: null
};

// SVG Icons for reuse
const ICONS = {
    check: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`,
    cross: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`
};

// Job Description Templates
const TEMPLATES = {
    frontend: {
        title: "Frontend Development Intern",
        desc: "We are seeking a Frontend Development Intern to join our engineering team. You will assist in building responsive user interfaces for our core SaaS platform.\n\nRequired Skills:\n- Strong knowledge of HTML, CSS, JavaScript, and typescript.\n- Experience with React, Tailwind, and bootstrap.\n- Familiarity with Git, GitHub, and agile software development workflows.\n- Good communication, teamwork, and problem-solving skills."
    },
    python: {
        title: "Junior Python Developer",
        desc: "We are looking for a Junior Python Developer to help build and maintain our backend APIs and data processing systems.\n\nRequired Skills:\n- Proficiency in Python, Flask, fastapi, or Django.\n- Experience working with SQL databases like PostgreSQL, mysql, or SQLite.\n- Understanding of RESTful API design, microservices, and Docker containers.\n- Experience deploying cloud services on AWS, GCP, or Azure.\n- Unit testing, scrum methodologies, and Jira for task management."
    },
    qa: {
        title: "QA Engineer Analyst",
        desc: "We are hiring a QA Analyst to ensure the quality and reliability of our web application releases.\n\nRequired Skills:\n- Experience writing detailed test cases and test plans.\n- Hands-on experience with manual testing and test management tools.\n- Familiarity with automation tools like Selenium or Cypress is a plus.\n- Experience with bug tracking tools like Jira or Trello.\n- Strong analytical, critical-thinking, and communication skills."
    }
};

// DOM Elements
const elements = {
    btnToggleSidebar: document.getElementById('btn-toggle-sidebar'),
    btnCloseSidebar: document.getElementById('btn-close-sidebar'),
    sidebarBackdrop: document.getElementById('sidebar-backdrop'),
    appContainer: document.querySelector('.app-container'),
    
    btnNewScan: document.getElementById('btn-new-scan'),
    candidateList: document.getElementById('candidate-list'),
    sidebarLoading: document.getElementById('sidebar-loading'),
    pageTitle: document.getElementById('page-title'),
    
    panelScan: document.getElementById('panel-scan'),
    panelResults: document.getElementById('panel-results'),
    
    formScan: document.getElementById('form-ats-scan'),
    inputJobTitle: document.getElementById('input-job-title'),
    inputCandidateName: document.getElementById('input-candidate-name'),
    inputJobDesc: document.getElementById('input-job-desc'),
    btnSubmitScan: document.getElementById('btn-submit-scan'),
    scanBtnSpinner: document.getElementById('scan-btn-spinner'),
    
    dropZoneResume: document.getElementById('drop-zone-resume'),
    inputResume: document.getElementById('input-resume'),
    fileInfoResume: document.getElementById('file-info-resume'),
    
    dropZoneCoverLetter: document.getElementById('drop-zone-cover-letter'),
    inputCoverLetter: document.getElementById('input-cover-letter'),
    fileInfoCoverLetter: document.getElementById('file-info-cover-letter'),
    
    btnTemplateFrontend: document.getElementById('btn-template-frontend'),
    btnTemplatePython: document.getElementById('btn-template-python'),
    btnTemplateQA: document.getElementById('btn-template-qa'),
    
    // Results DOM
    resCandidateName: document.getElementById('res-candidate-name'),
    resCandidateAvatar: document.getElementById('res-candidate-avatar'),
    resInterviewBadge: document.getElementById('res-interview-badge'),
    resCandidateTitle: document.getElementById('res-candidate-title'),
    resCandidateEmail: document.getElementById('res-candidate-email'),
    resCandidatePhone: document.getElementById('res-candidate-phone'),
    btnDeleteCandidate: document.getElementById('btn-delete-candidate'),
    
    resScoreRing: document.getElementById('res-score-ring'),
    resScoreNumber: document.getElementById('res-score-number'),
    resScoreCaption: document.getElementById('res-score-caption'),
    
    resLikelihoodPct: document.getElementById('res-likelihood-pct'),
    resLikelihoodBar: document.getElementById('res-likelihood-bar'),
    resLikelihoodDesc: document.getElementById('res-likelihood-desc'),
    
    resMetaWords: document.getElementById('res-meta-words'),
    resMetaNumbers: document.getElementById('res-meta-numbers'),
    resMetaVerbs: document.getElementById('res-meta-verbs'),
    resMetaVerbsList: document.getElementById('res-meta-verbs-list'),
    
    // Tabs Navigation
    tabBtnKeywords: document.getElementById('tab-btn-keywords'),
    tabBtnSuggestions: document.getElementById('tab-btn-suggestions'),
    tabBtnCoverLetter: document.getElementById('tab-btn-coverletter'),
    
    tabPanelKeywords: document.getElementById('tab-panel-keywords'),
    tabPanelSuggestions: document.getElementById('tab-panel-suggestions'),
    tabPanelCoverLetter: document.getElementById('tab-panel-coverletter'),
    
    // Keywords Results
    resKwRatio: document.getElementById('res-kw-ratio'),
    resKwsMatched: document.getElementById('res-kws-matched'),
    resKwsMissing: document.getElementById('res-kws-missing'),
    filterKwButtons: document.querySelectorAll('.filter-kw-btn'),
    
    // Suggestions Results
    resSuggestionsList: document.getElementById('res-suggestions-list'),
    resChecklistStack: document.getElementById('res-checklist-stack'),
    
    // Cover Letter Results
    coverletterResultsContainer: document.getElementById('coverletter-results-container'),
    coverletterEmptyState: document.getElementById('coverletter-empty-state'),
    resClScore: document.getElementById('res-cl-score'),
    resClStatus: document.getElementById('res-cl-status'),
    resClCheckGreeting: document.getElementById('res-cl-check-greeting'),
    resClCheckSignoff: document.getElementById('res-cl-check-signoff'),
    resClCheckLength: document.getElementById('res-cl-check-length'),
    resClWordcountLabel: document.getElementById('res-cl-wordcount-label'),
    resClSuggestionsList: document.getElementById('res-cl-suggestions-list'),
    
    // Parser Toggles
    parserOptionLocal: document.getElementById('parser-option-local'),
    parserOptionGemini: document.getElementById('parser-option-gemini'),
    radioParserLocal: document.getElementById('radio-parser-local'),
    radioParserGemini: document.getElementById('radio-parser-gemini'),
    geminiSublabel: document.getElementById('gemini-sublabel'),
    resCandidateParser: document.getElementById('res-candidate-parser')
};

// Event Listeners on Load
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

function initApp() {
    // 1. Load Candidates History
    loadCandidates();
    
    // 2. Tab Navigation Hooks
    setupTabs();
    
    // 3. Setup Drag and Drop File Listeners
    setupDragAndDrop(elements.dropZoneResume, elements.inputResume, elements.fileInfoResume);
    setupDragAndDrop(elements.dropZoneCoverLetter, elements.inputCoverLetter, elements.fileInfoCoverLetter);
    
    // 4. Forms Submit
    elements.formScan.addEventListener('submit', handleScanSubmit);
    
    // 5. Template Buttons
    elements.btnTemplateFrontend.addEventListener('click', () => fillTemplate('frontend'));
    elements.btnTemplatePython.addEventListener('click', () => fillTemplate('python'));
    elements.btnTemplateQA.addEventListener('click', () => fillTemplate('qa'));
    
    // 6. Navigation Control
    elements.btnNewScan.addEventListener('click', () => {
        showScanPanel();
        closeMobileSidebar();
    });
    elements.btnDeleteCandidate.addEventListener('click', handleDeleteActiveCandidate);
    
    if (elements.btnToggleSidebar) {
        elements.btnToggleSidebar.addEventListener('click', openMobileSidebar);
    }
    if (elements.btnCloseSidebar) {
        elements.btnCloseSidebar.addEventListener('click', closeMobileSidebar);
    }
    if (elements.sidebarBackdrop) {
        elements.sidebarBackdrop.addEventListener('click', closeMobileSidebar);
    }
    
    // 7. Keyword Filter Buttons
    elements.filterKwButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            elements.filterKwButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.keywordCategoryFilter = btn.dataset.category;
            renderKeywords();
        });
    });

    // 8. Parser UI setup
    setupParserToggles();
    checkGeminiAvailability();

    // 9. About & License Modal Hooks
    const btnAboutLicense = document.getElementById('btn-about-license');
    const modalAbout = document.getElementById('modal-about');
    const btnCloseAbout = document.getElementById('btn-close-about');
    
    if (btnAboutLicense && modalAbout && btnCloseAbout) {
        btnAboutLicense.addEventListener('click', () => {
            modalAbout.classList.add('active');
            modalAbout.setAttribute('aria-hidden', 'false');
        });
        
        const closeModal = () => {
            modalAbout.classList.remove('active');
            modalAbout.setAttribute('aria-hidden', 'true');
        };
        
        btnCloseAbout.addEventListener('click', closeModal);
        
        // Close modal on clicking backdrop
        modalAbout.addEventListener('click', (e) => {
            if (e.target === modalAbout) {
                closeModal();
            }
        });
        
        // Close modal on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modalAbout.classList.contains('active')) {
                closeModal();
            }
        });
    }
}

// Sidebar & Candidate list Management
async function loadCandidates() {
    elements.sidebarLoading.classList.remove('hidden');
    try {
        const response = await fetch(window.API_ROUTES.candidates);
        if (!response.ok) throw new Error("Failed to load candidates");
        state.candidates = await response.json();
        renderCandidateList();
    } catch (error) {
        console.error(error);
    } finally {
        elements.sidebarLoading.classList.add('hidden');
    }
}

function renderCandidateList() {
    elements.candidateList.innerHTML = '';
    
    if (state.candidates.length === 0) {
        elements.candidateList.innerHTML = `<li class="empty-list-placeholder">No candidates scanned yet. Run a new scan to get started.</li>`;
        return;
    }
    
    state.candidates.forEach(cand => {
        const li = document.createElement('li');
        li.className = `candidate-item ${cand.id === state.activeCandidateId ? 'active' : ''}`;
        li.setAttribute('role', 'menuitem');
        
        let scoreClass = 'score-low';
        if (cand.match_score >= 80) scoreClass = 'score-high';
        else if (cand.match_score >= 55) scoreClass = 'score-medium';
        
        li.innerHTML = `
            <div class="candidate-item-info">
                <span class="cand-item-name">${escapeHTML(cand.name)}</span>
                <span class="cand-item-job">${escapeHTML(cand.job_title)}</span>
            </div>
            <div class="candidate-item-score ${scoreClass}">
                ${cand.match_score}%
            </div>
        `;
        
        li.addEventListener('click', () => {
            loadCandidateDetail(cand.id);
        });
        
        elements.candidateList.appendChild(li);
    });
}

// Load Candidate Details
async function loadCandidateDetail(id) {
    state.activeCandidateId = id;
    renderCandidateList(); // update active highlight
    
    try {
        const response = await fetch(`${window.API_ROUTES.candidates}/${id}`);
        if (!response.ok) throw new Error("Failed to fetch candidate details");
        const details = await response.json();
        state.currentAnalysis = details;
        showResultsPanel();
        renderAnalysisResults();
        closeMobileSidebar();
    } catch (error) {
        alert("Error loading candidate analysis details.");
        console.error(error);
    }
}

// Panel Toggling
function showScanPanel() {
    state.activeCandidateId = null;
    renderCandidateList(); // Remove active highlights
    
    elements.pageTitle.textContent = "Candidate Analyzer";
    elements.panelResults.classList.remove('active');
    elements.panelScan.classList.add('active');
}

function showResultsPanel() {
    elements.pageTitle.textContent = "ATS Fit Scan Results";
    elements.panelScan.classList.remove('active');
    elements.panelResults.classList.add('active');
}

// Form Handlers & Drag-and-Drop
function setupDragAndDrop(dropZone, fileInput, fileInfoLabel) {
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            updateDropZoneLabel(fileInput, dropZone, fileInfoLabel);
        }
    });
    
    fileInput.addEventListener('change', () => {
        updateDropZoneLabel(fileInput, dropZone, fileInfoLabel);
    });
}

function updateDropZoneLabel(fileInput, dropZone, fileInfoLabel) {
    if (fileInput.files && fileInput.files.length > 0) {
        const name = fileInput.files[0].name;
        const sizeKb = (fileInput.files[0].size / 1024).toFixed(1);
        fileInfoLabel.textContent = `${name} (${sizeKb} KB)`;
        dropZone.classList.add('has-file');
    } else {
        fileInfoLabel.textContent = "No file selected";
        dropZone.classList.remove('has-file');
    }
}

function fillTemplate(key) {
    const data = TEMPLATES[key];
    if (!data) return;
    
    elements.inputJobTitle.value = data.title;
    elements.inputJobDesc.value = data.desc;
}

// Upload Submission
async function handleScanSubmit(e) {
    e.preventDefault();
    
    // Disable submit and show loader
    elements.btnSubmitScan.disabled = true;
    elements.scanBtnSpinner.classList.remove('hidden');
    
    const formData = new FormData(elements.formScan);
    
    try {
        const response = await fetch(window.API_ROUTES.analyze, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || "An unknown error occurred during scanning");
        }
        
        const data = await response.json();
        
        // Reset Form Files
        elements.inputResume.value = '';
        elements.inputCoverLetter.value = '';
        elements.dropZoneResume.classList.remove('has-file');
        elements.fileInfoResume.textContent = "No file selected";
        elements.dropZoneCoverLetter.classList.remove('has-file');
        elements.fileInfoCoverLetter.textContent = "No file selected";
        
        // Update state and load results
        state.activeCandidateId = data.candidate_id;
        state.currentAnalysis = {
            id: data.candidate_id,
            name: data.candidate_name,
            email: data.candidate_email,
            phone: data.candidate_phone,
            job_title: data.job_title,
            analysis: data.analysis
        };
        
        // Reload Candidates in sidebar
        await loadCandidates();
        
        showResultsPanel();
        renderAnalysisResults();
        
    } catch (error) {
        alert(error.message);
        console.error(error);
    } finally {
        elements.btnSubmitScan.disabled = false;
        elements.scanBtnSpinner.classList.add('hidden');
    }
}

// Delete Candidate
async function handleDeleteActiveCandidate() {
    if (!state.activeCandidateId) return;
    
    const cName = state.currentAnalysis.name;
    if (!confirm(`Are you sure you want to delete ${cName} from the database?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${window.API_ROUTES.candidates}/${state.activeCandidateId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error("Deletion failed");
        
        // Reload candidates and redirect to Scan view
        await loadCandidates();
        showScanPanel();
        closeMobileSidebar();
    } catch (error) {
        alert("Error deleting candidate record.");
        console.error(error);
    }
}

// Tabs Controller
function setupTabs() {
    const tabs = [
        { btn: elements.tabBtnKeywords, panel: elements.tabPanelKeywords, name: 'keywords' },
        { btn: elements.tabBtnSuggestions, panel: elements.tabPanelSuggestions, name: 'suggestions' },
        { btn: elements.tabBtnCoverLetter, panel: elements.tabPanelCoverLetter, name: 'coverletter' }
    ];
    
    tabs.forEach(tab => {
        tab.btn.addEventListener('click', () => {
            tabs.forEach(t => {
                t.btn.classList.remove('active');
                t.btn.setAttribute('aria-selected', 'false');
                t.panel.classList.remove('active');
            });
            
            tab.btn.classList.add('active');
            tab.btn.setAttribute('aria-selected', 'true');
            tab.panel.classList.add('active');
            state.activeTab = tab.name;
        });
    });
}

// Results Renderer
function renderAnalysisResults() {
    const c = state.currentAnalysis;
    if (!c || !c.analysis) return;
    
    const analysis = c.analysis;
    
    // Reset defaults
    state.activeTab = 'keywords';
    state.keywordCategoryFilter = 'all';
    
    // Set Tab State
    elements.tabBtnKeywords.click();
    elements.filterKwButtons.forEach(btn => {
        if (btn.dataset.category === 'all') btn.classList.add('active');
        else btn.classList.remove('active');
    });
    
    // 1. Populate Candidate Info
    elements.resCandidateName.textContent = c.name;
    elements.resCandidateAvatar.textContent = getInitials(c.name);
    elements.resCandidateTitle.textContent = c.job_title;
    elements.resCandidateEmail.textContent = c.email || 'N/A';
    elements.resCandidatePhone.textContent = c.phone || 'N/A';
    
    // Parser Used Badge
    if (elements.resCandidateParser) {
        const parser = analysis.parser_used || 'local';
        if (parser === 'gemini') {
            elements.resCandidateParser.textContent = 'Google Gemini AI';
            elements.resCandidateParser.className = 'parser-used-badge badge-gemini';
        } else {
            elements.resCandidateParser.textContent = 'Local NLP';
            elements.resCandidateParser.className = 'parser-used-badge badge-local';
        }
    }
    
    // Likelihood Badge
    elements.resInterviewBadge.className = 'interview-likelihood-badge';
    let badgeClass = 'badge-low-match';
    if (analysis.match_score >= 80) badgeClass = 'badge-high-match';
    else if (analysis.match_score >= 55) badgeClass = 'badge-moderate-match';
    
    elements.resInterviewBadge.classList.add(badgeClass);
    elements.resInterviewBadge.textContent = analysis.interview_likelihood;
    
    // 2. Score Ring SVG Gauge
    elements.resScoreNumber.textContent = analysis.match_score;
    // Circle circumference is 2 * PI * r = 2 * 3.14159 * 50 = 314
    const offset = 314 - (analysis.match_score / 100) * 314;
    elements.resScoreRing.style.strokeDashoffset = offset;
    
    // Ring Color Colorized
    elements.resScoreRing.style.stroke = 'var(--color-primary)';
    if (analysis.match_score >= 80) {
        elements.resScoreRing.style.stroke = 'var(--color-success)';
        elements.resScoreCaption.textContent = "High candidate alignment.";
    } else if (analysis.match_score >= 55) {
        elements.resScoreRing.style.stroke = 'var(--color-warning)';
        elements.resScoreCaption.textContent = "Moderate alignment; gaps exist.";
    } else {
        elements.resScoreRing.style.stroke = 'var(--color-danger)';
        elements.resScoreCaption.textContent = "Low alignment; review missing terms.";
    }
    
    // 3. Interview Likelihood bar
    elements.resLikelihoodPct.textContent = `${analysis.likelihood_percentage}%`;
    elements.resLikelihoodBar.style.width = `${analysis.likelihood_percentage}%`;
    
    // 4. Composition Metadata
    elements.resMetaWords.textContent = analysis.word_count;
    elements.resMetaNumbers.textContent = analysis.metrics_found;
    elements.resMetaVerbs.textContent = analysis.action_verbs ? analysis.action_verbs.length : 0;
    
    elements.resMetaVerbsList.innerHTML = '';
    if (analysis.action_verbs && analysis.action_verbs.length > 0) {
        analysis.action_verbs.forEach(v => {
            const span = document.createElement('span');
            span.className = 'verb-chip';
            span.textContent = v;
            elements.resMetaVerbsList.appendChild(span);
        });
    } else {
        elements.resMetaVerbsList.innerHTML = `<span class="verb-chip">None identified</span>`;
    }
    
    // 5. Tabs Content Renders
    renderKeywords();
    renderSuggestions();
    renderCoverLetterResult();
}

// Render Keywords List
function renderKeywords() {
    const analysis = state.currentAnalysis.analysis;
    if (!analysis || !analysis.keywords) return;
    
    const kws = analysis.keywords;
    const filter = state.keywordCategoryFilter;
    
    // Clear list
    elements.resKwsMatched.innerHTML = '';
    elements.resKwsMissing.innerHTML = '';
    
    // Filter functions
    const filterFn = (item) => filter === 'all' || item.category === filter;
    
    const matchedFiltered = kws.matched.filter(filterFn);
    const missingFiltered = kws.missing.filter(filterFn);
    
    // Show match ratios
    const totalMatch = kws.matched.length;
    const totalKeywords = totalMatch + kws.missing.length;
    elements.resKwRatio.textContent = `Matched: ${totalMatch} / ${totalKeywords}`;
    
    // Populate matched
    if (matchedFiltered.length === 0) {
        elements.resKwsMatched.innerHTML = `<span class="empty-list-placeholder">No matching terms.</span>`;
    } else {
        matchedFiltered.forEach(item => {
            const span = document.createElement('span');
            span.className = 'keyword-chip chip-matched';
            span.innerHTML = `
                ${escapeHTML(item.keyword)}
                <span class="chip-category-label">${escapeHTML(item.category)}</span>
            `;
            elements.resKwsMatched.appendChild(span);
        });
    }
    
    // Populate missing
    if (missingFiltered.length === 0) {
        elements.resKwsMissing.innerHTML = `<span class="empty-list-placeholder">No critical gaps. Excellent!</span>`;
    } else {
        missingFiltered.forEach(item => {
            const span = document.createElement('span');
            span.className = 'keyword-chip chip-missing';
            span.innerHTML = `
                ${escapeHTML(item.keyword)}
                <span class="chip-category-label">${escapeHTML(item.category)}</span>
            `;
            elements.resKwsMissing.appendChild(span);
        });
    }
}

// Render Suggestions & checklist
function renderSuggestions() {
    const analysis = state.currentAnalysis.analysis;
    if (!analysis) return;
    
    // 1. Load Suggestions Stack
    elements.resSuggestionsList.innerHTML = '';
    
    if (!analysis.suggestions || analysis.suggestions.length === 0) {
        elements.resSuggestionsList.innerHTML = `
            <div class="suggestion-item-card prio-low" style="border-left-color: var(--color-success);">
                <div class="suggestion-header-row">
                    <span class="suggestion-prio-tag tag-high" style="background-color: var(--color-success-light); color: var(--color-success);">Excellent</span>
                    <span class="suggestion-type-label">Resume Optimization</span>
                </div>
                <p class="suggestion-message">Your resume is highly optimized for this description. No major issues found.</p>
            </div>
        `;
    } else {
        analysis.suggestions.forEach(s => {
            const item = document.createElement('div');
            const prioClass = `prio-${s.priority.toLowerCase()}`;
            const tagClass = `tag-${s.priority.toLowerCase()}`;
            
            item.className = `suggestion-item-card ${prioClass}`;
            item.innerHTML = `
                <div class="suggestion-header-row">
                    <span class="suggestion-prio-tag ${tagClass}">${s.priority} Priority</span>
                    <span class="suggestion-type-label">${s.type.toUpperCase()}</span>
                </div>
                <p class="suggestion-message">${s.message}</p>
            `;
            elements.resSuggestionsList.appendChild(item);
        });
    }
    
    // 2. Load Section checklist sidebar
    elements.resChecklistStack.innerHTML = '';
    
    // Experience
    renderChecklistItem("Experience", analysis.sections_found.includes("Experience"));
    renderChecklistItem("Education", analysis.sections_found.includes("Education"));
    renderChecklistItem("Skills", analysis.sections_found.includes("Skills"));
    renderChecklistItem("Projects", analysis.sections_found.includes("Projects"));
}

function renderChecklistItem(name, isPresent) {
    const div = document.createElement('div');
    div.className = 'checklist-item';
    
    const iconClass = isPresent ? 'check-success' : 'check-missing';
    const icon = isPresent ? ICONS.check : ICONS.cross;
    
    div.innerHTML = `
        <div class="check-icon-circle ${iconClass}">
            ${icon}
        </div>
        <span>${name} Section</span>
    `;
    elements.resChecklistStack.appendChild(div);
}

// Render Cover Letter
function renderCoverLetterResult() {
    const analysis = state.currentAnalysis.analysis;
    if (!analysis) return;
    
    const cl = analysis.cover_letter;
    
    if (!cl) {
        elements.coverletterResultsContainer.classList.add('hidden');
        elements.coverletterEmptyState.classList.remove('hidden');
        return;
    }
    
    elements.coverletterEmptyState.classList.add('hidden');
    elements.coverletterResultsContainer.classList.remove('hidden');
    
    // Set score and details
    elements.resClScore.textContent = cl.cl_score;
    elements.resClWordcountLabel.textContent = `${cl.word_count} words`;
    
    // Classify alignment status
    if (cl.cl_score >= 80) {
        elements.resClStatus.textContent = "High Alignment";
        elements.resClStatus.style.color = "var(--color-success)";
    } else if (cl.cl_score >= 60) {
        elements.resClStatus.textContent = "Moderate Alignment";
        elements.resClStatus.style.color = "var(--color-warning)";
    } else {
        elements.resClStatus.textContent = "Poor Alignment";
        elements.resClStatus.style.color = "var(--color-danger)";
    }
    
    // Salutations & sign-offs
    updateClCheckItem(elements.resClCheckGreeting, cl.has_greeting);
    updateClCheckItem(elements.resClCheckSignoff, cl.has_signoff);
    
    // Length pass
    updateClCheckItem(elements.resClCheckLength, cl.length_status === "Good");
    
    // Suggestions
    elements.resClSuggestionsList.innerHTML = '';
    if (cl.suggestions.length === 0) {
        elements.resClSuggestionsList.innerHTML = `
            <div class="suggestion-item-card prio-low" style="border-left-color: var(--color-success);">
                <div class="suggestion-header-row">
                    <span class="suggestion-prio-tag tag-high" style="background-color: var(--color-success-light); color: var(--color-success);">Optimized</span>
                    <span class="suggestion-type-label">Salutations & Density</span>
                </div>
                <p class="suggestion-message">Your cover letter has excellent structure, formatting, and keyword alignment.</p>
            </div>
        `;
    } else {
        cl.suggestions.forEach(s => {
            const item = document.createElement('div');
            item.className = 'suggestion-item-card prio-medium';
            item.innerHTML = `
                <div class="suggestion-header-row">
                    <span class="suggestion-prio-tag tag-medium">Medium Priority</span>
                    <span class="suggestion-type-label">COVER LETTER GAP</span>
                </div>
                <p class="suggestion-message">${s}</p>
            `;
            elements.resClSuggestionsList.appendChild(item);
        });
    }
}

function updateClCheckItem(el, isPass) {
    if (!el) return;
    if (isPass) {
        el.className = 'check-pass';
    } else {
        el.className = 'check-fail';
    }
}

// Helpers
function getInitials(name) {
    if (!name) return 'UN';
    const parts = name.trim().split(/\s+/);
    if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

function escapeHTML(str) {
    if (!str) return '';
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}

function setupParserToggles() {
    const localOpt = elements.parserOptionLocal;
    const geminiOpt = elements.parserOptionGemini;
    
    if (localOpt && geminiOpt) {
        localOpt.addEventListener('click', () => {
            if (elements.radioParserLocal) {
                elements.radioParserLocal.checked = true;
                localOpt.classList.add('selected');
                geminiOpt.classList.remove('selected');
            }
        });
        
        geminiOpt.addEventListener('click', () => {
            if (geminiOpt.classList.contains('disabled')) return;
            if (elements.radioParserGemini) {
                elements.radioParserGemini.checked = true;
                geminiOpt.classList.add('selected');
                localOpt.classList.remove('selected');
            }
        });
    }
}

async function checkGeminiAvailability() {
    try {
        const response = await fetch(window.API_ROUTES.config);
        if (!response.ok) throw new Error("Config fetch failed");
        
        const data = await response.json();
        if (!data.gemini_enabled) {
            disableGeminiUI();
        }
    } catch (err) {
        console.error("Error checking Gemini status, disabling toggle:", err);
        disableGeminiUI();
    }
}

function disableGeminiUI() {
    if (elements.parserOptionGemini) {
        elements.parserOptionGemini.classList.add('disabled');
        elements.parserOptionGemini.classList.remove('selected');
    }
    if (elements.radioParserGemini) {
        elements.radioParserGemini.disabled = true;
        elements.radioParserGemini.checked = false;
    }
    if (elements.radioParserLocal) {
        elements.radioParserLocal.checked = true;
    }
    if (elements.parserOptionLocal) {
        elements.parserOptionLocal.classList.add('selected');
    }
    if (elements.geminiSublabel) {
        elements.geminiSublabel.textContent = "API Key Missing (Disabled)";
    }
}

// Mobile sidebar helpers
function openMobileSidebar() {
    if (elements.appContainer) {
        elements.appContainer.classList.add('sidebar-open');
    }
}

function closeMobileSidebar() {
    if (elements.appContainer) {
        elements.appContainer.classList.remove('sidebar-open');
    }
}
