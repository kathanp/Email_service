// Set API base URL: use environment variable in production, fallback to current domain for development
const API_BASE_URL = process.env.REACT_APP_API_URL || (window.location.hostname === 'localhost' ? 'http://localhost:8000' : window.location.origin);

export const API_ENDPOINTS = {
  AUTH: `${API_BASE_URL}/api/auth`,
  TEMPLATES: `${API_BASE_URL}/api/templates`,
  FILES: `${API_BASE_URL}/api/files`,
  SENDERS: `${API_BASE_URL}/api/senders`,
  CUSTOMERS: `${API_BASE_URL}/api/customers`,
  STATS: `${API_BASE_URL}/api/stats`,
  CAMPAIGNS: `${API_BASE_URL}/api/campaigns`,
  SUBSCRIPTIONS: `${API_BASE_URL}/api/v1/subscriptions`,
  GOOGLE_AUTH: `${API_BASE_URL}/api/v1/google-auth`,
};

export default API_BASE_URL; 