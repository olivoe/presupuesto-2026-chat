// Admin Dashboard - Frontend Logic

// Configuration
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:3000' 
    : '';

// State
let currentPassword = '';
let allLogs = [];
let analytics = {};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Check if already logged in (session storage)
    const savedPassword = sessionStorage.getItem('dashboard_password');
    if (savedPassword) {
        currentPassword = savedPassword;
        showDashboard();
        loadDashboardData();
    }
});

// Login
async function login(event) {
    event.preventDefault();
    
    const password = document.getElementById('passwordInput').value;
    const loginBtn = document.getElementById('loginBtn');
    const errorEl = document.getElementById('loginError');
    
    // Disable button
    loginBtn.disabled = true;
    loginBtn.innerHTML = '<div class="loading-spinner"></div> Authenticating...';
    errorEl.style.display = 'none';
    
    try {
        // Test authentication by fetching logs
        const response = await fetch(`${API_BASE_URL}/api/dashboard`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: 'get_logs',
                password: password,
                days: 7
            })
        });
        
        const data = await response.json();
        
        if (data.authenticated) {
            // Success
            currentPassword = password;
            sessionStorage.setItem('dashboard_password', password);
            showDashboard();
            loadDashboardData();
        } else {
            // Failed
            errorEl.textContent = data.error || 'Invalid password';
            errorEl.style.display = 'block';
            loginBtn.disabled = false;
            loginBtn.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>
                    <polyline points="10 17 15 12 10 7"></polyline>
                    <line x1="15" y1="12" x2="3" y2="12"></line>
                </svg>
                Login
            `;
        }
    } catch (error) {
        console.error('Login error:', error);
        errorEl.textContent = 'Connection error. Please try again.';
        errorEl.style.display = 'block';
        loginBtn.disabled = false;
        loginBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>
                <polyline points="10 17 15 12 10 7"></polyline>
                <line x1="15" y1="12" x2="3" y2="12"></line>
            </svg>
            Login
        `;
    }
}

// Logout
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        currentPassword = '';
        sessionStorage.removeItem('dashboard_password');
        document.getElementById('loginScreen').style.display = 'flex';
        document.getElementById('dashboardScreen').style.display = 'none';
        document.getElementById('passwordInput').value = '';
    }
}

// Show Dashboard
function showDashboard() {
    document.getElementById('loginScreen').style.display = 'none';
    document.getElementById('dashboardScreen').style.display = 'block';
}

// Load Dashboard Data
async function loadDashboardData() {
    const days = parseInt(document.getElementById('daysFilter').value);
    
    try {
        // Load logs
        const logsResponse = await fetch(`${API_BASE_URL}/api/dashboard`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: 'get_logs',
                password: currentPassword,
                days: days
            })
        });
        
        const logsData = await logsResponse.json();
        
        if (logsData.authenticated) {
            allLogs = logsData.logs || [];
            displayLogs(allLogs);
        }
        
        // Load analytics
        const analyticsResponse = await fetch(`${API_BASE_URL}/api/dashboard`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: 'get_analytics',
                password: currentPassword,
                days: days
            })
        });
        
        const analyticsData = await analyticsResponse.json();
        
        if (analyticsData.authenticated) {
            analytics = analyticsData.analytics || {};
            displayAnalytics(analytics);
        }
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        alert('Failed to load dashboard data. Please try again.');
    }
}

// Display Analytics
function displayAnalytics(data) {
    // Update stats
    document.getElementById('totalMessages').textContent = data.total_messages || 0;
    document.getElementById('uniqueSessions').textContent = data.unique_sessions || 0;
    document.getElementById('avgMessageLength').textContent = data.avg_message_length || 0;
    document.getElementById('avgResponseLength').textContent = data.avg_response_length || 0;
    
    // Queries per day chart
    if (data.queries_per_day && Object.keys(data.queries_per_day).length > 0) {
        const queriesCtx = document.getElementById('queriesChart');
        
        // Destroy existing chart if any
        if (window.queriesChartInstance) {
            window.queriesChartInstance.destroy();
        }
        
        const dates = Object.keys(data.queries_per_day).sort();
        const counts = dates.map(date => data.queries_per_day[date]);
        
        window.queriesChartInstance = new Chart(queriesCtx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Queries',
                    data: counts,
                    backgroundColor: 'rgba(102, 126, 234, 0.2)',
                    borderColor: '#667eea',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }
    
    // Popular topics chart
    if (data.popular_topics && data.popular_topics.length > 0) {
        const topicsCtx = document.getElementById('topicsChart');
        
        // Destroy existing chart if any
        if (window.topicsChartInstance) {
            window.topicsChartInstance.destroy();
        }
        
        const topics = data.popular_topics.map(t => t[0]);
        const counts = data.popular_topics.map(t => t[1]);
        
        window.topicsChartInstance = new Chart(topicsCtx, {
            type: 'bar',
            data: {
                labels: topics,
                datasets: [{
                    label: 'Mentions',
                    data: counts,
                    backgroundColor: '#667eea',
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }
}

// Display Logs
function displayLogs(logs) {
    const container = document.getElementById('logsContainer');
    
    if (logs.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <h3>No logs found</h3>
                <p>No conversation logs available for the selected time period.</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = logs.map(log => `
        <div class="log-entry">
            <div class="log-header">
                <span class="log-session">Session: ${log.session_id}</span>
                <span class="log-timestamp">${formatTimestamp(log.timestamp)}</span>
            </div>
            
            <div class="log-message">
                <div class="log-message-label">👤 User:</div>
                <div class="log-message-content">${escapeHtml(log.user_message)}</div>
            </div>
            
            <div class="log-message">
                <div class="log-message-label">🤖 Assistant:</div>
                <div class="log-message-content">${escapeHtml(log.assistant_response.substring(0, 300))}${log.assistant_response.length > 300 ? '...' : ''}</div>
            </div>
            
            ${log.sources && log.sources.length > 0 ? `
                <div class="log-sources">
                    ${log.sources.map(source => `<span class="source-badge">${source}</span>`).join('')}
                </div>
            ` : ''}
        </div>
    `).join('');
}

// Filter Logs
function filterLogs() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    
    if (!searchTerm) {
        displayLogs(allLogs);
        return;
    }
    
    const filtered = allLogs.filter(log => 
        log.user_message.toLowerCase().includes(searchTerm) ||
        log.assistant_response.toLowerCase().includes(searchTerm) ||
        log.session_id.toLowerCase().includes(searchTerm)
    );
    
    displayLogs(filtered);
}

// Refresh Data
function refreshData() {
    loadDashboardData();
}

// Export Logs
async function exportLogs() {
    const days = parseInt(document.getElementById('daysFilter').value);
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/dashboard`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: 'export_logs',
                password: currentPassword,
                days: days
            })
        });
        
        const data = await response.json();
        
        if (data.authenticated && data.logs) {
            // Create downloadable file
            const blob = new Blob([JSON.stringify(data.logs, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `presupuesto_2026_logs_${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
        } else {
            alert('Failed to export logs');
        }
    } catch (error) {
        console.error('Export error:', error);
        alert('Failed to export logs. Please try again.');
    }
}

// Utility Functions
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

