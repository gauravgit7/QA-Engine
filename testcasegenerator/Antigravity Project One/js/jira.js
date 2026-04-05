document.addEventListener('DOMContentLoaded', () => {

    const resultsCard = document.getElementById('resultsCard');
    const casesTableBody = document.getElementById('casesTableBody');
    const generateBtn = document.getElementById('generateBtn');
    const formError = document.getElementById('formError');

    document.getElementById('jiraForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        formError.style.display = 'none';
        const jiraTicketId = document.getElementById('jiraTicketId').value.trim();

        if (!jiraTicketId) {
            formError.textContent = 'Jira Ticket ID is required.';
            formError.style.display = 'block';
            return;
        }

        const originalBtnHtml = generateBtn.innerHTML;
        generateBtn.innerHTML = '<div class="spinner"></div> Processing...';
        generateBtn.disabled = true;

        try {
            // GET request with story ID in path
            const response = await AppAPI.request(`/jira/story/${encodeURIComponent(jiraTicketId)}`);

            if (response.success && response.testCases) {
                renderTestCases(response.testCases);
                resultsCard.classList.remove('d-none');
                resultsCard.scrollIntoView({ behavior: 'smooth' });
            }

        } catch (error) {
            formError.textContent = error.message || 'Error occurred while generating test cases.';
            formError.style.display = 'block';
        } finally {
            generateBtn.innerHTML = originalBtnHtml;
            generateBtn.disabled = false;
        }
    });

    function renderTestCases(cases) {
        let html = '';
        cases.forEach(tc => {
            let badgeClass = 'badge-medium';
            if (tc.priority === 'High') badgeClass = 'badge-high';
            else if (tc.priority === 'Low') badgeClass = 'badge-low';

            const formatSteps = tc.steps.replace(/\\n|\n/g, '<br>');

            html += `
                <tr>
                    <td><strong>${tc.id}</strong></td>
                    <td>${tc.title}</td>
                    <td class="text-muted" style="font-size: 0.9rem;">${tc.preconditions}</td>
                    <td style="font-size: 0.9rem;">${formatSteps}</td>
                    <td style="font-size: 0.9rem;">${tc.expectedResult}</td>
                    <td><span class="badge ${badgeClass}">${tc.priority}</span></td>
                </tr>
            `;
        });
        casesTableBody.innerHTML = html;
    }
});
