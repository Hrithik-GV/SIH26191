import axios from 'axios';

// Base API URL with fallback
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Direct backend root URL (stripping /api/v1) for root endpoints
export const BACKEND_ROOT_URL = API_BASE_URL.replace(/\/api\/v1\/?$/, '');

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// Response interceptor for consistent error normalization
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const errorDetails = {
      message: error.response?.data?.error?.message || error.message || 'Network Error',
      status: error.response?.status,
      data: error.response?.data,
      url: error.config?.url,
    };
    console.error('[API Response Error]', errorDetails);
    return Promise.reject(errorDetails);
  }
);

export const checkSystemHealth = async () => {
  // Query both the direct /health root and /api/v1/health
  const startTime = performance.now();
  try {
    const response = await axios.get(`${BACKEND_ROOT_URL}/health`, { timeout: 5000 });
    const roundTripTime = Math.round(performance.now() - startTime);
    return {
      success: true,
      data: response.data,
      latency: roundTripTime,
      error: null,
    };
  } catch (err) {
    const roundTripTime = Math.round(performance.now() - startTime);
    return {
      success: false,
      data: null,
      latency: roundTripTime,
      error: err.response?.data?.error?.message || err.message || 'Cannot connect to backend server',
    };
  }
};

export const pingBackend = async () => {
  const startTime = performance.now();
  try {
    const response = await apiClient.get('/ping', { timeout: 4000 });
    const latency = Math.round(performance.now() - startTime);
    return {
      success: true,
      data: response.data,
      latency,
      error: null,
    };
  } catch (err) {
    const latency = Math.round(performance.now() - startTime);
    return {
      success: false,
      data: null,
      latency,
      error: err.message || 'Ping failed',
    };
  }
};
