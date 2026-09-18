const API_BASE_URL = 'http://127.0.0.1:8000/api';

// ============================================================
// Хранение токенов
// ============================================================

function getAccessToken() {
    return localStorage.getItem('access_token');
}

function getRefreshToken() {
    return localStorage.getItem('refresh_token');
}

function setTokens(access, refresh) {
    localStorage.setItem('access_token', access);
    if (refresh) {
        localStorage.setItem('refresh_token', refresh);
    }
}

function clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
}

function isLoggedIn() {
    return !!getAccessToken();
}

// ============================================================
// Обновление access-токена через refresh
// ============================================================

async function refreshAccessToken() {
    const refresh = getRefreshToken();
    if (!refresh) return false;

    try {
        const response = await fetch(`${API_BASE_URL}/users/login/refresh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh }),
        });

        if (!response.ok) {
            clearTokens();
            return false;
        }

        const data = await response.json();
        setTokens(data.access, null);
        return true;
    } catch (err) {
        clearTokens();
        return false;
    }
}

// ============================================================
// Основная обёртка для запросов к API
// ============================================================

async function apiRequest(path, options = {}) {
    const isFormData = options.body instanceof FormData;

    const headers = {
        ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
        ...options.headers,
    };

    const token = getAccessToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    let response = await fetch(`${API_BASE_URL}${path}`, {
        ...options,
        headers,
    });

    // Если токен истёк — пробуем обновить и повторить запрос один раз
    if (response.status === 401 && token) {
        const refreshed = await refreshAccessToken();
        if (refreshed) {
            headers['Authorization'] = `Bearer ${getAccessToken()}`;
            response = await fetch(`${API_BASE_URL}${path}`, {
                ...options,
                headers,
            });
        }
    }

    return response;
}

// ============================================================
// Удобные шорткаты
// ============================================================

async function apiGet(path) {
    const response = await apiRequest(path, { method: 'GET' });
    return handleResponse(response);
}

async function apiPost(path, data) {
    const isFormData = data instanceof FormData;
    const response = await apiRequest(path, {
        method: 'POST',
        body: isFormData ? data : JSON.stringify(data),
    });
    return handleResponse(response);
}

async function apiPatch(path, data) {
    const response = await apiRequest(path, {
        method: 'PATCH',
        body: JSON.stringify(data),
    });
    return handleResponse(response);
}

async function apiDelete(path) {
    const response = await apiRequest(path, { method: 'DELETE' });
    if (response.status === 204) return null;
    return handleResponse(response);
}

async function handleResponse(response) {
    if (!response.ok) {
        let errorData;
        try {
            errorData = await response.json();
        } catch {
            errorData = { detail: `Error ${response.status}` };
        }
        throw { status: response.status, data: errorData };
    }
    if (response.status === 204) return null;
    return response.json();
}