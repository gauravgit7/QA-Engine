document.addEventListener('DOMContentLoaded', async () => {
    
    // Load dashboard stats
    try {
        const response = await AppAPI.request('/dashboard/stats');
        if (response.success && response.stats) {
            renderStatsGrid(response.stats);
        }
        
        const historyResponse = await AppAPI.request('/history');
        if (historyResponse.success && historyResponse.history) {
            renderRecentActivity(historyResponse.history.slice(0, 5));
        }

        renderCharts();

    } catch (e) {
        console.error('Error loading dashboard data', e);
    }

});

function renderStatsGrid(stats) {
    const statsGrid = document.getElementById('statsGrid');
    
    const items = [
        { icon: 'fas fa-vials', title: 'Total Generated', value: stats.totalGenerated, color: '--accent-color' },
        { icon: 'fas fa-calendar-week', title: 'Generated This Week', value: stats.thisWeek, color: '--success-color' },
        { icon: 'fab fa-jira', title: 'Jira Synced', value: stats.jiraSynced, color: '#0052cc' },
        { icon: 'fas fa-users', title: 'Active Users', value: stats.activeUsers, color: '--secondary-color' }
    ];

    let html = '';
    items.forEach(item => {
        html += `
            <div class="card stat-card" style="margin-bottom: 0;">
                <div class="stat-icon" style="color: var(${item.color}); background-color: rgba(0,0,0,0.05);">
                    <i class="${item.icon}"></i>
                </div>
                <div class="stat-content">
                    <p>${item.title}</p>
                    <h3>${item.value}</h3>
                </div>
            </div>
        `;
    });
    
    statsGrid.innerHTML = html;
}

function renderRecentActivity(history) {
    const tableBody = document.getElementById('recentActivityTable');
    if (!history.length) {
        tableBody.innerHTML = '<tr><td colspan="3" class="text-center text-muted">No recent activity found.</td></tr>';
        return;
    }

    let html = '';
    history.forEach(row => {
        let badgeClass = 'badge-medium';
        if (row.type === 'UAT') badgeClass = 'badge-high';
        else if (row.type === 'Jira') badgeClass = 'badge-low';

        html += `
            <tr>
                <td>${row.date}</td>
                <td><span class="badge ${badgeClass}">${row.type} Module</span></td>
                <td><strong>${row.itemsGenerated}</strong> test cases</td>
            </tr>
        `;
    });
    
    tableBody.innerHTML = html;
}

function renderCharts() {
    // Setup generic theme defaults for chart js
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.color = "#6c757d";
    
    // Line Chart: Generation Trends
    const ctxTrend = document.getElementById('generationChart').getContext('2d');
    
    // Create gradient
    const gradient = ctxTrend.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(0, 180, 216, 0.5)');   
    gradient.addColorStop(1, 'rgba(0, 180, 216, 0.0)');

    new Chart(ctxTrend, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Test Cases Generated',
                data: [12, 19, 15, 25, 22, 5, 8],
                borderColor: '#00b4d8',
                backgroundColor: gradient,
                borderWidth: 2,
                pointBackgroundColor: '#0d1b2a',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#00b4d8',
                fill: true,
                tension: 0.4 // curve
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true, grid: { borderDash: [5, 5] } },
                x: { grid: { display: false } }
            }
        }
    });

    // Doughnut Chart: Modules
    const ctxModule = document.getElementById('moduleChart').getContext('2d');
    new Chart(ctxModule, {
        type: 'doughnut',
        data: {
            labels: ['UAT', 'Story/Feature', 'Jira'],
            datasets: [{
                data: [45, 25, 30],
                backgroundColor: ['#0d1b2a', '#0077b6', '#00b4d8'],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' }
            },
            cutout: '70%'
        }
    });
}
