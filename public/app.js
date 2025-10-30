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
    
    let html = `
        <div class="message-content">
            <div class="message-header">
                <div class="message-icon">${icon}</div>
                <div class="message-label">${label}</div>
            </div>
            <div class="message-text">${role === 'assistant' ? renderMarkdown(content) : escapeHtml(content)}</div>
    `;
    
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

