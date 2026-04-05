let allHistory = [];

document.addEventListener('DOMContentLoaded', async () => {

    const tableBody = document.getElementById('historyTableBody');
    const formError = document.getElementById('formError');

    try {
        const response = await AppAPI.request('/history');
        if (response.success && response.history) {
            allHistory = response.history;
            renderHistoryTable(allHistory);
        }
    } catch (e) {
        formError.textContent = e.message || 'Failed to load history data.';
        formError.style.display = 'block';
    }

    window.applyFilters = function () {
        const filterDate = document.getElementById('filterDate').value;
        const filterType = document.getElementById('filterType').value;

        let filtered = allHistory;

        if (filterDate) {
            filtered = filtered.filter(item => item.date === filterDate);
        }

        if (filterType) {
            filtered = filtered.filter(item => item.type === filterType);
        }

        renderHistoryTable(filtered);
    };

    function renderHistoryTable(data) {
        if (!data.length) {
            tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 40px;">No history records found.</td></tr>';
            return;
        }

        let html = '';
        data.forEach(row => {
            let badgeClass = 'badge-medium';
            if (row.type === 'UAT') badgeClass = 'badge-high';
            else if (row.type === 'JIRA') badgeClass = 'badge-low';

            html += `
                <tr>
                    <td>${row.date}</td>
                    <td><strong>${row.id}</strong></td>
                    <td><span class="badge ${badgeClass}">${row.type}</span></td>
                    <td>${row.itemsGenerated} test cases</td>
                    <td>${row.author}</td>
                    <td>
                        <button class="btn btn-secondary" style="padding: 4px 10px; font-size: 0.8rem;" onclick="viewDetails('${row.id}')">
                            <i class="fas fa-eye"></i> View
                        </button>
                    </td>
                </tr>
            `;
        });
        tableBody.innerHTML = html;
    }

    window.viewDetails = function (id) {
        // Extract numeric ID from HST-xxx format
        const numericId = id.replace('HST-', '');
        alert(`Viewing details for record ${numericId}. This could open a detail modal in production.`);
    }
});
