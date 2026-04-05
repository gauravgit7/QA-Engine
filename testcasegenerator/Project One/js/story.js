document.addEventListener('DOMContentLoaded', () => {

    const resultsCard = document.getElementById('resultsCard');
    const casesTableBody = document.getElementById('casesTableBody');
    const generateBtn = document.getElementById('generateBtn');
    const formError = document.getElementById('formError');

    document.getElementById('storyForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        formError.style.display = 'none';
        const storyContext = document.getElementById('storyContext').value.trim();

        if (!storyContext) {
            formError.textContent = 'Story Context is required.';
            formError.style.display = 'block';
            return;
        }

        const originalBtnHtml = generateBtn.innerHTML;
        const genMethodInput = document.querySelector('input[name="genMethod"]:checked');
        const genMethod = genMethodInput ? genMethodInput.value : 'llm';
        
        let loadingInterval;
        if (genMethod === 'llm') {
            const messages = [
                'Analyzing story context...',
                'Connecting to local Llama 3...',
                'Local AI is thinking (this may take a minute)...',
                'Synthesizing test scenarios...',
                'Formatting structured JSON...',
                'Almost ready...'
            ];
            let msgIdx = 0;
            generateBtn.innerHTML = `<div class="spinner"></div> ${messages[0]}`;
            loadingInterval = setInterval(() => {
                msgIdx = (msgIdx + 1) % messages.length;
                generateBtn.innerHTML = `<div class="spinner"></div> ${messages[msgIdx]}`;
            }, 5000);
        } else {
            generateBtn.innerHTML = '<div class="spinner"></div> Generating...';
        }
        
        generateBtn.disabled = true;

        try {
            // Build FormData for multipart upload
            const formData = new FormData();
            formData.append('text', storyContext);

            const storyIdVal = document.getElementById('storyId').value.trim();
            if (storyIdVal) formData.append('story_id', storyIdVal);
            
            const genMethod = document.querySelector('input[name="genMethod"]:checked').value;
            formData.append('generation_method', genMethod);
            formData.append('options', JSON.stringify({
                test_case_count: 5,
                include_negative: true,
                include_edge: true
            }));

            const fileUpload = document.getElementById('fileUpload');
            if (fileUpload && fileUpload.files.length > 0) {
                formData.append('file', fileUpload.files[0]);
            }

            const response = await AppAPI.uploadRequest('/generate/story', formData);

            if (response.success && response.testCases) {
                renderTestCases(response.testCases);
                
                // Render metadata
                const metadataDiv = document.getElementById('genMetadata');
                metadataDiv.innerHTML = `
                    <span><strong>Method Used:</strong> ${response.method_used === "rules" ? "Rules Engine" : response.method_used}</span>
                    <span><strong>Time:</strong> ${response.generation_time.toFixed(2)}s</span>
                    ${response.method_used !== "rules" ? `<span><strong>Tokens:</strong> ${response.token_usage}</span><span><strong>Est. Cost:</strong> $${response.cost.toFixed(5)}</span>` : ''}
                `;
                metadataDiv.style.display = 'flex';
                
                const warningDiv = document.getElementById('fallbackWarning');
                if (response.fallback_triggered) {
                    warningDiv.style.display = 'block';
                    warningDiv.textContent = `Warning: Fallback triggered. Reason: ${response.fallback_reason || 'Unknown error'}`;
                } else {
                    warningDiv.style.display = 'none';
                }

                resultsCard.classList.remove('d-none');
                resultsCard.scrollIntoView({ behavior: 'smooth' });
            }

        } catch (error) {
            formError.textContent = error.message || 'Error occurred while generating test cases.';
            formError.style.display = 'block';
        } finally {
            if (loadingInterval) clearInterval(loadingInterval);
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
                    <td>${tc.test_type || 'Functional'}</td>
                    <td style="font-size: 0.85rem; word-break: break-all;">${tc.test_data || 'N/A'}</td>
                    <td><span class="badge ${badgeClass}">${tc.priority}</span></td>
                </tr>
            `;
        });
        casesTableBody.innerHTML = html;
    }
});
