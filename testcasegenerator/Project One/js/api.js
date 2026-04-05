const API_BASE_URL = 'http://127.0.0.1:8000';

const AppAPI = {
    getToken: () => localStorage.getItem('jwt_token'),

    setToken: (token) => {
        if (token) localStorage.setItem('jwt_token', token);
        else localStorage.removeItem('jwt_token');
    },

    request: async (endpoint, options = {}) => {
        const token = AppAPI.getToken();

        const headers = {
            ...(token && { 'Authorization': `Bearer ${token}` }),
            ...options.headers
        };

        // Only set Content-Type to JSON if body is not FormData
        if (!(options.body instanceof FormData)) {
            headers['Content-Type'] = 'application/json';
        }

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: options.method || 'GET',
                headers: headers,
                body: options.body || undefined,
            });

            const data = await response.json();

            if (!response.ok) {
                // Handle 401 - redirect to login
                if (response.status === 401) {
                    AppAPI.setToken(null);
                    window.location.href = 'index.html';
                    return;
                }
                throw new Error(data.message || `Request failed with status ${response.status}`);
            }

            return data;

        } catch (error) {
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new Error('Cannot connect to the server. Make sure the backend is running on ' + API_BASE_URL);
            }
            throw error;
        }
    },

    getRequest: async (endpoint) => AppAPI.request(endpoint, { method: 'GET' }),

    postRequest: async (endpoint, body = {}) => AppAPI.request(endpoint, {
        method: 'POST',
        body: JSON.stringify(body)
    }),

    /**
     * Helper for multipart/form-data uploads (used by UAT and Story generators).
     * Accepts an object of key-value pairs and an optional File object.
     */
    uploadRequest: async (endpoint, formData) => {
        const token = AppAPI.getToken();

        const headers = {};
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        // Do NOT set Content-Type — browser sets it with boundary for FormData

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: headers,
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                if (response.status === 401) {
                    AppAPI.setToken(null);
                    window.location.href = 'index.html';
                    return;
                }
                throw new Error(data.message || `Request failed with status ${response.status}`);
            }

            return data;

        } catch (error) {
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new Error('Cannot connect to the server. Make sure the backend is running on ' + API_BASE_URL);
            }
            throw error;
        }
    }
};
