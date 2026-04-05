document.addEventListener('DOMContentLoaded', () => {
    // Auth Check
    const path = window.location.pathname;
    if (!path.endsWith('index.html') && !path.endsWith('/') && !path.includes('index')) {
        const token = localStorage.getItem('jwt_token');
        if (!token) {
            window.location.href = 'index.html';
            return;
        }
    }

    // Layout Injector
    const appContainer = document.querySelector('.app-container');
    if (appContainer && !appContainer.classList.contains('login-page')) {
        injectSidebar(appContainer);
        
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            injectTopbar(mainContent);
            injectFooter(mainContent);
            
// Start AI status check after Topbar is injected
if (localStorage.getItem('jwt_token')) {
    console.log("Initiating AI status polling...");
    setTimeout(() => {
        if (window.checkAIStatus) window.checkAIStatus();
        aiStatusPolling = setInterval(() => {
            if (window.checkAIStatus) window.checkAIStatus();
        }, 5000);
    }, 1000); // Give it another second for everything to settle
}
        }
    }
});

function injectSidebar(container) {
    const currentPage = window.location.pathname.split('/').pop() || 'dashboard.html';
    
    const sidebarHtml = `
        <div class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <div class="sidebar-logo">
                    <i class="fas fa-layer-group"></i> QA Engine
                </div>
                <button class="toggle-btn" onclick="toggleSidebar()">
                    <i class="fas fa-bars"></i>
                </button>
            </div>
            <div class="sidebar-nav">
                <a href="dashboard.html" class="nav-item ${currentPage === 'dashboard.html' ? 'active' : ''}">
                    <i class="fas fa-chart-pie"></i> <span>Dashboard</span>
                </a>
                <a href="uat.html" class="nav-item ${currentPage === 'uat.html' ? 'active' : ''}">
                    <i class="fas fa-file-invoice"></i> <span>UAT Generator</span>
                </a>
                <a href="story.html" class="nav-item ${currentPage === 'story.html' ? 'active' : ''}">
                    <i class="fas fa-book-open"></i> <span>Story Generator</span>
                </a>
                <a href="jira.html" class="nav-item ${currentPage === 'jira.html' ? 'active' : ''}">
                    <i class="fab fa-jira"></i> <span>Jira Generator</span>
                </a>
                <a href="history.html" class="nav-item ${currentPage === 'history.html' ? 'active' : ''}">
                    <i class="fas fa-history"></i> <span>History</span>
                </a>
                <a href="config.html" class="nav-item ${currentPage === 'config.html' ? 'active' : ''}">
                    <i class="fas fa-cog"></i> <span>Configuration</span>
                </a>
            </div>
        </div>
    `;

    container.insertAdjacentHTML('afterbegin', sidebarHtml);
}

function injectTopbar(mainContent) {
    const titleElements = {
        'dashboard.html': 'Dashboard',
        'uat.html': 'UAT Test Case Generator',
        'story.html': 'Story/Feature Test Case Generator',
        'jira.html': 'Jira Test Case Generator',
        'history.html': 'Generation History',
        'config.html': 'System Configuration'
    };
    
    const currentPage = window.location.pathname.split('/').pop() || 'dashboard.html';
    const pageTitle = titleElements[currentPage] || 'FirstFintech QA Engine';

    const topbarHtml = `
        <div class="topbar">
            <div class="page-title">${pageTitle}</div>
            <div class="user-profile">
                <div id="ai-status-container" class="ai-status-container" title="Local AI Engine Status">
                    <button onclick="initiateAI()" class="btn btn-ai-ready" id="ai-ready-btn">
                        <i class="fas fa-microchip"></i> <span id="ai-status-text">Ready AI</span>
                        <div class="status-dot" id="ai-status-dot"></div>
                    </button>
                </div>
                <div class="user-info" style="text-align: right;">
                    <span class="user-name">Gaurav Subedi</span>
                    <span class="user-role">Administrator</span>
                </div>
                <div class="avatar">GS</div>
                <button onclick="toggleTheme()" class="btn btn-secondary" style="margin-left: 12px; padding: 8px;" title="Toggle Theme">
                    <i class="fas fa-moon" id="themeIcon" style="margin: 0"></i>
                </button>
                <button onclick="logout()" class="btn btn-secondary" style="margin-left: 12px; padding: 8px;" title="Logout">
                    <i class="fas fa-sign-out-alt" style="margin: 0"></i>
                </button>
            </div>
        </div>
    `;

    mainContent.insertAdjacentHTML('afterbegin', topbarHtml);
}

function injectFooter(mainContent) {
    const footerHtml = `
        <footer class="footer">
            &copy; ${new Date().getFullYear()} FirstFintech QA Engine. Developed by Gaurav Subedi.
        </footer>
    `;
    mainContent.insertAdjacentHTML('beforeend', footerHtml);
}

window.toggleSidebar = function() {
    const sidebar = document.getElementById('sidebar');
    if(sidebar) {
        sidebar.classList.toggle('collapsed');
    }
};

window.logout = function() {
    localStorage.removeItem('jwt_token');
    window.location.href = 'index.html';
};

window.exportTableToExcel = function(tableId, filename = '') {
    if (typeof XLSX === 'undefined') {
        alert('SheetJS (XLSX) is not loaded.');
        return;
    }
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const ws = XLSX.utils.table_to_sheet(table);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Test Cases");
    
    XLSX.writeFile(wb, filename ? filename + '.xlsx' : 'TestCases.xlsx');
};

window.showError = function(message) {
    const alertBox = document.getElementById('errorAlert');
    if (alertBox) {
        alertBox.textContent = message;
        alertBox.style.display = 'block';
        setTimeout(() => alertBox.style.display = 'none', 5000);
    } else {
        alert(message);
    }
}

// --- THEME SYSTEM ---
function initTheme() {
    const storedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    let activeTheme = storedTheme || (prefersDark ? 'dark' : 'light');
    
    if (activeTheme === 'dark') {
        document.body.classList.add('dark-theme');
        updateThemeIcon('dark');
    } else {
        document.body.classList.remove('dark-theme');
        updateThemeIcon('light');
    }
}

function updateThemeIcon(theme) {
    const icon = document.getElementById('themeIcon');
    if (icon) {
        if (theme === 'dark') {
            icon.className = 'fas fa-sun';
        } else {
            icon.className = 'fas fa-moon';
        }
    }
}

window.toggleTheme = async function() {
    const isDark = document.body.classList.toggle('dark-theme');
    const newTheme = isDark ? 'dark' : 'light';
    
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
    
    // Sync with backend if logged in
    const token = localStorage.getItem('jwt_token');
    if (token && window.AppAPI) {
        try {
            await AppAPI.postRequest('/user/theme', { theme: newTheme });
        } catch (e) {
            console.error("Failed to sync theme to backend", e);
        }
    }
};

// Initialize theme immediately
initTheme();

// --- AI ENGINE STATUS SYSTEM ---
let aiStatusPolling = null;

async function checkAIStatus() {
    const btn = document.getElementById('ai-ready-btn');
    const dot = document.getElementById('ai-status-dot');
    const text = document.getElementById('ai-status-text');
    if (!btn || !window.AppAPI) return;

    try {
        const response = await AppAPI.getRequest('/config/ollama/status');
        if (response.is_running) {
            btn.classList.add('ready');
            btn.classList.remove('waking');
            dot.className = 'status-dot ready';
            text.textContent = 'AI Ready';
            btn.title = "AI Engine is active and pre-loaded.";
        } else {
            btn.classList.remove('ready', 'waking');
            dot.className = 'status-dot';
            text.textContent = 'Ready AI';
            btn.title = "Local AI is offline. Click to initiate and pre-load.";
        }
    } catch (e) {
        console.error("AI Status check failed", e);
    }
}

window.initiateAI = async function() {
    const btn = document.getElementById('ai-ready-btn');
    const dot = document.getElementById('ai-status-dot');
    const text = document.getElementById('ai-status-text');
    
    if (btn.classList.contains('ready') || btn.classList.contains('waking')) return;

    btn.classList.add('waking');
    dot.className = 'status-dot waking';
    text.textContent = 'Waking Up...';

    try {
        const response = await AppAPI.postRequest('/config/ollama/start');
        if (response.success) {
            checkAIStatus();
        } else {
            showError(response.message || "Failed to start AI Engine.");
            btn.classList.remove('waking');
            dot.className = 'status-dot';
            text.textContent = 'Ready AI';
        }
    } catch (e) {
        showError("Backend error while triggering AI initiation.");
        btn.classList.remove('waking');
        dot.className = 'status-dot';
        text.textContent = 'Ready AI';
    }
}

// Start polling if logged in
// (Moved to initialization block above)

// Register globally
window.checkAIStatus = checkAIStatus;
window.initiateAI = initiateAI;
