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
    console.error('Error fetching stats:', error);
    // Return default stats if API fails
    return {
      totalSent: 0,
      totalCustomers: 0,
      sentToday: 0,
      scheduledEmails: 0,
      thisWeekSent: 0,
      totalCampaigns: 0,
      todayChange: 0,
      weekChange: 0,
      monthChange: 0,
      todaySuccessRate: 0,
      yesterdaySuccessRate: 0,
      overallSuccessRate: 0
    };
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
      throw new Error('Failed to fetch activity');
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching activity:', error);
    return [];
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
      throw new Error('Failed to fetch campaigns');
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching campaigns:', error);
    return [];
  }
}; 