/**
 * API service for ABBK LeadEngine
 */

const API_BASE_URL = `http://${window.location.hostname}:8000/api`;

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
export const getLeads = async (skip = 0, limit = 1000, sortBy = 'created_at', sortOrder = 'desc') => {
  const params = new URLSearchParams();
  params.append('skip', skip);
  params.append('limit', limit);
  params.append('sort_by', sortBy);
  params.append('sort_order', sortOrder);

  const response = await apiCall(`/leads/?${params.toString()}`);
  // Response format: {leads: [...], total: 349, skip: 0, limit: 1000}
  return response.leads || response || []; // Return the leads array
};

// Scores APIs
export const getRankedLeads = async (limit = 10000, minScore = 0, filters = {}) => {
  const params = new URLSearchParams();
  params.append('limit', limit);
  params.append('min_score', minScore);

  if (filters.sector) params.append('sector', filters.sector);
  if (filters.city) params.append('city', filters.city);
  if (filters.country) params.append('country', filters.country);
  if (filters.status) params.append('status', filters.status);
  if (filters.is_multinational) params.append('is_multinational', 'true');
  if (filters.is_exporter) params.append('is_exporter', 'true');
  if (filters.under_audit) params.append('under_audit', 'true');

  return apiCall(`/scores/ranked?${params.toString()}`);
};

export const getLeadScores = async (leadId) => {
  return apiCall(`/scores/${leadId}`);
};

// Signals APIs
export const getLeadSignals = async (leadId) => {
  return apiCall(`/signals/${leadId}`);
};

// Combined lead detail with scores and signals
export const getLeadDetail = async (leadId) => {
  const [lead, scores, signals] = await Promise.all([
    apiCall(`/leads/${leadId}`),
    apiCall(`/scores/${leadId}`),
    apiCall(`/signals/${leadId}`),
  ]);
  return { lead, scores, signals };
};

// Health check
export const checkHealth = async () => {
  const response = await fetch('http://localhost:8000/health');
  return response.json();
};

// Status Management APIs
export const updateLeadStatus = async (leadId, status, notes = null) => {
  return apiCall(`/leads/${leadId}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status, notes }),
  });
};

export const getLeadStatusHistory = async (leadId) => {
  return apiCall(`/leads/${leadId}/status/history`);
};

// Notifications APIs
export const getNotifications = async (unreadOnly = false, limit = 50) => {
  return apiCall(`/notifications/?unread_only=${unreadOnly}&limit=${limit}`);
};

export const getUnreadCount = async () => {
  return apiCall('/notifications/unread-count');
};

export const markNotificationRead = async (notificationId) => {
  return apiCall(`/notifications/${notificationId}/read`, {
    method: 'PATCH',
  });
};

export const markAllRead = async () => {
  return apiCall('/notifications/mark-all-read', {
    method: 'POST',
  });
};

export const deleteNotification = async (notificationId) => {
  return apiCall(`/notifications/${notificationId}`, {
    method: 'DELETE',
  });
};
