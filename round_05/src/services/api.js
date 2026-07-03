import axios from 'axios';
import { store } from '../store/index'; // Adjust path if necessary once store is created
import { logout, setCredentials } from '../features/auth/authSlice';

// Create an Axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach the JWT token
api.interceptors.request.use(
  (config) => {
    // We can fetch the token directly from Redux store state
    const token = store.getState().auth.token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh and generic errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Check if error is 401 Unauthorized and we haven't already retried
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = store.getState().auth.refreshToken;
        
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }
        
        // Attempt to refresh the token
        const response = await axios.post(
          `${api.defaults.baseURL}/auth/refresh`,
          {}, // empty body
          {
            headers: {
              Authorization: `Bearer ${refreshToken}`
            }
          }
        );
        
        const { access_token } = response.data;
        
        // Update the Redux store with the new access token
        store.dispatch(setCredentials({ 
          token: access_token, 
          refreshToken: refreshToken, // keep the same refresh token
          user: store.getState().auth.user 
        }));
        
        // Update the failed request with the new token and retry
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
        
      } catch (refreshError) {
        // If refresh fails, log the user out
        store.dispatch(logout());
        // In a real app, you might also want to redirect to the login page here
        // window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
