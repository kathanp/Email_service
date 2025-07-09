import { API_ENDPOINTS } from '../config';

const API_BASE_URL = API_ENDPOINTS.STATS.replace('/api/stats', '');

export const fetchStats = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}/api/stats/summary`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch stats');
    }

    return await response.json();
  } catch (error) {
    throw new Error('Failed to fetch stats');
  }
};

export const fetchRecentActivity = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}/api/stats/activity`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch activity data');
    }

    return await response.json();
  } catch (error) {
    throw new Error('Failed to fetch activity data');
  }
};

export const fetchRecentCampaigns = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}/api/stats/campaigns`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch campaigns data');
    }

    return await response.json();
  } catch (error) {
    throw new Error('Failed to fetch campaigns data');
  }
}; 