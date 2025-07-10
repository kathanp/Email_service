import { API_ENDPOINTS } from '../config';

const API_URL = API_ENDPOINTS.AUTH;

export async function register({ name, email, password }) {
  const res = await fetch(`${API_URL}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ full_name: name, email, password }),
  });
  if (!res.ok) throw new Error((await res.json()).detail || "Registration failed");
  return await res.json();
}

export async function login({ email, password }) {
  const res = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error((await res.json()).detail || "Login failed");
  return await res.json();
}

export async function connectGmail() {
  // User clicks "Connect Gmail"
  // Your app redirects to Google (using YOUR OAuth credentials)
  // User authorizes your app to send emails from their Gmail
  // Google sends back tokens to your app
  // User can now send emails from their own Gmail address
  const res = await fetch(`${API_URL}/connect-gmail`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) throw new Error((await res.json()).detail || "Gmail connection failed");
  return await res.json();
}

let isRedirecting = false;

export const handleAuthError = (response) => {
  if ((response.status === 401 || response.status === 403) && !isRedirecting) {
    // Token is expired or invalid, redirect to login
    isRedirecting = true;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    
    // Only redirect if not already on login page
    if (window.location.pathname !== '/login') {
      window.location.href = '/login';
    }
    
    return true; // Indicates auth error was handled
  }
  return false; // No auth error
};

export const apiRequest = async (url, options = {}) => {
  const token = localStorage.getItem('token');

  const config = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  try {
    const response = await fetch(url, config);

    // Check for auth errors
    if (handleAuthError(response)) {
      return null; // Request was interrupted due to auth error
    }

    return response;
  } catch (error) {
    throw new Error('API request failed');
  }
};