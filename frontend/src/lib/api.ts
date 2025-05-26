import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/v1',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add request interceptor for handling errors
api.interceptors.request.use(
    (config) => config,
    (error) => Promise.reject(error)
);

// Add response interceptor for handling errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            console.error('API Error:', error.response.data);
            return Promise.reject(error.response.data);
        } else if (error.request) {
            // The request was made but no response was received
            console.error('Network Error:', error.request);
            return Promise.reject(new Error('Network error occurred'));
        } else {
            // Something happened in setting up the request that triggered an Error
            console.error('Request Error:', error.message);
            return Promise.reject(error);
        }
    }
);

export default api; 