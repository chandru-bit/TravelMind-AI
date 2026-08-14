import axios from 'axios';

// API Base URL - Proxied by Vite or direct to API Gateway
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_GATEWAY_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

// Request Interceptor: Attach Auth Token and Request ID
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('travelmind_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Inject client-generated X-Request-ID if not present
    if (!config.headers['X-Request-ID']) {
      config.headers['X-Request-ID'] = `req-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Centralized Error Formatting
api.interceptors.response.use(
  (response) => response,
  (error) => {
    let errorMessage = 'TravelMind AI encountered a server error. Please try again.';

    if (error.response) {
      const status = error.response.status;
      const apiErr = error.response.data?.error;
      const detail = error.response.data?.detail;

      if (apiErr && typeof apiErr.message === 'string') {
        errorMessage = apiErr.message;
        if (Array.isArray(apiErr.details) && apiErr.details.length > 0) {
          const firstDetail = apiErr.details[0];
          if (typeof firstDetail?.msg === 'string') {
            const field = firstDetail.loc ? firstDetail.loc[firstDetail.loc.length - 1] : '';
            errorMessage = `${firstDetail.msg}${field ? ` (${field})` : ''}`;
          }
        }
      } else if (typeof apiErr === 'string') {
        errorMessage = apiErr;
      } else if (typeof error.response.data?.message === 'string') {
        errorMessage = error.response.data.message;
      } else if (typeof detail === 'string') {
        errorMessage = detail;
      } else if (Array.isArray(detail) && detail.length > 0 && detail[0].msg) {
        errorMessage = detail[0].msg;
      } else if (status === 401) {
        errorMessage = 'Invalid email or password.';
      } else if (status === 404) {
        errorMessage = 'The requested endpoint or resource was not found.';
      } else if (status === 422) {
        errorMessage = 'Please check the information you entered.';
      } else if (status === 429) {
        errorMessage = 'Too many login attempts. Please try again later.';
      } else if (status === 502) {
        errorMessage = 'Authentication service is temporarily unavailable.';
      } else if (status === 503) {
        errorMessage = 'Authentication service is currently unavailable.';
      } else if (status >= 500) {
        errorMessage = 'TravelMind AI encountered a server error. Please try again.';
      }
    } else if (error.request) {
      errorMessage = 'Unable to connect to TravelMind AI.';
    }

    error.userFriendlyMessage = errorMessage;
    return Promise.reject(error);
  }
);

export default api;
