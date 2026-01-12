/**
 * SQL Detective Analytics Dashboard
 * Main JavaScript for data fetching and visualization
 */

const API_BASE = '/api/analytics';

// ==========================================
// Chart Instances
// ==========================================
let suspectChart = null;
let hourlyChart = null;
let comparisonChart = null;
let funnelChart = null;
let learningChart = null;

// ==========================================
// Initialization
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    setupTabNavigation();
    setupEventListeners();
    loadAllData();
});

function setupTabNavigation() {
    const tabs = document.querySelectorAll('.tab-btn');
    const panels = document.querySelectorAll('.tab-panel');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Show corresponding panel
            const tabId = tab.dataset.tab;
            panels.forEach(p => p.classList.remove('active'));
            document.getElementById(`${tabId}-tab`).classList.add('active');
        });
    });
}

function setupEventListeners() {
    document.getElementById('refresh-btn').addEventListener('click', loadAllData);
    document.getElementById('save-config').addEventListener('click', saveConfig);
}

async function loadAllData() {
    await Promise.all([
        loadSuspectData(),
        loadTimelineData(),
        loadPlayerData(),
        loadConfig()
    ]);
}

// ==========================================
// Module 1: Suspect Intelligence
// ==========================================

async function loadSuspectData() {
    try {
        // Load rankings
        const response = await fetch(`${API_BASE}/suspects/rankings`);
        const data = await response.json();

        if (data.success) {
            renderTopSuspects(data.rankings.slice(0, 3));
            renderRankingsTable(data.rankings);
        }

        // Load chart data
        const chartResponse = await fetch(`${API_BASE}/suspects/chart-data`);
        const chartData = await chartResponse.json();

        if (chartData.success) {
            renderSuspectChart(chartData.data);
        }
    } catch (error) {
        console.error('Error loading suspect data:', error);
    }
}

function renderTopSuspects(suspects) {
    const container = document.getElementById('top-suspects');
    container.innerHTML = suspects.map((s, i) => `
        <div class="suspect-card rank-${i + 1}">
            <span class="suspect-rank">${i + 1}</span>
            <div class="suspect-name">${s.name}</div>
            <div class="suspect-score">${s.total_score}</div>
            <div class="suspect-occupation">${s.occupation}</div>
        </div>
    `).join('');
}

function renderRankingsTable(rankings) {
    const tbody = document.querySelector('#rankings-table tbody');
    tbody.innerHTML = rankings.map(s => `
        <tr>
            <td class="highlight">#${s.rank}</td>
            <td>${s.name}</td>
            <td>${s.occupation}</td>
            <td>${s.criminal_record ? '✓' : '-'}</td>
            <td>${s.details.crime_window_calls}</td>
            <td>${s.details.high_transactions}</td>
            <td>${s.details.bank_sightings}</td>
            <td class="highlight">${s.total_score}</td>
        </tr>
    `).join('');
}

function renderSuspectChart(data) {
    const ctx = document.getElementById('suspect-chart').getContext('2d');

    if (suspectChart) {
        suspectChart.destroy();
    }

    suspectChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: data.datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    stacked: true,
                    ticks: { color: '#8b949e' },
                    grid: { color: '#30363d' }
                },
                y: {
                    stacked: true,
                    ticks: { color: '#8b949e' },
                    grid: { color: '#30363d' }
                }
            }
        }
    });
}

// ==========================================
// Module 2: Time Analysis
// ==========================================

async function loadTimelineData() {
    try {
        // Hourly activity
        const hourlyResponse = await fetch(`${API_BASE}/timeline/hourly?date=2024-03-15`);
        const hourlyData = await hourlyResponse.json();

        if (hourlyData.success) {
            renderHourlyChart(hourlyData.data);
        }

        // Before/After comparison
        const comparisonResponse = await fetch(`${API_BASE}/timeline/comparison`);
        const comparisonData = await comparisonResponse.json();

        if (comparisonData.success) {
            renderComparisonChart(comparisonData.data);
            renderAnomalies(comparisonData.data.anomalies);
        }

        // Heatmap
        const heatmapResponse = await fetch(`${API_BASE}/timeline/heatmap`);
        const heatmapData = await heatmapResponse.json();

        if (heatmapData.success) {
            renderHeatmap(heatmapData.data);
        }
    } catch (error) {
        console.error('Error loading timeline data:', error);
    }
}

function renderHourlyChart(data) {
    const ctx = document.getElementById('hourly-chart').getContext('2d');

    if (hourlyChart) {
        hourlyChart.destroy();
    }

    hourlyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Phone Calls',
                    data: data.phone_calls,
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Transactions',
                    data: data.transactions,
                    borderColor: 'rgba(255, 206, 86, 1)',
                    backgroundColor: 'rgba(255, 206, 86, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'CCTV Sightings',
                    data: data.cctv_sightings,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#8b949e' }
                },
                annotation: {
                    annotations: {
                        crimeTime: {
                            type: 'line',
                            xMin: 23,
                            xMax: 23,
                            borderColor: 'rgba(248, 81, 73, 0.8)',
                            borderWidth: 2,
                            borderDash: [5, 5],
                            label: {
                                content: 'Crime Time',
                                enabled: true
                            }
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#8b949e' },
                    grid: { color: '#30363d' }
                },
                y: {
                    ticks: { color: '#8b949e' },
                    grid: { color: '#30363d' }
                }
            }
        }
    });
}

function renderComparisonChart(data) {
    const ctx = document.getElementById('comparison-chart').getContext('2d');

    if (comparisonChart) {
        comparisonChart.destroy();
    }

    const suspects = data.suspects.slice(0, 6); // Top 6 for visibility

    comparisonChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: suspects.map(s => s.name),
            datasets: [
                {
                    label: 'Before Crime',
                    data: suspects.map(s => s.calls.before),
                    backgroundColor: 'rgba(54, 162, 235, 0.7)'
                },
                {
                    label: 'After Crime',
                    data: suspects.map(s => s.calls.after),
                    backgroundColor: 'rgba(255, 99, 132, 0.7)'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#8b949e' }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#8b949e' },
                    grid: { color: '#30363d' }
                },
                y: {
                    ticks: { color: '#8b949e' },
                    grid: { color: '#30363d' }
                }
            }
        }
    });
}

function renderAnomalies(anomalies) {
    const container = document.getElementById('anomalies-list');

    if (anomalies.length === 0) {
        container.innerHTML = '<p class="loading">No anomalies detected</p>';
        return;
    }

    container.innerHTML = anomalies.map(a => `
        <div class="anomaly-item">
            <div class="item-label">${a.name}</div>
            <div class="item-value">
                Calls: ${a.calls.pattern} (${a.calls.before} → ${a.calls.after})
            </div>
        </div>
    `).join('');
}

function renderHeatmap(data) {
    const container = document.getElementById('heatmap-container');

    if (!data.suspects || data.suspects.length === 0) {
        container.innerHTML = '<p class="loading">No heatmap data available</p>';
        return;
    }

    const maxActivity = Math.max(...data.suspects.flatMap(s => s.hours));

    let html = '<table class="heatmap-table"><thead><tr><th></th>';
    html += data.hours.map(h => `<th>${h}</th>`).join('');
    html += '</tr></thead><tbody>';

    data.suspects.forEach(suspect => {
        html += `<tr><td style="text-align: left; font-size: 0.75rem;">${suspect.name}</td>`;
        suspect.hours.forEach(val => {
            const intensity = maxActivity > 0 ? val / maxActivity : 0;
            const color = `rgba(245, 158, 11, ${intensity * 0.9 + 0.1})`;
            html += `<td><span class="heatmap-cell" style="background: ${color}" title="${val}"></span></td>`;
        });
        html += '</tr>';
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

// ==========================================
// Module 3: Player Analytics
// ==========================================

async function loadPlayerData() {
    try {
        const response = await fetch(`${API_BASE}/players/dashboard`);
        const data = await response.json();

        if (data.success) {
            renderPlayerStats(data.data);
            renderFunnelChart(data.data.funnel);
            renderLearningChart(data.data.learning_curve);
            renderErrors(data.data.errors);
            renderRecentSessions(data.data.sessions);
        }
    } catch (error) {
        console.error('Error loading player data:', error);
    }
}

function renderPlayerStats(data) {
    document.getElementById('stat-sessions').textContent = data.sessions.total_sessions;
    document.getElementById('stat-queries').textContent = data.sessions.total_queries;
    document.getElementById('stat-success').textContent = `${data.queries.success_rate}%`;
    document.getElementById('stat-avg-levels').textContent = data.sessions.avg_levels_per_session;
}

function renderFunnelChart(data) {
    const ctx = document.getElementById('funnel-chart').getContext('2d');

    if (funnelChart) {
        funnelChart.destroy();
    }

    const levels = data.levels || [];

    funnelChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: levels.map(l => `Level ${l.level_id}`),
            datasets: [
                {
                    label: 'Started',
                    data: levels.map(l => l.started),
                    backgroundColor: 'rgba(88, 166, 255, 0.7)'
                },
                {
                    label: 'Completed',
                    data: levels.map(l => l.completed),
                    backgroundColor: 'rgba(63, 185, 80, 0.7)'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#8b949e' }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#8b949e' },
                    grid: { color: '#30363d' }
                },
                y: {
                    ticks: { color: '#8b949e' },
                    grid: { color: '#30363d' }
                }
            }
        }
    });
}

function renderLearningChart(data) {
    const ctx = document.getElementById('learning-chart').getContext('2d');

    if (learningChart) {
        learningChart.destroy();
    }

    const levels = data.levels || [];

    learningChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: levels.map(l => `Level ${l.level_id}`),
            datasets: [{
                label: 'Avg Attempts',
                data: levels.map(l => l.avg_attempts),
                borderColor: 'rgba(245, 158, 11, 1)',
                backgroundColor: 'rgba(245, 158, 11, 0.2)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#8b949e' }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#8b949e' },
                    grid: { color: '#30363d' }
                },
                y: {
                    ticks: { color: '#8b949e' },
                    grid: { color: '#30363d' }
                }
            }
        }
    });
}

function renderErrors(data) {
    const container = document.getElementById('errors-list');
    const errors = data.top_errors || [];

    if (errors.length === 0) {
        container.innerHTML = '<p class="loading">No errors recorded yet</p>';
        return;
    }

    container.innerHTML = errors.map(e => `
        <div class="error-item">
            <div class="item-label">${e.type}</div>
            <div class="item-value">${e.count} occurrences (${e.percentage}%)</div>
        </div>
    `).join('');
}

function renderRecentSessions(data) {
    const container = document.getElementById('recent-sessions');
    const sessions = data.recent_sessions || [];

    if (sessions.length === 0) {
        container.innerHTML = '<p class="loading">No sessions recorded yet</p>';
        return;
    }

    container.innerHTML = sessions.map(s => `
        <div class="session-item">
            <div class="item-label">${s.session_id}</div>
            <div class="item-value">${s.levels} levels, ${s.queries} queries</div>
        </div>
    `).join('');
}

// ==========================================
// Configuration
// ==========================================

async function loadConfig() {
    try {
        const response = await fetch(`${API_BASE}/config`);
        const data = await response.json();

        if (data.success) {
            renderConfigForm(data.config);
        }
    } catch (error) {
        console.error('Error loading config:', error);
    }
}

function renderConfigForm(config) {
    const container = document.getElementById('config-form');

    const weightKeys = [
        { key: 'weight_criminal_record', label: 'Criminal Record Weight' },
        { key: 'weight_crime_calls', label: 'Crime Window Calls Weight' },
        { key: 'weight_high_transactions', label: 'High Transactions Weight' },
        { key: 'weight_bank_cctv', label: 'Bank CCTV Weight' },
        { key: 'weight_call_volume', label: 'Call Volume Weight' },
        { key: 'high_transaction_threshold', label: 'High Transaction Threshold ($)' }
    ];

    container.innerHTML = weightKeys.map(w => `
        <div class="config-item">
            <span class="config-label">${w.label}</span>
            <input type="number" class="config-input" 
                   data-key="${w.key}" 
                   value="${config[w.key] || 0}" 
                   step="0.1">
        </div>
    `).join('');
}

async function saveConfig() {
    const inputs = document.querySelectorAll('.config-input');

    for (const input of inputs) {
        const key = input.dataset.key;
        const value = parseFloat(input.value);

        try {
            await fetch(`${API_BASE}/config`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ key, value })
            });
        } catch (error) {
            console.error('Error saving config:', error);
        }
    }

    // Reload suspect data to reflect changes
    await loadSuspectData();
    alert('Configuration saved and scores recalculated!');
}
