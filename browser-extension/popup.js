/**
 * Phish Hunter AI — Extension Popup Script
 * Handles UI interactions, API calls, and result rendering.
 */

const API_URL = 'http://localhost:5000/api/analyze';
const CIRCUMFERENCE = 2 * Math.PI * 32; // r=32

// Elements
const textarea = document.getElementById('popup-input');
const charCount = document.getElementById('char-count');
const btnAnalyze = document.getElementById('btn-analyze');
const btnText = document.getElementById('btn-text');
const btnSpinner = document.getElementById('btn-spinner');
const btnScanPage = document.getElementById('btn-scan-page');
const resultSection = document.getElementById('result-section');
const errorBox = document.getElementById('error-box');
const errorText = document.getElementById('error-text');

// Result elements
const ringFill = document.getElementById('ring-fill');
const probText = document.getElementById('prob-text');
const riskBadge = document.getElementById('risk-badge');
const resultTitle = document.getElementById('result-title');
const explanationText = document.getElementById('explanation-text');
const tagsContainer = document.getElementById('tags-container');

// ---- Char counter ----
textarea.addEventListener('input', () => {
    const len = textarea.value.length;
    charCount.textContent = len;
    charCount.style.color = len > 2700 ? '#f59e0b' : '';
    btnAnalyze.disabled = len === 0;
});

// ---- Ctrl+Enter shortcut ----
textarea.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) analyze();
});

// ---- Scan current page URL ----
btnScanPage.addEventListener('click', async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab?.url) {
        textarea.value = tab.url;
        charCount.textContent = tab.url.length;
        btnAnalyze.disabled = false;
        textarea.focus();
    }
});

// ---- Analyze button ----
btnAnalyze.addEventListener('click', analyze);

// ---- On load: check if background set pending text (from context menu) ----
document.addEventListener('DOMContentLoaded', async () => {
    const stored = await chrome.storage.local.get('pendingText');
    if (stored.pendingText) {
        textarea.value = stored.pendingText;
        charCount.textContent = stored.pendingText.length;
        btnAnalyze.disabled = false;
        await chrome.storage.local.remove('pendingText');
        // Auto-analyze for context-menu triggered flow
        analyze();
    }
});

// ---- Core analyze function ----
async function analyze() {
    const text = textarea.value.trim();
    if (!text) return;

    setLoading(true);
    hideResult();
    hideError();

    try {
        const res = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text }),
        });

        // Get response text first to handle empty or non-JSON responses
        const responseText = await res.text();

        if (!responseText || !responseText.trim()) {
            throw new Error('Empty response from server. Make sure Flask is running on port 5000.');
        }

        let data;
        try {
            data = JSON.parse(responseText);
        } catch (parseError) {
            throw new Error(`Server returned invalid response: ${responseText.substring(0, 100)}`);
        }

        if (!res.ok) throw new Error(data.error || `Analysis failed with status ${res.status}`);

        showResult(data);
    } catch (err) {
        if (err.message.includes('fetch') || err.message.includes('Failed to fetch')) {
            showError('Cannot reach Phish Hunter AI server. Make sure Flask is running on port 5000.');
        } else {
            showError(err.message);
        }
    } finally {
        setLoading(false);
    }
}

// ---- UI helpers ----
function setLoading(on) {
    btnText.classList.toggle('hidden', on);
    btnSpinner.classList.toggle('hidden', !on);
    btnAnalyze.disabled = on;
}

function hideResult() {
    resultSection.classList.add('hidden');
}

function hideError() {
    errorBox.classList.add('hidden');
}

function showError(msg) {
    errorText.textContent = msg;
    errorBox.classList.remove('hidden');
}

function showResult(data) {
    const { probability, risk_level, explanation, flagged_keywords, suspicious_domains, urgency_phrases } = data;

    // Risk config
    const config = getRiskConfig(risk_level);

    // Ring
    const offset = CIRCUMFERENCE - (probability / 100) * CIRCUMFERENCE;
    ringFill.style.stroke = config.color;
    ringFill.style.strokeDashoffset = CIRCUMFERENCE; // reset
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            ringFill.style.strokeDashoffset = offset;
        });
    });

    probText.textContent = `${probability}%`;
    probText.style.color = config.color;

    // Badge
    riskBadge.textContent = `${config.icon} ${risk_level}`;
    riskBadge.className = `risk-badge ${config.badgeClass}`;

    // Title
    resultTitle.textContent = config.title;

    // Explanation
    explanationText.textContent = explanation;

    // Tags
    tagsContainer.innerHTML = '';
    (flagged_keywords || []).forEach(kw => addTag(kw, 'keyword', '⚠'));
    (urgency_phrases || []).forEach(ph => addTag(ph, 'urgency', '⏰'));
    (suspicious_domains || []).forEach(dm => addTag(dm, 'domain', '🔗'));

    resultSection.classList.remove('hidden');
}

function addTag(text, type, icon) {
    const span = document.createElement('span');
    span.className = `tag tag-${type}`;
    span.textContent = `${icon} ${text}`;
    tagsContainer.appendChild(span);
}

function getRiskConfig(risk_level) {
    switch (risk_level) {
        case 'DANGEROUS':
            return { color: '#ef4444', badgeClass: 'dangerous', icon: '🚨', title: 'Dangerous — High Scam Risk' };
        case 'SUSPICIOUS':
            return { color: '#f59e0b', badgeClass: 'suspicious', icon: '⚠️', title: 'Suspicious — Proceed with Caution' };
        default:
            return { color: '#10b981', badgeClass: 'safe', icon: '✅', title: 'Safe — No Threats Detected' };
    }
}
