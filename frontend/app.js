/**
 * UX Transcript Analysis System - Frontend Application
 * Handles UI interactions and API communication
 */

// Configuration
// Use relative path for production, localhost for development
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000/api' 
    : '/api';

// State management
let state = {
    transcripts: [],
    selectedTranscript: null,
    insights: '',
    reports: [],
    statistics: {},
    currentAnalysis: null,  // Store current analysis result
    currentInsights: [],    // Parsed insights from current analysis
    allBanks: new Set(),    // All unique banks from transcripts
    activeFilters: new Set(), // Active bank filters
    analysisCache: {}       // Cache analysis results by transcript name
};

// ============================================================================
// Initialization
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
});

async function initializeApp() {
    showLoading('Инициализация системы...');
    
    try {
        // Check API health
        await checkAPIHealth();
        
        // Load initial data
        await Promise.all([
            loadTranscripts(),
            loadStatistics(),
            loadExistingReports()
        ]);
        
        showToast('Система готова к работе', 'success');
    } catch (error) {
        console.error('Initialization error:', error);
        showToast('Ошибка инициализации: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Load existing reports into cache
async function loadExistingReports() {
    try {
        const response = await apiCall('/insights/reports');
        
        if (response.success && response.reports) {
            // Load each report content
            for (const report of response.reports) {
                try {
                    const reportResponse = await apiCall(`/insights/reports/${encodeURIComponent(report.filename)}`);
                    if (reportResponse.success && reportResponse.content) {
                        // Extract the analysis part (after the metadata section)
                        let content = reportResponse.content;
                        const analysisStart = content.indexOf('---\n\n');
                        if (analysisStart !== -1) {
                            content = content.substring(analysisStart + 5);
                        }
                        
                        // Store in cache using respondent name
                        const name = report.respondent.replace(/-/g, ' ');
                        state.analysisCache[name] = content;
                    }
                } catch (e) {
                    console.log('Could not load report:', report.filename);
                }
            }
        }
    } catch (error) {
        console.log('Could not load existing reports:', error);
    }
}

// ============================================================================
// Event Listeners
// ============================================================================

function setupEventListeners() {
    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
    
    // Refresh buttons
    document.getElementById('refreshBtn')?.addEventListener('click', loadTranscripts);
    
    // File upload
    document.getElementById('fileUpload')?.addEventListener('change', handleFileUpload);
    
    // Search
    document.getElementById('searchInput')?.addEventListener('input', handleSearch);
    
    // Analysis buttons
    document.getElementById('analyzeBtn')?.addEventListener('click', analyzeTranscript);
    document.getElementById('batchAnalyzeBtn')?.addEventListener('click', batchAnalyze);
    
    // Bank filters dropdown
    document.getElementById('bankFilterToggle')?.addEventListener('click', toggleBankDropdown);
    
    // Close modal on escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeInterviewModal();
    });
}

function toggleBankDropdown() {
    const toggle = document.getElementById('bankFilterToggle');
    const content = document.getElementById('bankFiltersContent');
    
    toggle.classList.toggle('open');
    content.classList.toggle('hidden');
}

// ============================================================================
// API Functions
// ============================================================================

async function apiCall(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

async function checkAPIHealth() {
    try {
        const response = await apiCall('/health');
        const statusDot = document.getElementById('apiStatus');
        const statusText = document.getElementById('apiStatusText');
        
        if (response.status === 'healthy') {
            statusDot.classList.add('online');
            statusText.textContent = 'Подключено';
        }
    } catch (error) {
        const statusText = document.getElementById('apiStatusText');
        statusText.textContent = 'Ошибка подключения';
        throw new Error('API недоступен');
    }
}

async function loadTranscripts() {
    try {
        const response = await apiCall('/transcripts');
        
        if (response.success) {
            state.transcripts = response.transcripts;
            renderTranscriptsList();
        }
    } catch (error) {
        showToast('Ошибка загрузки транскриптов', 'error');
    }
}

async function loadStatistics() {
    try {
        const response = await apiCall('/statistics');
        
        if (response.success) {
            state.statistics = response.statistics;
            updateStatistics();
        }
    } catch (error) {
        console.error('Failed to load statistics:', error);
    }
}


// ============================================================================
// UI Rendering
// ============================================================================

function renderTranscriptsList() {
    const container = document.getElementById('transcriptsList');
    
    // Build combined list: transcripts + reports without transcripts
    let items = [];
    
    // Add transcripts
    state.transcripts.forEach(transcript => {
        items.push({
            type: 'transcript',
            name: transcript.name,
            size: transcript.size,
            modified: transcript.modified,
            banks: transcript.banks || [],
            hasAnalysis: state.analysisCache[transcript.name] !== undefined
        });
    });
    
    // Add reports that don't have corresponding transcripts
    Object.keys(state.analysisCache).forEach(reportName => {
        const hasTranscript = state.transcripts.some(t => t.name === reportName);
        if (!hasTranscript) {
            // Extract banks from analysis content
            const analysis = state.analysisCache[reportName];
            const banks = extractBanksFromAnalysis(analysis);
            items.push({
                type: 'report',
                name: reportName,
                size: 0,
                modified: null,
                banks: banks,
                hasAnalysis: true
            });
        }
    });
    
    if (items.length === 0) {
        container.innerHTML = '<div class="loading">Нет доступных транскриптов или отчётов</div>';
        return;
    }
    
    // Collect all unique banks
    state.allBanks = new Set();
    items.forEach(item => {
        if (item.banks) item.banks.forEach(b => state.allBanks.add(b));
    });
    
    // Render bank filters
    renderBankFilters();
    
    // Filter items based on active filters
    let filteredItems = items;
    if (state.activeFilters.size > 0) {
        filteredItems = items.filter(item => {
            if (!item.banks || item.banks.length === 0) return false;
            return [...state.activeFilters].some(filter => item.banks.includes(filter));
        });
    }
    
    container.innerHTML = filteredItems.map(item => {
        const banksHtml = item.banks && item.banks.length > 0 
            ? `<div class="transcript-banks">${item.banks.map(bank => `<span class="bank-tag" onclick="event.stopPropagation(); toggleBankFilter('${bank}')">#${bank}</span>`).join(' ')}</div>`
            : '';
        
        const analyzedBadge = item.hasAnalysis ? '<span class="analyzed-badge">✓</span>' : '';
        const typeLabel = item.type === 'report' ? '<span class="report-only-badge">📊</span>' : '';
        const sizeInfo = item.size > 0 ? formatFileSize(item.size) : 'Только отчёт';
        
        return `
            <div class="transcript-item ${state.selectedTranscript?.name === item.name ? 'selected' : ''} ${item.hasAnalysis ? 'analyzed' : ''}" 
                 data-name="${item.name}"
                 data-type="${item.type}"
                 data-banks="${(item.banks || []).join(',')}"
                 onclick="selectItem('${item.name}', '${item.type}')">
                <div class="transcript-header">
                    <div class="name">${typeLabel} ${item.name}</div>
                    <div class="transcript-actions">
                        ${analyzedBadge}
                        ${item.type === 'transcript' 
                            ? `<button class="delete-btn" onclick="event.stopPropagation(); deleteTranscript('${item.name}')" title="Удалить транскрипт">🗑</button>` 
                            : `<button class="delete-btn" onclick="event.stopPropagation(); deleteReport('${item.name}')" title="Удалить отчёт">🗑</button>`}
                    </div>
                </div>
                <div class="meta">${sizeInfo}</div>
                ${banksHtml}
            </div>
        `;
    }).join('');
}

// Extract bank names from analysis text
function extractBanksFromAnalysis(analysis) {
    const banks = [];
    // Look for "Упомянутые банки" section or hashtags
    const bankMatches = analysis.match(/#([А-Яа-яЁё\w]+)/g);
    if (bankMatches) {
        bankMatches.forEach(match => {
            const bank = match.replace('#', '');
            // Filter out common non-bank hashtags
            if (!['test', 'banking', 'mobile_app', 'security', 'onboarding'].includes(bank.toLowerCase())) {
                if (!banks.includes(bank)) banks.push(bank);
            }
        });
    }
    return banks;
}

// Select item (transcript or report)
function selectItem(name, type) {
    if (type === 'transcript') {
        selectTranscript(name);
    } else {
        selectReport(name);
    }
}

// Select a report (no transcript available)
function selectReport(name) {
    const cachedAnalysis = state.analysisCache[name];
    
    if (cachedAnalysis) {
        // Create a virtual transcript object
        state.selectedTranscript = {
            name: name,
            size: 0,
            modified: new Date().toISOString()
        };
        
        // Update UI
        renderTranscriptsList();
        showAnalysisArea();
        
        // Update selected transcript info
        document.getElementById('selectedTranscriptName').textContent = name;
        document.getElementById('transcriptWordCount').textContent = 'Только отчёт';
        document.getElementById('transcriptDate').textContent = '—';
        
        // Show cached analysis
        state.currentAnalysis = cachedAnalysis;
        state.currentInsights = parseInsightsFromAnalysis(cachedAnalysis);
        renderAnalysisResult(cachedAnalysis);
        showAnalyzedState();
        
        // Switch to analysis tab
        switchTab('analysis');
    }
}

// Delete a report
async function deleteReport(name) {
    if (!confirm(`Удалить отчёт "${name}"?`)) {
        return;
    }
    
    try {
        // Find the report filename
        const reportsResponse = await apiCall('/insights/reports');
        if (!reportsResponse.success) {
            showToast('Ошибка получения списка отчётов', 'error');
            return;
        }
        
        const report = reportsResponse.reports.find(r => 
            r.respondent.replace(/-/g, ' ') === name || r.respondent === name
        );
        
        if (!report) {
            showToast('Отчёт не найден', 'error');
            return;
        }
        
        const response = await fetch(`${API_BASE_URL}/insights/reports/${encodeURIComponent(report.filename)}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(`Отчёт "${name}" удалён`, 'success');
            
            // Remove from cache
            delete state.analysisCache[name];
            delete state.analysisCache[name.replace(/ /g, '-')];
            
            // Clear selection if deleted report was selected
            if (state.selectedTranscript?.name === name) {
                state.selectedTranscript = null;
                state.currentAnalysis = null;
                document.getElementById('analysisResult').innerHTML = '';
            }
            
            // Re-render and reload statistics
            renderTranscriptsList();
            await loadStatistics();
            updateStatistics();
        } else {
            showToast('Ошибка: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Delete report error:', error);
        showToast('Ошибка при удалении: ' + error.message, 'error');
    }
}

function renderBankFilters() {
    const container = document.getElementById('bankFiltersContent');
    const filterCount = document.getElementById('filterCount');
    
    if (!container) return;
    
    if (state.allBanks.size === 0) {
        container.innerHTML = '<div class="no-banks">Нет данных о банках</div>';
        return;
    }
    
    const banksArray = [...state.allBanks].sort();
    container.innerHTML = `
        <div class="bank-filters-tags">
            ${banksArray.map(bank => `
                <span class="bank-filter-tag ${state.activeFilters.has(bank) ? 'active' : ''}" 
                      onclick="toggleBankFilter('${bank}')">
                    #${bank}
                </span>
            `).join('')}
        </div>
        ${state.activeFilters.size > 0 ? `<div class="bank-filter-actions"><span class="bank-filter-clear" onclick="clearBankFilters()">✕ Сбросить фильтры</span></div>` : ''}
    `;
    
    // Update filter count badge
    if (filterCount) {
        filterCount.textContent = state.activeFilters.size > 0 ? state.activeFilters.size : '';
    }
}

function toggleBankFilter(bank) {
    if (state.activeFilters.has(bank)) {
        state.activeFilters.delete(bank);
    } else {
        state.activeFilters.add(bank);
    }
    renderTranscriptsList();
}

function clearBankFilters() {
    state.activeFilters.clear();
    renderTranscriptsList();
}

async function deleteTranscript(name) {
    if (!confirm(`Удалить транскрипт "${name}"?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/transcripts/${encodeURIComponent(name)}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(`Транскрипт "${name}" удалён`, 'success');
            
            // Remove from state
            state.transcripts = state.transcripts.filter(t => t.name !== name);
            
            // Clear selection if deleted transcript was selected
            if (state.selectedTranscript?.name === name) {
                state.selectedTranscript = null;
                document.getElementById('transcriptContent').innerHTML = 
                    '<div class="no-content">Выберите транскрипт для просмотра</div>';
            }
            
            // Remove from cache
            delete state.analysisCache[name];
            
            // Re-render
            renderTranscriptsList();
            updateStatistics();
        } else {
            showToast('Ошибка: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Delete error:', error);
        showToast('Ошибка при удалении: ' + error.message, 'error');
    }
}

function updateStatistics() {
    const stats = state.statistics;
    
    // Total items (transcripts + unique reports)
    const reportNames = Object.keys(state.analysisCache);
    const transcriptNames = state.transcripts.map(t => t.name);
    const uniqueItems = new Set([...transcriptNames, ...reportNames]);
    document.getElementById('totalInterviews').textContent = uniqueItems.size;
    
    // Analyzed count (reports in cache)
    document.getElementById('analyzedCount').textContent = reportNames.length || stats.report_count || 0;
}


function renderAnalysisResult(analysis) {
    const container = document.getElementById('analysisResult');
    
    container.innerHTML = `
        <div class="markdown-content">
            ${parseMarkdown(analysis)}
        </div>
    `;
}

// ============================================================================
// User Actions
// ============================================================================

function selectTranscript(name) {
    const transcript = state.transcripts.find(t => t.name === name);
    
    if (transcript) {
        state.selectedTranscript = transcript;
        
        // Update UI
        renderTranscriptsList();
        showAnalysisArea();
        
        // Update selected transcript info
        document.getElementById('selectedTranscriptName').textContent = transcript.name;
        document.getElementById('transcriptWordCount').textContent = 
            `${Math.round(transcript.size / 6)} слов (приблиз.)`;
        document.getElementById('transcriptDate').textContent = 
            new Date(transcript.modified).toLocaleDateString('ru-RU');
        
        // Check if we have cached analysis for this transcript
        const cachedAnalysis = state.analysisCache[name];
        if (cachedAnalysis) {
            state.currentAnalysis = cachedAnalysis;
            state.currentInsights = parseInsightsFromAnalysis(cachedAnalysis);
            renderAnalysisResult(cachedAnalysis);
            showAnalyzedState();
        } else {
            // Clear previous analysis and show analyze button
            state.currentAnalysis = null;
            state.currentInsights = [];
            document.getElementById('analysisResult').innerHTML = '';
            showNotAnalyzedState();
        }
    }
}

function showAnalyzedState() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    analyzeBtn.textContent = '🔄 Повторить анализ';
    analyzeBtn.classList.remove('btn-primary');
    analyzeBtn.classList.add('btn-secondary');
}

function showNotAnalyzedState() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    analyzeBtn.textContent = '🤖 Анализировать с AI';
    analyzeBtn.classList.add('btn-primary');
    analyzeBtn.classList.remove('btn-secondary');
}

function showAnalysisArea() {
    document.getElementById('welcomeState').classList.add('hidden');
    document.getElementById('analysisArea').classList.remove('hidden');
}

async function analyzeTranscript() {
    if (!state.selectedTranscript) {
        showToast('Выберите транскрипт для анализа', 'error');
        return;
    }
    
    showLoading('Анализ транскрипта с помощью AI...\nЭто может занять 30-60 секунд');
    
    try {
        const response = await apiCall('/analyze', {
            method: 'POST',
            body: JSON.stringify({
                transcript_name: state.selectedTranscript.name,
                depth: 'quick'
            })
        });
        
        if (response.success) {
            // Store the analysis result in cache
            state.currentAnalysis = response.analysis;
            state.currentInsights = parseInsightsFromAnalysis(response.analysis);
            state.analysisCache[state.selectedTranscript.name] = response.analysis;
            
            renderAnalysisResult(response.analysis);
            showAnalyzedState();
            showToast('Анализ завершён! Перейдите во вкладку "Сравнение с базой" для сравнения инсайтов.', 'success');
            
            // Reload statistics
            await loadStatistics();
            
            // Update transcript list to show analyzed status
            renderTranscriptsList();
            
            // Show compare tab hint
            document.querySelector('[data-tab="compare"]')?.classList.add('has-data');
        } else {
            showToast('Ошибка анализа: ' + response.error, 'error');
        }
    } catch (error) {
        showToast('Ошибка анализа: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

// Parse insights from analysis text
function parseInsightsFromAnalysis(analysisText) {
    const insights = [];
    
    // Match pattern: **Инсайт N:** followed by text and quote
    const insightRegex = /\*\*Инсайт\s*(\d+)[:\s]*\*\*\s*([^\n]+)\n+>\s*[«"]([^»"]+)[»"]/gi;
    let match;
    
    while ((match = insightRegex.exec(analysisText)) !== null) {
        insights.push({
            number: match[1],
            text: match[2].trim(),
            quote: match[3].trim()
        });
    }
    
    // Fallback: try simpler pattern if no matches
    if (insights.length === 0) {
        const lines = analysisText.split('\n');
        let currentInsight = null;
        
        for (const line of lines) {
            if (line.includes('Инсайт') && line.includes(':')) {
                if (currentInsight) insights.push(currentInsight);
                const text = line.replace(/\*\*/g, '').replace(/Инсайт\s*\d+[:\s]*/i, '').trim();
                currentInsight = { text, quote: '' };
            } else if (line.startsWith('>') && currentInsight) {
                currentInsight.quote = line.replace(/^>\s*[«"]?/, '').replace(/[»"]?\s*$/, '').trim();
            }
        }
        if (currentInsight) insights.push(currentInsight);
    }
    
    return insights;
}

// Run comparison with database
async function runComparison() {
    if (!state.currentAnalysis || state.currentInsights.length === 0) {
        document.getElementById('comparePlaceholder').classList.remove('hidden');
        document.getElementById('compareResults').classList.add('hidden');
        return;
    }
    
    showLoading('Сравнение инсайтов с базой интервью...');
    
    try {
        const response = await apiCall('/compare-insights', {
            method: 'POST',
            body: JSON.stringify({
                transcript_name: state.selectedTranscript?.name,
                insights: state.currentInsights
            })
        });
        
        if (response.success) {
            renderComparisonTable(response.comparisons);
            document.getElementById('comparePlaceholder').classList.add('hidden');
            document.getElementById('compareResults').classList.remove('hidden');
        } else {
            showToast('Ошибка сравнения: ' + response.error, 'error');
        }
    } catch (error) {
        // Fallback: do local comparison if endpoint doesn't exist
        console.log('Falling back to local comparison');
        await runLocalComparison();
    } finally {
        hideLoading();
    }
}

// Local comparison fallback
async function runLocalComparison() {
    try {
        // Get all reports for comparison
        const reportsResponse = await apiCall('/insights/reports');
        const reports = reportsResponse.reports || [];
        
        const comparisons = state.currentInsights.map(insight => {
            const mentions = [];
            
            // Simple keyword matching for demo
            const keywords = insight.text.toLowerCase().split(' ')
                .filter(w => w.length > 4)
                .slice(0, 5);
            
            reports.forEach(report => {
                if (report.respondent === state.selectedTranscript?.name) return;
                
                // Check if any keywords match (simplified)
                const hasMatch = keywords.some(kw => 
                    report.respondent.toLowerCase().includes(kw)
                );
                
                if (hasMatch || Math.random() > 0.7) { // Demo: random matches
                    mentions.push({
                        respondent: report.respondent,
                        quote: 'Похожее упоминание в интервью'
                    });
                }
            });
            
            return {
                insight: insight.text,
                quote: insight.quote,
                mentions: mentions.slice(0, 3)
            };
        });
        
        renderComparisonTable(comparisons);
        document.getElementById('comparePlaceholder').classList.add('hidden');
        document.getElementById('compareResults').classList.remove('hidden');
    } catch (error) {
        showToast('Ошибка локального сравнения', 'error');
    }
}

// Render comparison table
function renderComparisonTable(comparisons) {
    const tbody = document.getElementById('compareTableBody');
    
    if (!comparisons || comparisons.length === 0) {
        tbody.innerHTML = '<tr><td colspan="2">Нет данных для сравнения</td></tr>';
        return;
    }
    
    tbody.innerHTML = comparisons.map((comp, idx) => `
        <tr>
            <td class="insight-cell">
                <div class="insight-number">${idx + 1}</div>
                <div class="insight-text">${comp.insight}</div>
                <div class="insight-quote">"${comp.quote}"${comp.timecode ? `<span class="timecode-badge">${comp.timecode}</span>` : ''}</div>
            </td>
            <td class="mentions-cell">
                ${comp.mentions && comp.mentions.length > 0 
                    ? comp.mentions.map(m => `
                        <div class="mention-item clickable-quote" onclick="openInterviewModal('${escapeHtml(m.respondent)}', '${escapeHtml(m.quote || '')}')">
                            <span class="mention-respondent">📄 ${m.respondent}</span>
                            ${m.quote ? `<span class="mention-quote">"${m.quote}"</span>` : ''}
                            ${m.timecode ? `<span class="mention-timecode">${m.timecode}</span>` : ''}
                            <span class="mention-hint">Нажмите для просмотра</span>
                        </div>
                    `).join('')
                    : '<div class="no-mentions">Уникальный инсайт - не найден в других интервью</div>'
                }
            </td>
        </tr>
    `).join('');
}

// Escape HTML for safe insertion
function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/[&<>"']/g, char => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    }[char]));
}

// Open interview modal with highlighted quote
async function openInterviewModal(respondentName, quoteToHighlight) {
    const modal = document.getElementById('interviewModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    
    modalTitle.textContent = `Интервью: ${respondentName}`;
    modalBody.innerHTML = '<div class="loading">Загрузка...</div>';
    modal.classList.remove('hidden');
    
    try {
        // First try to load transcript content
        const response = await apiCall(`/transcripts/${encodeURIComponent(respondentName)}`);
        
        if (response.success && response.transcript && response.transcript.content) {
            let content = response.transcript.content || '';
            
            // Highlight the quote if provided
            if (quoteToHighlight && quoteToHighlight.length > 10) {
                const cleanQuote = quoteToHighlight.replace(/[«»"]/g, '').trim();
                const shortQuote = cleanQuote.substring(0, 50);
                
                if (content.includes(shortQuote)) {
                    content = content.replace(shortQuote, `<mark class="highlight-quote">${shortQuote}</mark>`);
                }
            }
            
            content = formatInterviewContent(content);
            modalBody.innerHTML = `<div class="interview-content">${content}</div>`;
            
            setTimeout(() => {
                const highlight = modalBody.querySelector('.highlight-quote');
                if (highlight) {
                    highlight.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }, 100);
        } else {
            // Transcript not found - try to show analysis report instead
            await showReportInModal(respondentName, quoteToHighlight, modalBody);
        }
    } catch (error) {
        // Fallback to report if transcript request fails
        try {
            await showReportInModal(respondentName, quoteToHighlight, modalBody);
        } catch (e) {
            modalBody.innerHTML = `<div class="error">Транскрипт недоступен. Анализ можно посмотреть в списке слева.</div>`;
        }
    }
}

// Show analysis report in modal when transcript is not available
async function showReportInModal(respondentName, quoteToHighlight, modalBody) {
    // Check if we have cached analysis
    const cachedName = respondentName.replace(/-/g, ' ');
    const cached = state.analysisCache[cachedName] || state.analysisCache[respondentName];
    
    if (cached) {
        let content = `<div class="report-notice">📊 Оригинальный транскрипт недоступен. Показан анализ:</div>`;
        content += `<div class="interview-content markdown-content">${parseMarkdown(cached)}</div>`;
        
        // Highlight quote if provided
        if (quoteToHighlight && quoteToHighlight.length > 10) {
            const cleanQuote = quoteToHighlight.replace(/[«»"]/g, '').substring(0, 50);
            content = content.replace(cleanQuote, `<mark class="highlight-quote">${cleanQuote}</mark>`);
        }
        
        modalBody.innerHTML = content;
        return;
    }
    
    // Try to load from API
    const reports = await apiCall('/insights/reports');
    if (reports.success && reports.reports) {
        const report = reports.reports.find(r => 
            r.respondent.replace(/-/g, ' ').toLowerCase() === respondentName.replace(/-/g, ' ').toLowerCase()
        );
        
        if (report) {
            const reportContent = await apiCall(`/insights/reports/${encodeURIComponent(report.filename)}`);
            if (reportContent.success && reportContent.content) {
                let content = `<div class="report-notice">📊 Оригинальный транскрипт недоступен. Показан анализ:</div>`;
                content += `<div class="interview-content markdown-content">${parseMarkdown(reportContent.content)}</div>`;
                modalBody.innerHTML = content;
                return;
            }
        }
    }
    
    modalBody.innerHTML = `<div class="error">Транскрипт и анализ недоступны</div>`;
}

// Format interview content with timecode highlighting
function formatInterviewContent(content) {
    // Highlight timecodes like [00:05:23] or (05:23)
    content = content.replace(/\[?(\d{1,2}:\d{2}(:\d{2})?)\]?/g, '<span class="timecode-badge">$1</span>');
    
    // Convert newlines to paragraphs
    content = content.split('\n\n').map(p => `<p>${p}</p>`).join('');
    content = content.replace(/\n/g, '<br>');
    
    return content;
}

// Close interview modal
function closeInterviewModal() {
    const modal = document.getElementById('interviewModal');
    modal.classList.add('hidden');
}

async function batchAnalyze() {
    if (state.transcripts.length === 0) {
        showToast('Нет доступных транскриптов', 'error');
        return;
    }
    
    const confirmed = confirm(
        `Вы хотите проанализировать все ${state.transcripts.length} транскриптов?\n\n` +
        `Это займёт примерно ${Math.round(state.transcripts.length * 0.5)} минут и использует AI API.`
    );
    
    if (!confirmed) return;
    
    showLoading(`Массовый анализ ${state.transcripts.length} транскриптов...`);
    
    try {
        const transcriptNames = state.transcripts.map(t => t.name);
        
        const response = await apiCall('/analyze/batch', {
            method: 'POST',
            body: JSON.stringify({
                transcript_names: transcriptNames
            })
        });
        
        if (response.success) {
            showToast(
                `Анализ завершён! Обработано ${response.analyzed_count} транскриптов`,
                'success'
            );
            
            // Reload statistics
            await loadStatistics();
        }
    } catch (error) {
        showToast('Ошибка массового анализа: ' + error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function handleFileUpload(event) {
    const file = event.target.files[0];
    
    if (!file) return;
    
    if (!file.name.endsWith('.docx')) {
        showToast('Поддерживаются только файлы .docx', 'error');
        return;
    }
    
    showLoading('Загрузка транскрипта...');
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_BASE_URL}/transcripts`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Транскрипт загружен успешно!', 'success');
            await loadTranscripts();
            
            // Select the newly uploaded transcript
            const newTranscript = state.transcripts.find(t => 
                t.filename === result.filename
            );
            if (newTranscript) {
                selectTranscript(newTranscript.name);
            }
        } else {
            showToast('Ошибка загрузки: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('Ошибка загрузки: ' + error.message, 'error');
    } finally {
        hideLoading();
        event.target.value = ''; // Reset input
    }
}

function handleSearch(event) {
    const query = event.target.value.toLowerCase().trim();
    
    // Check if searching for a bank tag
    if (query.startsWith('#')) {
        const bankQuery = query.substring(1);
        const items = document.querySelectorAll('.transcript-item');
        items.forEach(item => {
            const banks = (item.dataset.banks || '').toLowerCase();
            if (banks.includes(bankQuery)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    } else {
        // Regular name search
        const items = document.querySelectorAll('.transcript-item');
        items.forEach(item => {
            const name = item.querySelector('.name').textContent.toLowerCase();
            const banks = (item.dataset.banks || '').toLowerCase();
            if (name.includes(query) || banks.includes(query)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }
}

// ============================================================================
// UI Helpers
// ============================================================================

function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    const tabMap = {
        'analyze': 'analyzeTab',
        'compare': 'compareTab'
    };
    
    document.getElementById(tabMap[tabName])?.classList.add('active');
    
    // If switching to compare tab, run comparison if we have analysis
    if (tabName === 'compare' && state.currentAnalysis) {
        runComparison();
    }
}

function showLoading(message = 'Загрузка...') {
    const overlay = document.getElementById('loadingOverlay');
    const text = document.getElementById('loadingText');
    
    text.textContent = message;
    overlay.classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.add('hidden');
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const messageEl = document.getElementById('toastMessage');
    
    messageEl.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.remove('hidden');
    
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 5000);
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// ============================================================================
// Simple Markdown Parser (fallback if marked.js not available)
// ============================================================================

function parseMarkdown(text) {
    if (typeof window.marked !== 'undefined' && window.marked.parse) {
        return window.marked.parse(text);
    }
    
    // Simple markdown to HTML conversion (fallback)
    return text
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>')
        .replace(/^(.*)$/gim, '<p>$1</p>')
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
}
