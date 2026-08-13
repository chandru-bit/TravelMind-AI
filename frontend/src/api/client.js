import axios from 'axios';

// API Base URL - Proxied by Vite or direct to API Gateway
const API_BASE_URL = import.meta.env.VITE_API_GATEWAY_URL || '/api';

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
    let errorMessage = 'Something went wrong on our server. Please try again.';

    if (error.response) {
      const status = error.response.status;
      const apiErr = error.response.data?.error;
      const detail = error.response.data?.detail;

      if (apiErr && typeof apiErr.message === 'string') {
        errorMessage = apiErr.message;
      } else if (typeof detail === 'string') {
        errorMessage = detail;
      } else if (Array.isArray(detail) && detail.length > 0 && detail[0].msg) {
        errorMessage = detail[0].msg;
      } else if (status === 401) {
        errorMessage = 'Invalid email or password. Please check your credentials.';
      } else if (status === 404) {
        errorMessage = 'The requested endpoint or resource was not found.';
      } else if (status === 429) {
        errorMessage = 'Too many requests. Please wait a moment before trying again.';
      } else if (status >= 500) {
        errorMessage = 'Server temporary error. Please try again later.';
      }
    } else if (error.request) {
      errorMessage = 'Unable to connect to TravelMind AI server. Please check your network connection.';
    }

    error.userFriendlyMessage = errorMessage;
    return Promise.reject(error);
  }
);

export default api;
