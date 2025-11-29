import axios from 'axios';

// Configure the base URL - update this to match your backend API URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: async (username, email, password, first_name = null, last_name = null) => {
    const response = await api.post('/register', { 
      username, 
      email, 
      password,
      first_name,
      last_name
    });
    return response.data;
  },
  
  login: async (username, password) => {
    const response = await api.post('/login', { username, password });
    return response.data;
  },
  
  getProfile: async () => {
    const response = await api.get('/me');
    return response.data;
  },
  
  // Note: Backend doesn't have an update profile endpoint
  // updateProfile: async (data) => {
  //   const response = await api.put('/me', data);
  //   return response.data;
  // },
};

export const paragraphAPI = {
  generateTitle: async (paragraph, max_length = 15, min_length = 5, save_result = true) => {
    const response = await api.post('/generate-title', { 
      paragraph,
      max_length,
      min_length,
      save_result
    });
    return response.data;
  },
  
  getHistory: async (limit = 50, offset = 0) => {
    const response = await api.get(`/saved-results?limit=${limit}&offset=${offset}`);
    return response.data;
  },
  
  deleteResult: async (result_id) => {
    const response = await api.delete(`/saved-results/${result_id}`);
    return response.data;
  },
};

export default api;

