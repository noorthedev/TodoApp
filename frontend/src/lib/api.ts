<<<<<<< HEAD
import axios, { AxiosInstance, AxiosError } from 'axios';                                                                                                       │
                                                                                                                                                                │
 const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';                                                                                │
                                                                                                                                                                │
 // Create Axios instance                                                                                                                                        │
const apiClient: AxiosInstance = axios.create({                                                                                                                 │
  baseURL: API_BASE_URL,                                                                                                                                        │
 headers: {                                                                                                                                                    │
     'Content-Type': 'application/json',                                                                                                                         │
  },                                                                                                                                                            │
});                                                                                                                                                             │
                                                                                                                                                                 │
 // Request interceptor: inject JWT token                                                                                                                        │
 apiClient.interceptors.request.use(                                                                                                                             │
   (config) => {                                                                                                                                                 │
    const token = localStorage.getItem('auth_token');                                                                                                           │
    if (token) {                                                                                                                                                │
      config.headers.Authorization = `Bearer ${token}`;                                                                                                         │
   }                                                                                                                                                           │
    return config;                                                                                                                                              │
  },                                                                                                                                                            │
  (error) => {                                                                                                                                                  │
     return Promise.reject(error);                                                                                                                               │
   }                                                                                                                                                             │
 );                                                                                                                                                              │
                                                                                                                                                                │
// Response interceptor: handle errors                                                                                                                          │
 apiClient.interceptors.response.use(                                                                                                                            │
 (response) => response,                                                                                                                                       │
  (error: AxiosError) => {                                                                                                                                      │
     if (error.response?.status === 401) {                                                                                                                       │
     // Token expired or invalid - clear token and redirect to login                                                                                           │
       localStorage.removeItem('auth_token');                                                                                                                    │
       if (typeof window !== 'undefined') {                                                                                                                      │
        window.location.href = '/login';                                                                                                                        │
      }                                                                                                                                                         │
     }                                                                                                                                                           │
    return Promise.reject(error);                                                                                                                               │
   }                                                                                                                                                             │
 );                                                                                                                                                              │
                                                                                                                                                                 │
export default apiClient;                                                                                                                                       │
 // Placeholder for API client functions                                                                                                                         │
 export const api = {};
=======
import axios, { AxiosInstance, AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create Axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: inject JWT token
apiClient.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token');
      if (token) {
        // Cast headers to any to allow Authorization assignment
        (config.headers as any).Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: handle errors
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;

// Placeholder for API client functions
export const api = {};
>>>>>>> f43f4d1 (add)
