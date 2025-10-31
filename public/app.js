// Presupuesto 2026 AI Chat - Frontend Logic

// Configuration
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:3000' 
    : '';

// State
let conversationHistory = [];
let sessionId = generateSessionId();
let isLoading = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupTextareaAutoResize();
    checkAPIConnection();
});

// Generate unique session ID
function generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// Setup textarea auto-resize
function setupTextareaAutoResize() {
    const textarea = document.getElementById('userInput');
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 200) + 'px';
    });
}

// Check API connection
async function checkAPIConnection() {
    const statusEl = document.getElementById('connectionStatus');
    
    // For Vercel deployment, assume it's connected
    statusEl.innerHTML = '<span class="status-dot"></span> Ready';
}

// Handle key press in textarea
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Ask example question
function askExample(question) {
    document.getElementById('userInput').value = question;
    sendMessage();
}

// Send message
async function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    if (!message || isLoading) return;
    
    // Clear input
    input.value = '';
    input.style.height = 'auto';
    
    // Hide welcome message
    const welcomeMessage = document.getElementById('welcomeMessage');
    if (welcomeMessage) {
        welcomeMessage.style.display = 'none';
    }
    
    // Add user message to chat
    addMessage('user', message);
    
    // Add loading indicator
    const loadingId = addLoadingMessage();
    
    // Disable send button
    isLoading = true;
    updateSendButton();
    
    try {
        // Call API
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                conversation_history: conversationHistory,
                session_id: sessionId
            })
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        console.log('DEBUG: Received data from API:', data);
        
        // Check if there's an error in the response
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Check if response exists
        if (!data.response) {
            throw new Error('No response received from API');
        }
        
        // Remove loading indicator
        removeLoadingMessage(loadingId);
        
        // Add assistant response
        addMessage('assistant', data.response, data.sources);
        
        // Update conversation history
        conversationHistory.push(
            { role: 'user', content: message },
            { role: 'assistant', content: data.response }
        );
        
        // Keep only last 10 messages (5 turns)
        if (conversationHistory.length > 10) {
            conversationHistory = conversationHistory.slice(-10);
        }
        
    } catch (error) {
        console.error('Error:', error);
        removeLoadingMessage(loadingId);
        showError('Sorry, there was an error processing your request. Please try again.');
    } finally {
        isLoading = false;
        updateSendButton();
    }
}

// Add message to chat
function addMessage(role, content, sources = null) {
    const chatContainer = document.getElementById('chatContainer');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const icon = role === 'user' ? '👤' : '🤖';
    const label = role === 'user' ? 'You' : 'AI Assistant';
    
    // Extract chart specifications if present
    let chartSpec = null;
    let textContent = content;
    
    if (role === 'assistant') {
        const chartMatch = content.match(/\[CHART_START\]([\s\S]*?)\[CHART_END\]/);
        if (chartMatch) {
            try {
                chartSpec = JSON.parse(chartMatch[1].trim());
                // Remove chart spec from text content
                textContent = content.replace(/\[CHART_START\][\s\S]*?\[CHART_END\]/, '').trim();
            } catch (e) {
                console.error('Failed to parse chart specification:', e);
            }
        }
    }
    
    let html = `
        <div class="message-content">
            <div class="message-header">
                <div class="message-icon">${icon}</div>
                <div class="message-label">${label}</div>
            </div>
            <div class="message-text">${role === 'assistant' ? renderMarkdown(textContent) : escapeHtml(textContent)}</div>
    `;
    
    // Add chart container if chart spec exists
    if (chartSpec) {
        const chartId = `chart-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        html += `
            <div class="chart-container">
                <canvas id="${chartId}"></canvas>
            </div>
        `;
    }
    
    // Add sources if available
    if (sources && sources.length > 0) {
        const uniqueSources = [...new Set(sources.map(s => s.source))];
        html += `
            <div class="message-sources">
                <strong>Sources:</strong> 
                ${uniqueSources.map(s => `<span class="source-tag">${s}</span>`).join('')}
            </div>
        `;
    }
    
    html += `</div>`;
    messageDiv.innerHTML = html;
    
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
    
    // Highlight code blocks if present
    if (role === 'assistant') {
        messageDiv.querySelectorAll('pre code').forEach(block => {
            hljs.highlightElement(block);
        });
        
        // Render chart if spec exists
        if (chartSpec) {
            const chartCanvas = messageDiv.querySelector(`#${chartId}`);
            if (chartCanvas) {
                renderChart(chartCanvas, chartSpec);
            }
        }
    }
}

// Add loading message
function addLoadingMessage() {
    const chatContainer = document.getElementById('chatContainer');
    
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message assistant';
    loadingDiv.id = `loading-${Date.now()}`;
    
    loadingDiv.innerHTML = `
        <div class="message-content">
            <div class="message-header">
                <div class="message-icon">🤖</div>
                <div class="message-label">AI Assistant</div>
            </div>
            <div class="loading">
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
            </div>
        </div>
    `;
    
    chatContainer.appendChild(loadingDiv);
    scrollToBottom();
    
    return loadingDiv.id;
}

// Remove loading message
function removeLoadingMessage(loadingId) {
    const loadingEl = document.getElementById(loadingId);
    if (loadingEl) {
        loadingEl.remove();
    }
}

// Show error message
function showError(message) {
    const chatContainer = document.getElementById('chatContainer');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    
    chatContainer.appendChild(errorDiv);
    scrollToBottom();
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// Render markdown
function renderMarkdown(text) {
    // Configure marked options
    marked.setOptions({
        breaks: true,
        gfm: true,
        headerIds: false,
        mangle: false
    });
    
    return marked.parse(text);
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Scroll to bottom
function scrollToBottom() {
    const chatContainer = document.getElementById('chatContainer');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Update send button state
function updateSendButton() {
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = isLoading;
}

// Start new chat
function startNewChat() {
    // Confirm if there's existing conversation
    if (conversationHistory.length > 0) {
        if (!confirm('Start a new conversation? Current chat will be cleared.')) {
            return;
        }
    }
    
    // Reset state
    conversationHistory = [];
    sessionId = generateSessionId();
    
    // Clear chat container
    const chatContainer = document.getElementById('chatContainer');
    chatContainer.innerHTML = `
        <div class="welcome-message" id="welcomeMessage">
            <div class="welcome-icon">🎯</div>
            <h2>Welcome to Presupuesto 2026 AI Assistant!</h2>
            <p>I can help you explore insights from the TikTok analysis project.</p>
            
            <div class="example-questions">
                <h3>Try asking:</h3>
                <button class="example-btn" onclick="askExample('What are the main findings from the sentiment analysis?')">
                    What are the main findings from the sentiment analysis?
                </button>
                <button class="example-btn" onclick="askExample('Which post has the highest Interest Index?')">
                    Which post has the highest Interest Index?
                </button>
                <button class="example-btn" onclick="askExample('What are the most common topics in negative comments?')">
                    What are the most common topics in negative comments?
                </button>
                <button class="example-btn" onclick="askExample('What are the strategic communication recommendations?')">
                    What are the strategic communication recommendations?
                </button>
            </div>
        </div>
    `;
    
    // Clear input
    document.getElementById('userInput').value = '';
}

// Export conversation (bonus feature)
function exportConversation() {
    if (conversationHistory.length === 0) {
        alert('No conversation to export');
        return;
    }
    
    const exportData = {
        session_id: sessionId,
        timestamp: new Date().toISOString(),
        messages: conversationHistory
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `presupuesto_2026_chat_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

// Render chart using Chart.js
function renderChart(canvas, chartSpec) {
    try {
        // Default color schemes
        const defaultColors = {
            positive: '#10b981',
            negative: '#ef4444',
            neutral: '#94a3b8',
            primary: '#667eea',
            secondary: '#764ba2'
        };
        
        // Generate colors if not provided
        if (chartSpec.data.datasets) {
            chartSpec.data.datasets.forEach(dataset => {
                if (!dataset.backgroundColor) {
                    // Generate colors based on chart type
                    if (chartSpec.type === 'pie' || chartSpec.type === 'doughnut') {
                        dataset.backgroundColor = generateColorPalette(chartSpec.data.labels.length);
                    } else {
                        dataset.backgroundColor = defaultColors.primary;
                        dataset.borderColor = defaultColors.primary;
                    }
                }
                
                // Set border width for better visibility
                if (!dataset.borderWidth) {
                    dataset.borderWidth = chartSpec.type === 'pie' || chartSpec.type === 'doughnut' ? 2 : 0;
                }
            });
        }
        
        // Configure chart options
        const options = {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        font: {
                            size: 12,
                            family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif'
                        },
                        padding: 15,
                        usePointStyle: true
                    }
                },
                title: {
                    display: !!chartSpec.title,
                    text: chartSpec.title || '',
                    font: {
                        size: 16,
                        weight: 'bold',
                        family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif'
                    },
                    padding: {
                        top: 10,
                        bottom: 20
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    cornerRadius: 8,
                    titleFont: {
                        size: 14
                    },
                    bodyFont: {
                        size: 13
                    }
                }
            },
            scales: chartSpec.type !== 'pie' && chartSpec.type !== 'doughnut' ? {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 11
                        },
                        maxRotation: 45,
                        minRotation: 0
                    }
                }
            } : {}
        };
        
        // Handle horizontal bar chart
        if (chartSpec.type === 'horizontalBar') {
            chartSpec.type = 'bar';
            options.indexAxis = 'y';
        }
        
        // Merge with custom options if provided
        if (chartSpec.options) {
            Object.assign(options, chartSpec.options);
        }
        
        // Create chart
        new Chart(canvas, {
            type: chartSpec.type,
            data: chartSpec.data,
            options: options
        });
        
    } catch (error) {
        console.error('Error rendering chart:', error);
        canvas.parentElement.innerHTML = '<p style="color: #ef4444; padding: 20px;">Failed to render chart</p>';
    }
}

// Generate color palette
function generateColorPalette(count) {
    const baseColors = [
        '#667eea', '#764ba2', '#f093fb', '#4facfe',
        '#43e97b', '#fa709a', '#fee140', '#30cfd0',
        '#a8edea', '#fed6e3', '#c471f5', '#fa71cd'
    ];
    
    const colors = [];
    for (let i = 0; i < count; i++) {
        colors.push(baseColors[i % baseColors.length]);
    }
    return colors;
}

