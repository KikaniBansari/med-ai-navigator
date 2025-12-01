// API Configuration - Auto-detect based on environment
// In production (Render), use the same origin. In development, use localhost
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : window.location.origin; // Use same origin in production (Render)

// DOM Elements
const patientForm = document.getElementById('patientForm');
const submitBtn = document.getElementById('submitBtn');
const resultsSection = document.getElementById('resultsSection');
const closeResults = document.getElementById('closeResults');
const viewHistoryBtn = document.getElementById('viewHistoryBtn');
const viewMetricsBtn = document.getElementById('viewMetricsBtn');
const metricsModal = document.getElementById('metricsModal');
const historyModal = document.getElementById('historyModal');
const closeMetrics = document.getElementById('closeMetrics');
const closeHistory = document.getElementById('closeHistory');
const symptomTextarea = document.getElementById('symptoms');
const symptomCount = document.getElementById('symptomCount');

let currentPatientId = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    checkAPIHealth();
    setupCharacterCount();
});

// Event Listeners
function setupEventListeners() {
    patientForm.addEventListener('submit', handleFormSubmit);
    closeResults.addEventListener('click', () => hideResults());
    viewHistoryBtn.addEventListener('click', handleViewHistory);
    viewMetricsBtn.addEventListener('click', handleViewMetrics);
    closeMetrics.addEventListener('click', () => hideModal(metricsModal));
    closeHistory.addEventListener('click', () => hideModal(historyModal));
    
    // Close modals on outside click
    [metricsModal, historyModal].forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                hideModal(modal);
            }
        });
    });

    // Close modals on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            hideModal(metricsModal);
            hideModal(historyModal);
        }
    });
}

// Character Count
function setupCharacterCount() {
    if (symptomTextarea && symptomCount) {
        symptomTextarea.addEventListener('input', () => {
            const count = symptomTextarea.value.length;
            symptomCount.textContent = count;
            
            if (count > 500) {
                symptomCount.style.color = 'var(--warning)';
            } else if (count > 200) {
                symptomCount.style.color = 'var(--info)';
            } else {
                symptomCount.style.color = 'var(--text-muted)';
            }
        });
    }
}

// API Health Check
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            showToast('API connected successfully', 'success');
        }
    } catch (error) {
        console.error('API health check failed:', error);
        showToast('Cannot connect to API. Make sure the server is running on port 8000.', 'error');
    }
}

// Handle Form Submit
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(patientForm);
    const patientId = formData.get('patientId');
    const symptoms = formData.get('symptoms');
    const medicalRecord = formData.get('medicalRecord') || '';
    
    currentPatientId = patientId;
    
    // Show loading state
    setLoading(true);
    hideResults();
    showToast('Processing patient information...', 'info');
    
    try {
        const response = await fetch(`${API_BASE_URL}/process`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                patient_id: patientId,
                symptoms: symptoms,
                medical_record_text: medicalRecord
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
            showToast('Analysis completed successfully!', 'success');
        } else {
            throw new Error(data.error || 'Processing failed');
        }
        
    } catch (error) {
        console.error('Error processing request:', error);
        showToast(`Failed to process request: ${error.message}`, 'error');
    } finally {
        setLoading(false);
    }
}

// Display Results
function displayResults(data) {
    if (!data.success) {
        showToast(data.error || 'Processing failed', 'error');
        return;
    }
    
    const analysis = data.analysis || {};
    
    // Processing time
    updateProcessingTime(data.processing_time || 0);
    
    // Quick stats
    updateQuickStats(analysis);
    
    // Symptoms
    displaySymptoms(analysis.symptoms_parsed || {});
    
    // History
    displayHistory(analysis.history_context || {});
    
    // Risk Assessment
    displayRiskAssessment(analysis.risk_assessment || {});
    
    // Diagnosis Suggestions
    if (analysis.diagnosis_suggestions) {
        displayDiagnosisSuggestions(analysis.diagnosis_suggestions);
    }
    
    // Triage Recommendation
    displayTriageRecommendation(analysis.triage_recommendation || {});
    
    // Web Guidelines
    if (analysis.web_guidelines && analysis.web_guidelines.results) {
        displayWebGuidelines(analysis.web_guidelines);
    }
    
    // Warning
    if (data.bias_detected || analysis.triage_recommendation?.warning) {
        showWarning(analysis.triage_recommendation?.warning || 'Bias detected in recommendation');
    }
    
    // Show results section
    resultsSection.style.display = 'block';
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

// Update Processing Time
function updateProcessingTime(time) {
    const el = document.getElementById('processingTime');
    if (el) {
        const span = el.querySelector('span');
        if (span) {
            span.textContent = `Analysis completed in ${time.toFixed(2)} seconds`;
        }
    }
}

// Update Quick Stats
function updateQuickStats(analysis) {
    const container = document.getElementById('quickStats');
    if (!container) return;
    
    const symptoms = analysis.symptoms_parsed?.symptoms || [];
    const risk = analysis.risk_assessment || {};
    const diagnoses = analysis.diagnosis_suggestions || [];
    
    container.innerHTML = `
        <div class="stat-card">
            <div class="stat-icon" style="background: linear-gradient(135deg, var(--info), var(--primary-light));">
                <i class="fas fa-clipboard-list"></i>
            </div>
            <div class="stat-content">
                <h4>Symptoms Found</h4>
                <p>${Array.isArray(symptoms) ? symptoms.length : 0}</p>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="background: linear-gradient(135deg, var(--warning), #ff9800);">
                <i class="fas fa-exclamation-triangle"></i>
            </div>
            <div class="stat-content">
                <h4>Risk Score</h4>
                <p>${risk.score || 0}/10</p>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon" style="background: linear-gradient(135deg, var(--primary), var(--primary-light));">
                <i class="fas fa-diagnoses"></i>
            </div>
            <div class="stat-content">
                <h4>Possible Diagnoses</h4>
                <p>${Array.isArray(diagnoses) ? diagnoses.length : 0}</p>
            </div>
        </div>
    `;
}

// Display Symptoms
function displaySymptoms(symptoms) {
    const container = document.getElementById('symptomsResult');
    if (!container) return;
    
    const symptomsList = Array.isArray(symptoms.symptoms) 
        ? symptoms.symptoms 
        : (symptoms.symptoms ? [symptoms.symptoms] : []);
    
    container.innerHTML = `
        <div class="result-item">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                <i class="fas fa-list-ul" style="color: var(--info);"></i>
                <strong style="font-size: 1.1rem;">Identified Symptoms:</strong>
            </div>
            <ul style="margin-top: 0.5rem; padding-left: 1.5rem; display: flex; flex-direction: column; gap: 0.5rem;">
                ${symptomsList.map(s => `
                    <li style="padding: 0.5rem; background: var(--bg-primary); border-radius: var(--radius-sm); border-left: 3px solid var(--info);">
                        ${escapeHtml(s)}
                    </li>
                `).join('')}
            </ul>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1.5rem;">
            <div style="background: var(--bg-primary); padding: 1rem; border-radius: var(--radius-md);">
                <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Duration</div>
                <div style="font-size: 1.25rem; font-weight: 600; color: var(--text-primary);">
                    ${escapeHtml(symptoms.duration || 'Unknown')}
                </div>
            </div>
            <div style="background: var(--bg-primary); padding: 1rem; border-radius: var(--radius-md);">
                <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Severity</div>
                <div>
                    <span class="badge badge-${getSeverityBadgeClass(symptoms.severity)}">
                        ${escapeHtml(symptoms.severity || 'Unknown')}
                    </span>
                </div>
            </div>
        </div>
    `;
}

// Display History
function displayHistory(history) {
    const container = document.getElementById('historyResult');
    if (!container) return;
    
    const conditions = Array.isArray(history.conditions) ? history.conditions : [];
    const medications = Array.isArray(history.medications) ? history.medications : [];
    const vitals = history.vitals || {};
    
    container.innerHTML = `
        ${conditions.length > 0 ? `
            <div class="result-item">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                    <i class="fas fa-heartbeat" style="color: var(--danger);"></i>
                    <strong style="font-size: 1.1rem;">Chronic Conditions:</strong>
                </div>
                <ul style="margin-top: 0.5rem; padding-left: 1.5rem; display: flex; flex-direction: column; gap: 0.5rem;">
                    ${conditions.map(c => `
                        <li style="padding: 0.5rem; background: var(--bg-primary); border-radius: var(--radius-sm); border-left: 3px solid var(--danger);">
                            ${escapeHtml(c)}
                        </li>
                    `).join('')}
                </ul>
            </div>
        ` : '<div class="result-item" style="text-align: center; color: var(--text-muted); padding: 2rem;">No chronic conditions found</div>'}
        
        ${medications.length > 0 ? `
            <div class="result-item" style="margin-top: 1.5rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                    <i class="fas fa-pills" style="color: var(--secondary);"></i>
                    <strong style="font-size: 1.1rem;">Current Medications:</strong>
                </div>
                <ul style="margin-top: 0.5rem; padding-left: 1.5rem; display: flex; flex-direction: column; gap: 0.5rem;">
                    ${medications.map(m => `
                        <li style="padding: 0.5rem; background: var(--bg-primary); border-radius: var(--radius-sm); border-left: 3px solid var(--secondary);">
                            ${escapeHtml(m)}
                        </li>
                    `).join('')}
                </ul>
            </div>
        ` : ''}
        
        ${Object.keys(vitals).length > 0 ? `
            <div class="result-item" style="margin-top: 1.5rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                    <i class="fas fa-thermometer-half" style="color: var(--warning);"></i>
                    <strong style="font-size: 1.1rem;">Vital Signs:</strong>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-top: 0.5rem;">
                    ${Object.entries(vitals).map(([key, value]) => `
                        <div style="background: var(--bg-primary); padding: 1rem; border-radius: var(--radius-md); text-align: center;">
                            <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">${escapeHtml(key)}</div>
                            <div style="font-size: 1.25rem; font-weight: 600; color: var(--text-primary);">${escapeHtml(value)}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : ''}
    `;
}

// Display Risk Assessment
function displayRiskAssessment(risk) {
    const scoreValueEl = document.getElementById('scoreValue');
    const scoreProgressEl = document.getElementById('scoreProgress');
    const riskDetailsEl = document.getElementById('riskDetails');
    const riskBadgeEl = document.getElementById('riskBadge');
    
    const score = risk.score || 0;
    const category = risk.category || 'Medium';
    const reasoning = risk.reasoning || 'Standard assessment';
    
    // Update score value
    if (scoreValueEl) {
        scoreValueEl.textContent = score;
        scoreValueEl.style.color = getRiskColor(score);
    }
    
    // Update circular progress
    if (scoreProgressEl) {
        const circumference = 2 * Math.PI * 54;
        const offset = circumference - (score / 10) * circumference;
        scoreProgressEl.style.strokeDashoffset = offset;
        scoreProgressEl.style.stroke = getRiskColor(score);
        
        // Animate
        setTimeout(() => {
            scoreProgressEl.style.transition = 'stroke-dashoffset 1s ease-out, stroke 0.5s ease';
        }, 100);
    }
    
    // Update badge
    if (riskBadgeEl) {
        riskBadgeEl.textContent = category;
        riskBadgeEl.className = `badge badge-${getRiskBadgeClass(category)}`;
    }
    
    // Update details
    if (riskDetailsEl) {
        riskDetailsEl.innerHTML = `
            <div style="margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <i class="fas fa-tag" style="color: var(--primary);"></i>
                    <strong>Category:</strong>
                </div>
                <div style="padding-left: 1.75rem;">
                    <span class="badge badge-${getRiskBadgeClass(category)}">${escapeHtml(category)}</span>
                </div>
            </div>
            <div>
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <i class="fas fa-brain" style="color: var(--primary);"></i>
                    <strong>Reasoning:</strong>
                </div>
                <p style="padding-left: 1.75rem; color: var(--text-secondary); line-height: 1.6; margin: 0;">
                    ${escapeHtml(reasoning)}
                </p>
            </div>
        `;
    }
}

// Display Diagnosis Suggestions
function displayDiagnosisSuggestions(diagnoses) {
    const container = document.getElementById('diagnosisResult');
    if (!container) return;
    
    // Handle both array and object formats
    const diagnosesList = Array.isArray(diagnoses) ? diagnoses : (diagnoses.possible_diagnoses || []);
    
    if (diagnosesList.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-muted); padding: 2rem;">No specific diagnosis suggestions available at this time.</p>';
        return;
    }
    
    container.innerHTML = `
        <div class="diagnosis-grid">
            ${diagnosesList.map((diagnosis, index) => {
                const condition = diagnosis.Condition || diagnosis.condition || 'Unknown Condition';
                const likelihood = diagnosis.Likelihood || diagnosis.likelihood || 'Unknown';
                const explanation = diagnosis.Explanation || diagnosis.explanation || 'No explanation provided';
                const medications = diagnosis.Medications || diagnosis.medications || [];
                const whenToSeeDoctor = diagnosis['When to See Doctor'] || diagnosis.when_to_see_doctor || '';
                
                return `
                    <div class="diagnosis-item">
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
                            <h4 style="margin: 0; font-size: 1.25rem; color: var(--text-primary); display: flex; align-items: center; gap: 0.5rem;">
                                <span style="width: 30px; height: 30px; background: linear-gradient(135deg, var(--primary), var(--primary-light)); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.875rem; font-weight: 700;">${index + 1}</span>
                                ${escapeHtml(condition)}
                            </h4>
                            <span class="badge badge-${getLikelihoodBadgeClass(likelihood)}">
                                ${escapeHtml(likelihood)} Likelihood
                            </span>
                        </div>
                        
                        <div style="margin-bottom: 1rem;">
                            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                                <i class="fas fa-info-circle" style="color: var(--info);"></i>
                                <strong style="color: var(--text-primary);">Explanation:</strong>
                            </div>
                            <p style="padding-left: 1.75rem; color: var(--text-secondary); line-height: 1.6; margin: 0;">
                                ${escapeHtml(explanation)}
                            </p>
                        </div>
                        
                        ${medications.length > 0 ? `
                            <div style="margin-bottom: 1rem;">
                                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
                                    <i class="fas fa-pills" style="color: var(--secondary);"></i>
                                    <strong style="color: var(--text-primary);">Recommended Medications:</strong>
                                </div>
                                <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                                    ${medications.map(med => {
                                        const name = med.Name || med.name || 'Unknown Medication';
                                        const type = med.Type || med.type || 'N/A';
                                        const purpose = med.Purpose || med.purpose || 'N/A';
                                        const dosage = med.Dosage || med.dosage || '';
                                        
                                        return `
                                            <div class="medication-item">
                                                <div style="display: flex; align-items: start; justify-content: space-between; margin-bottom: 0.5rem;">
                                                    <strong style="color: var(--text-primary); font-size: 1rem;">
                                                        ${escapeHtml(name)}
                                                    </strong>
                                                    <span class="badge ${type === 'Prescription' ? 'badge-warning' : 'badge-success'}" style="font-size: 0.75rem;">
                                                        ${escapeHtml(type)}
                                                    </span>
                                                </div>
                                                <div style="color: var(--text-secondary); font-size: 0.875rem; margin-bottom: 0.25rem;">
                                                    <strong>Purpose:</strong> ${escapeHtml(purpose)}
                                                </div>
                                                ${dosage ? `
                                                    <div style="color: var(--text-secondary); font-size: 0.875rem;">
                                                        <strong>Dosage:</strong> ${escapeHtml(dosage)}
                                                    </div>
                                                ` : ''}
                                            </div>
                                        `;
                                    }).join('')}
                                </div>
                            </div>
                        ` : ''}
                        
                        ${whenToSeeDoctor ? `
                            <div style="background: #fff3cd; padding: 1rem; border-radius: var(--radius-md); border-left: 4px solid var(--warning);">
                                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                                    <i class="fas fa-exclamation-triangle" style="color: var(--warning);"></i>
                                    <strong style="color: #856404;">When to See a Doctor:</strong>
                                </div>
                                <p style="margin: 0; color: #856404; line-height: 1.6; padding-left: 1.75rem;">
                                    ${escapeHtml(whenToSeeDoctor)}
                                </p>
                            </div>
                        ` : ''}
                    </div>
                `;
            }).join('')}
        </div>
        
        <div style="margin-top: 1.5rem; padding: 1.25rem; background: #dbeafe; border-radius: var(--radius-md); border-left: 4px solid var(--info);">
            <div style="display: flex; align-items: start; gap: 0.75rem;">
                <i class="fas fa-info-circle" style="color: var(--info); font-size: 1.25rem; margin-top: 0.25rem;"></i>
                <div>
                    <strong style="color: #1e40af; display: block; margin-bottom: 0.5rem;">Important Disclaimer:</strong>
                    <p style="margin: 0; color: #1e40af; line-height: 1.6; font-size: 0.9375rem;">
                        These are AI-generated suggestions based on symptoms. Always consult with a healthcare professional for proper diagnosis and treatment. Do not self-medicate without professional guidance.
                    </p>
                </div>
            </div>
        </div>
    `;
}

function getLikelihoodBadgeClass(likelihood) {
    const likelihoodLower = (likelihood || '').toLowerCase();
    if (likelihoodLower.includes('high')) return 'danger';
    if (likelihoodLower.includes('medium')) return 'warning';
    return 'info';
}

// Display Triage Recommendation
function displayTriageRecommendation(triage) {
    const actionEl = document.getElementById('triageAction');
    const detailsEl = document.getElementById('triageDetails');
    
    if (!actionEl || !detailsEl) return;
    
    const action = triage.action || 'Schedule Appointment';
    const timeframe = triage.timeframe || 'Next available';
    const specialist = triage.specialist || 'General Practice';
    
    actionEl.innerHTML = `
        <i class="fas fa-ambulance" style="margin-right: 0.5rem;"></i>
        ${escapeHtml(action)}
    `;
    
    detailsEl.innerHTML = `
        <div class="triage-detail-item">
            <i class="fas fa-clock"></i>
            <span><strong>Timeframe:</strong> ${escapeHtml(timeframe)}</span>
        </div>
        <div class="triage-detail-item">
            <i class="fas fa-user-md"></i>
            <span><strong>Recommended Specialist:</strong> ${escapeHtml(specialist)}</span>
        </div>
    `;
}

// Display Web Guidelines
function displayWebGuidelines(webInfo) {
    const card = document.getElementById('webGuidelinesCard');
    const container = document.getElementById('webGuidelinesResult');
    
    if (!card || !container) return;
    
    const results = webInfo.results || [];
    
    if (results.length === 0) {
        card.style.display = 'none';
        return;
    }
    
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 1rem;">
            ${results.map((result, index) => `
                <div style="background: var(--bg-primary); padding: 1.25rem; border-radius: var(--radius-md); border: 1px solid var(--border-color); transition: all var(--transition-base); cursor: pointer;" 
                     onmouseover="this.style.borderColor='var(--primary)'; this.style.transform='translateX(4px)'"
                     onmouseout="this.style.borderColor='var(--border-color)'; this.style.transform='translateX(0)'">
                    <a href="${escapeHtml(result.link)}" target="_blank" rel="noopener noreferrer" 
                       style="color: var(--primary); text-decoration: none; font-weight: 600; display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
                        ${escapeHtml(result.title)}
                        <i class="fas fa-external-link-alt" style="font-size: 0.875rem;"></i>
                    </a>
                    <p style="color: var(--text-secondary); font-size: 0.9375rem; line-height: 1.6; margin: 0 0 0.5rem 0;">
                        ${escapeHtml(result.snippet)}
                    </p>
                    <a href="${escapeHtml(result.link)}" target="_blank" rel="noopener noreferrer" 
                       style="color: var(--text-muted); font-size: 0.8125rem; text-decoration: none;">
                        ${escapeHtml(result.link)}
                    </a>
                </div>
            `).join('')}
        </div>
        <div style="margin-top: 1rem; padding: 1rem; background: var(--bg-tertiary); border-radius: var(--radius-md); font-size: 0.875rem; color: var(--text-secondary);">
            <i class="fas fa-info-circle" style="margin-right: 0.5rem;"></i>
            <strong>Note:</strong> These guidelines are sourced from the web and should be used as reference. Always consult with healthcare professionals for medical decisions.
        </div>
    `;
    
    card.style.display = 'block';
}

// View Patient History
async function handleViewHistory() {
    if (!currentPatientId) {
        showToast('Please process a patient query first', 'warning');
        return;
    }
    
    showModal(historyModal);
    showToast('Loading patient history...', 'info');
    
    try {
        const response = await fetch(`${API_BASE_URL}/history/${currentPatientId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        displayPatientHistory(data);
        showToast('Patient history loaded', 'success');
        
    } catch (error) {
        console.error('Error fetching history:', error);
        showToast(`Failed to fetch patient history: ${error.message}`, 'error');
    }
}

// Display Patient History
function displayPatientHistory(data) {
    const container = document.getElementById('historyContent');
    if (!container) return;
    
    const facts = data.stored_facts || {};
    
    if (Object.keys(facts).length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-muted); padding: 2rem;">No history found for this patient.</p>';
    } else {
        container.innerHTML = Object.entries(facts)
            .filter(([key]) => !key.endsWith('_timestamp'))
            .map(([key, value]) => `
                <div style="background: var(--bg-secondary); padding: 1.5rem; border-radius: var(--radius-md); margin-bottom: 1rem; border-left: 4px solid var(--primary);">
                    <h3 style="margin-bottom: 1rem; color: var(--text-primary); font-size: 1.1rem;">
                        ${escapeHtml(key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()))}
                    </h3>
                    <pre style="margin: 0; white-space: pre-wrap; font-family: inherit; background: var(--bg-primary); padding: 1rem; border-radius: var(--radius-sm); font-size: 0.875rem; line-height: 1.6; color: var(--text-secondary);">${escapeHtml(JSON.stringify(value, null, 2))}</pre>
                </div>
            `).join('');
    }
}

// View Metrics
async function handleViewMetrics() {
    showModal(metricsModal);
    showToast('Loading system metrics...', 'info');
    
    try {
        const response = await fetch(`${API_BASE_URL}/observability`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        displayMetrics(data);
        showToast('Metrics loaded', 'success');
        
    } catch (error) {
        console.error('Error fetching metrics:', error);
        showToast(`Failed to fetch metrics: ${error.message}`, 'error');
    }
}

// Display Metrics
function displayMetrics(data) {
    const container = document.getElementById('metricsContent');
    if (!container) return;
    
    const metrics = data.metrics || {};
    const avgLatencies = data.average_latencies || {};
    
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 2rem;">
            <div>
                <h3 style="margin-bottom: 1rem; color: var(--text-primary); font-size: 1.25rem; display: flex; align-items: center; gap: 0.5rem;">
                    <i class="fas fa-tachometer-alt" style="color: var(--primary);"></i>
                    Performance Metrics
                </h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                    ${Object.entries(avgLatencies).map(([key, value]) => `
                        <div style="background: var(--bg-secondary); padding: 1.5rem; border-radius: var(--radius-md); border-left: 4px solid var(--primary);">
                            <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                                ${escapeHtml(key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()))}
                            </div>
                            <div style="font-size: 2rem; font-weight: 700; color: var(--primary);">
                                ${value.toFixed(2)}s
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <div>
                <h3 style="margin-bottom: 1rem; color: var(--text-primary); font-size: 1.25rem; display: flex; align-items: center; gap: 0.5rem;">
                    <i class="fas fa-chart-bar" style="color: var(--primary);"></i>
                    System Metrics
                </h3>
                <div style="background: var(--bg-secondary); padding: 1.5rem; border-radius: var(--radius-md);">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                        <div>
                            <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Mis-triage Count</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: var(--danger);">${data.mistriage_count || 0}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Bias Detected</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: var(--warning);">${data.bias_detected_count || 0}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Trace Count</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: var(--info);">${data.trace_count || 0}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Utility Functions
function setLoading(loading) {
    const btnContent = submitBtn.querySelector('.btn-content');
    const btnLoader = submitBtn.querySelector('.btn-loader');
    
    if (loading) {
        btnContent.style.display = 'none';
        btnLoader.style.display = 'flex';
        submitBtn.disabled = true;
    } else {
        btnContent.style.display = 'flex';
        btnLoader.style.display = 'none';
        submitBtn.disabled = false;
    }
}

function hideResults() {
    resultsSection.style.display = 'none';
}

function showWarning(message) {
    const warningEl = document.getElementById('warningAlert');
    if (warningEl) {
        const span = warningEl.querySelector('span');
        if (span) {
            span.textContent = message;
        }
        warningEl.style.display = 'flex';
    }
}

function showModal(modal) {
    modal.style.display = 'flex';
}

function hideModal(modal) {
    modal.style.display = 'none';
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    toast.innerHTML = `
        <i class="fas ${icons[type] || icons.info}"></i>
        <span>${escapeHtml(message)}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.4s ease-out reverse';
        setTimeout(() => {
            toast.remove();
        }, 400);
    }, 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getSeverityBadgeClass(severity) {
    const severityLower = (severity || '').toLowerCase();
    if (severityLower.includes('high')) return 'danger';
    if (severityLower.includes('medium')) return 'warning';
    return 'info';
}

function getRiskBadgeClass(category) {
    const categoryLower = (category || '').toLowerCase();
    if (categoryLower.includes('high')) return 'danger';
    if (categoryLower.includes('medium')) return 'warning';
    return 'success';
}

function getRiskColor(score) {
    if (score >= 8) return '#ff5252'; // red
    if (score >= 5) return '#ffa726'; // orange
    return '#00a86b'; // green
}
