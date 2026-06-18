/**
 * API service for ABBK LeadEngine
 */

const API_BASE_URL = 'http://localhost:8000/api';

// Get auth token from localStorage
const getToken = () => localStorage.getItem('token');

// Set auth token in localStorage
export const setToken = (token) => localStorage.setItem('token', token);

// Remove auth token
export const removeToken = () => localStorage.removeItem('token');

// Generic API call with auth
const apiCall = async (endpoint, options = {}) => {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      removeToken();
      window.location.href = '/';
    }
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
};

// Auth APIs
export const login = async (email, password) => {
  const data = await apiCall('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  setToken(data.access_token);
  return data;
};

export const logout = () => {
  removeToken();
  window.location.href = '/';
};

// Leads APIs
export const getLeads = async () => {
  return apiCall('/leads/');
};

// Scores APIs
export const getRankedLeads = async (limit = 20, minScore = 0) => {
  return apiCall(`/scores/ranked?limit=${limit}&min_score=${minScore}`);
};

export const getLeadScores = async (leadId) => {
  return apiCall(`/scores/${leadId}`);
};

// Health check
export const checkHealth = async () => {
  const response = await fetch('http://localhost:8000/health');
  return response.json();
};
