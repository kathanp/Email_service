// Set API base URL: use environment variable in production, fallback to current domain for development
const getBaseUrl = () => {
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  if (window.location.hostname === 'localhost') {
    return 'http://localhost:8000';
  }
  // Remove trailing slash if present to avoid double slashes
  return window.location.origin.replace(/\/$/, '');
};

const API_BASE_URL = getBaseUrl();

export const API_ENDPOINTS = {
  AUTH: `${API_BASE_URL}/api/auth`,
  TEMPLATES: `${API_BASE_URL}/api/templates`,
  FILES: `${API_BASE_URL}/api/files`,
  FOLDERS: `${API_BASE_URL}/api/folders`,
  SENDERS: `${API_BASE_URL}/api/senders`,
  STATS: `${API_BASE_URL}/api/stats`,
  CAMPAIGNS: `${API_BASE_URL}/api/campaigns`,
  CONTACTS: `${API_BASE_URL}/api/contacts`,
  SUBSCRIPTIONS: `${API_BASE_URL}/api/subscriptions`,
  SUBSCRIPTIONS_V1: `${API_BASE_URL}/api/v1/subscriptions`,
  GOOGLE_AUTH: `${API_BASE_URL}/api/v1/google-auth`,
};

export default API_BASE_URL; 