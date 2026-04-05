document.addEventListener('DOMContentLoaded', async () => {

    const configForm = document.getElementById('configForm');
    const saveBtn = document.getElementById('saveBtn');
    const configSuccess = document.getElementById('configSuccess');
    const configError = document.getElementById('configError');

    // Load existing config from backend
    await loadConfig();

    configForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        configSuccess.style.display = 'none';
        configError.style.display = 'none';

        const originalBtnHtml = saveBtn.innerHTML;
        saveBtn.innerHTML = '<div class="spinner"></div> Saving...';
        saveBtn.disabled = true;

        try {
            const payload = {
                jira_base_url: document.getElementById('jiraBaseUrl').value.trim(),
                jira_email: document.getElementById('jiraEmail').value.trim(),
                jira_api_token: document.getElementById('jiraToken').value.trim(),
                llm_api_key: document.getElementById('llmApiKey').value.trim(),
                ollama_model: document.getElementById('ollamaModel').value.trim()
            };

            const response = await AppAPI.request('/config/save', {
                method: 'POST',
                body: JSON.stringify(payload)
            });

            if (response.success) {
                configSuccess.textContent = response.message || 'Configuration saved successfully.';
                configSuccess.style.display = 'block';

                setTimeout(() => {
                    configSuccess.style.display = 'none';
                }, 3000);
            }
        } catch (error) {
            configError.textContent = error.message || 'Error occurred while saving configuration.';
            configError.style.display = 'block';
        } finally {
            saveBtn.innerHTML = originalBtnHtml;
            saveBtn.disabled = false;
        }
    });

    window.togglePasswordVisibility = function (inputId) {
        const input = document.getElementById(inputId);
        const icon = document.getElementById(inputId + 'Icon');

        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            input.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    };

    async function loadConfig() {
        try {
            const response = await AppAPI.request('/config');
            if (response.success) {
                document.getElementById('jiraBaseUrl').value = response.jira_base_url || '';
                document.getElementById('jiraEmail').value = response.jira_email || '';
                document.getElementById('jiraToken').value = response.jira_api_token || '';
                document.getElementById('llmApiKey').value = response.llm_api_key || '';
                document.getElementById('ollamaModel').value = response.ollama_model || 'llama3:latest';
            }
        } catch (e) {
            // Config not set yet — that's fine
            console.log('No existing config found.');
        }
    }
});
