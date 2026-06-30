document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileList = document.getElementById('file-list');
    const form = document.getElementById('upload-form');
    const processBtn = document.getElementById('process-btn');
    const btnText = document.getElementById('btn-text');
    const spinner = document.getElementById('spinner');
    
    const resultsSection = document.getElementById('results-section');
    const profilesContainer = document.getElementById('profiles-container');
    const profileCount = document.getElementById('profile-count');
    const warningContainer = document.getElementById('warning-container');
    const pipelineStatus = document.getElementById('pipeline-status');

    // Modals
    const jsonModal = document.getElementById('json-modal');
    const closeJsonBtn = document.getElementById('close-json-modal');
    const jsonViewer = document.getElementById('json-viewer');
    const copyJsonBtn = document.getElementById('copy-json-btn');
    const downloadJsonBtn = document.getElementById('download-json-btn');

    const provModal = document.getElementById('provenance-modal');
    const closeProvBtn = document.getElementById('close-provenance-modal');
    const provTbody = document.getElementById('provenance-tbody');

    const toast = document.getElementById('toast');

    let uploadedFiles = [];
    let currentDisplayedJson = null;

    // Drag and Drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', handleDrop, false);
    fileInput.addEventListener('change', handleFiles, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles({ target: { files: files } });
    }

    function handleFiles(e) {
        const files = [...e.target.files];
        files.forEach(file => {
            if (file.name.endsWith('.csv') || file.name.endsWith('.pdf')) {
                uploadedFiles.push(file);
                renderFileItem(file);
            }
        });
    }

    function renderFileItem(file) {
        const div = document.createElement('div');
        div.className = 'file-item';
        div.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 8px;">
                <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
                <polyline points="13 2 13 9 20 9"></polyline>
            </svg>
            ${file.name}
        `;
        fileList.appendChild(div);
    }

    // Loading State Simulator
    const loadingStages = [
        "Parsing CSV...",
        "Extracting Resume...",
        "Fetching GitHub...",
        "Normalizing...",
        "Resolving Entities...",
        "Validating...",
        "Generating Output..."
    ];
    let loadingInterval;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (uploadedFiles.length === 0 && !document.getElementById('github-url').value) {
            alert('Please upload files or provide a GitHub URL');
            return;
        }

        // Start Loading Experience
        btnText.classList.add('hidden');
        spinner.classList.remove('hidden');
        processBtn.disabled = true;
        
        pipelineStatus.classList.remove('hidden');
        pipelineStatus.innerHTML = '';
        warningContainer.classList.add('hidden');
        warningContainer.innerHTML = '';

        let stageIndex = 0;
        loadingInterval = setInterval(() => {
            if (stageIndex < loadingStages.length) {
                pipelineStatus.innerHTML = `<div class="status-item active">⟳ ${loadingStages[stageIndex]}</div>`;
                stageIndex++;
            }
        }, 500);

        const formData = new FormData();
        uploadedFiles.forEach(file => formData.append('files', file));
        formData.append('github_url', document.getElementById('github-url').value);

        try {
            const response = await fetch('/process', {
                method: 'POST',
                body: formData
            });
            
            clearInterval(loadingInterval);
            
            const data = await response.json();
            if (response.ok) {
                renderFinalStatus();
                renderWarnings(data.stats.warnings);
                renderDashboard(data.stats);
                renderResults(data.profiles);
            } else {
                pipelineStatus.innerHTML = `<div class="status-item" style="color: var(--error);">✖ Processing Failed</div>`;
                alert(data.error || 'Processing failed');
            }
        } catch (error) {
            clearInterval(loadingInterval);
            console.error('Error:', error);
            pipelineStatus.innerHTML = `<div class="status-item" style="color: var(--error);">✖ Server Error</div>`;
            alert('Server error occurred');
        } finally {
            btnText.classList.remove('hidden');
            spinner.classList.add('hidden');
            processBtn.disabled = false;
        }
    });

    function renderFinalStatus() {
        const finalChecks = [
            "CSV Parsed", "Resume Parsed", "GitHub Retrieved", 
            "Phone Normalization", "Skill Canonicalization", 
            "Entity Resolution", "Conflict Resolution", 
            "Schema Validation", "Projection Completed"
        ];
        pipelineStatus.innerHTML = finalChecks.map(c => `<div class="status-item done">✓ ${c}</div>`).join('');
    }

    function renderWarnings(warnings) {
        if (!warnings || warnings.length === 0) return;
        warningContainer.classList.remove('hidden');
        warnings.forEach(w => {
            const div = document.createElement('div');
            div.className = 'warning-banner';
            div.innerHTML = `
                <span>⚠ ${w}</span>
                <button onclick="this.parentElement.remove()">×</button>
            `;
            warningContainer.appendChild(div);
        });
    }

    function renderDashboard(stats) {
        document.getElementById('stat-processed').textContent = stats.processed;
        document.getElementById('stat-merged').textContent = stats.merged;
        document.getElementById('stat-duplicates').textContent = stats.duplicates_resolved;
        document.getElementById('stat-warnings').textContent = (stats.warnings && stats.warnings.length) || 0;
    }

    function renderResults(profiles) {
        resultsSection.classList.remove('hidden');
        profilesContainer.innerHTML = '';
        profileCount.textContent = profiles.length;

        profiles.forEach((profile, index) => {
            const card = document.createElement('div');
            card.className = 'profile-card';
            
            const confidencePercent = (profile.overall_confidence * 100).toFixed(0);
            
            let skillsHtml = '';
            if (profile.skills && profile.skills.length > 0) {
                const first8 = profile.skills.slice(0, 8);
                const rest = profile.skills.slice(8);
                skillsHtml = `
                    <div class="skills-tags" id="skills-${index}">
                        ${first8.map(s => `<span class="skill-tag">${s.name || s}</span>`).join('')}
                        ${rest.length > 0 ? `<button class="skill-tag more-skills" onclick="document.getElementById('more-skills-${index}').style.display='inline'; this.style.display='none'">+${rest.length} More</button>` : ''}
                        <span id="more-skills-${index}" style="display:none;">
                            ${rest.map(s => `<span class="skill-tag">${s.name || s}</span>`).join('')}
                        </span>
                    </div>
                `;
            }

            const email = profile.primary_email || (profile.emails && profile.emails[0]) || profile.candidate_id || 'No email';
            const phone = profile.phone || (profile.phones && profile.phones[0]) || 'No phone';

            card.innerHTML = `
                <div class="card-header">
                    <h3>${profile.full_name || 'Unknown Candidate'}</h3>
                    <div class="email">${email}</div>
                </div>
                
                <div class="info-row">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
                    </svg>
                    ${phone}
                </div>
                
                ${skillsHtml}

                <div style="font-size: 0.8rem; color: var(--text-muted);">
                    Overall Confidence
                    <span style="float:right; font-weight: 600; color: white;">${confidencePercent}%</span>
                    <div class="confidence-bar-container">
                        <div class="confidence-bar" style="width: ${confidencePercent}%; background: ${confidencePercent > 80 ? 'var(--success)' : 'orange'}"></div>
                    </div>
                </div>
                
                <div class="card-actions">
                    <button class="view-prov-btn" data-index="${index}">View Provenance</button>
                    <button class="view-json-btn" data-index="${index}">View Output JSON</button>
                </div>
            `;
            
            profilesContainer.appendChild(card);

            // Bind buttons
            card.querySelector('.view-json-btn').addEventListener('click', () => openJsonModal(profile));
            card.querySelector('.view-prov-btn').addEventListener('click', () => openProvModal(profile));
        });
        
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    // Modal Logic
    function openJsonModal(profile) {
        currentDisplayedJson = JSON.stringify(profile, null, 2);
        jsonViewer.innerHTML = syntaxHighlight(currentDisplayedJson);
        jsonModal.classList.remove('hidden');
    }

    function openProvModal(profile) {
        provTbody.innerHTML = '';
        const provenance = profile.provenance || [];
        if (provenance.length === 0) {
            provTbody.innerHTML = '<tr><td colspan="3">No provenance available</td></tr>';
        } else {
            provenance.forEach(p => {
                provTbody.innerHTML += `
                    <tr>
                        <td style="color: white; font-weight: 500;">${p.field}</td>
                        <td>${p.source}</td>
                        <td>${p.method}</td>
                    </tr>
                `;
            });
        }
        provModal.classList.remove('hidden');
    }

    [closeJsonBtn, closeProvBtn].forEach(btn => {
        btn.addEventListener('click', () => {
            jsonModal.classList.add('hidden');
            provModal.classList.add('hidden');
        });
    });

    // Close on click outside
    window.addEventListener('click', (e) => {
        if (e.target === jsonModal) jsonModal.classList.add('hidden');
        if (e.target === provModal) provModal.classList.add('hidden');
    });

    // Copy JSON
    copyJsonBtn.addEventListener('click', () => {
        if (currentDisplayedJson) {
            navigator.clipboard.writeText(currentDisplayedJson).then(() => {
                toast.classList.remove('hidden');
                setTimeout(() => toast.classList.add('hidden'), 2500);
            });
        }
    });

    // Download JSON
    downloadJsonBtn.addEventListener('click', () => {
        if (currentDisplayedJson) {
            const blob = new Blob([currentDisplayedJson], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'candidate_profile.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    });

    // Syntax Highlighter for JSON
    function syntaxHighlight(json) {
        json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
            let cls = 'json-number';
            if (/^"/.test(match)) {
                if (/:$/.test(match)) {
                    cls = 'json-key';
                } else {
                    cls = 'json-string';
                }
            } else if (/true|false/.test(match)) {
                cls = 'json-boolean';
            } else if (/null/.test(match)) {
                cls = 'json-null';
            }
            return '<span class="' + cls + '">' + match + '</span>';
        });
    }
});
