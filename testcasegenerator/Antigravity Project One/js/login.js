document.addEventListener('DOMContentLoaded', () => {
    // If already logged in, redirect to dashboard
    if (localStorage.getItem('jwt_token')) {
        window.location.href = 'dashboard.html';
        return;
    }

    const loginForm = document.getElementById('loginForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const emailError = document.getElementById('emailError');
    const passwordError = document.getElementById('passwordError');
    const loginError = document.getElementById('loginError');
    const loginBtn = document.getElementById('loginBtn');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        let isValid = true;
        
        // Reset errors
        emailError.classList.add('d-none');
        passwordError.classList.add('d-none');
        loginError.style.display = 'none';

        // Validation
        if (!emailInput.value.trim()) {
            emailError.classList.remove('d-none');
            isValid = false;
        }
        
        if (!passwordInput.value.trim()) {
            passwordError.classList.remove('d-none');
            isValid = false;
        }

        if (!isValid) return;

        // Perform login
        const originalBtnText = loginBtn.innerHTML;
        loginBtn.innerHTML = '<div class="spinner"></div> Signing in...';
        loginBtn.disabled = true;

        try {
            const response = await AppAPI.request('/auth/login', {
                method: 'POST',
                body: JSON.stringify({
                    email: emailInput.value.trim(),
                    password: passwordInput.value.trim()
                })
            });

            if (response.success && response.token) {
                AppAPI.setToken(response.token);
                // Redirect on success
                window.location.href = 'dashboard.html';
            }
        } catch (error) {
            loginError.textContent = error.message || 'Login failed. Please try again.';
            loginError.style.display = 'block';
        } finally {
            loginBtn.innerHTML = originalBtnText;
            loginBtn.disabled = false;
        }
    });
});
