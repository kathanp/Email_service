import React, { createContext, useContext, useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../config';

const AppContext = createContext();

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};

export const AppProvider = ({ children }) => {
  const [stats, setStats] = useState({
    totalEmails: 0,
    totalCampaigns: 0,
    totalTemplates: 0,
    totalCustomers: 0,
    totalSenders: 0,
    emailsSentToday: 0,
    emailsSentThisMonth: 0,
    successRate: 0,
    recentActivity: [],
    campaignStats: []
  });

  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const apiRequest = async (url, options = {}) => {
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
      return response;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  };

  const fetchStats = async () => {
    try {
      const response = await apiRequest(`${API_ENDPOINTS.STATS}/summary`);
      if (response.ok) {
        const data = await response.json();
        setStats(prevStats => ({
          ...prevStats,
          totalEmails: data.totalEmails || 0,
          totalCampaigns: data.totalCampaigns || 0,
          totalTemplates: data.totalTemplates || 0,
          totalCustomers: data.totalCustomers || 0,
          totalSenders: data.totalSenders || 0,
          emailsSentToday: data.emailsSentToday || 0,
          emailsSentThisMonth: data.emailsSentThisMonth || 0,
          successRate: data.successRate || 0
        }));
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchActivity = async () => {
    try {
      const response = await apiRequest(`${API_ENDPOINTS.STATS}/activity`);
      if (response.ok) {
        const data = await response.json();
        setStats(prevStats => ({
          ...prevStats,
          recentActivity: data.recentActivity || []
        }));
      }
    } catch (error) {
      console.error('Error fetching activity:', error);
    }
  };

  const fetchCampaignStats = async () => {
    try {
      const response = await apiRequest(`${API_ENDPOINTS.STATS}/campaigns`);
      if (response.ok) {
        const data = await response.json();
        setStats(prevStats => ({
          ...prevStats,
          campaignStats: data.campaignStats || []
        }));
      }
    } catch (error) {
      console.error('Error fetching campaign stats:', error);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await apiRequest(`${API_ENDPOINTS.TEMPLATES}/`);
      if (response.ok) {
        const data = await response.json();
        setTemplates(data);
      }
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const createTemplate = async (templateData) => {
    try {
      const response = await apiRequest(`${API_ENDPOINTS.TEMPLATES}/`, {
        method: 'POST',
        body: JSON.stringify(templateData)
      });
      
      if (response.ok) {
        const newTemplate = await response.json();
        setTemplates(prev => [...prev, newTemplate]);
        return { success: true, template: newTemplate };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.detail || 'Failed to create template' };
      }
    } catch (error) {
      console.error('Error creating template:', error);
      return { success: false, error: 'Network error' };
    }
  };

  const updateTemplate = async (templateId, templateData) => {
    try {
      const response = await apiRequest(`${API_ENDPOINTS.TEMPLATES}/${templateId}`, {
        method: 'PUT',
        body: JSON.stringify(templateData)
      });
      
      if (response.ok) {
        const updatedTemplate = await response.json();
        setTemplates(prev => prev.map(t => t.id === templateId ? updatedTemplate : t));
        return { success: true, template: updatedTemplate };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.detail || 'Failed to update template' };
      }
    } catch (error) {
      console.error('Error updating template:', error);
      return { success: false, error: 'Network error' };
    }
  };

  const setDefaultTemplate = async (templateId) => {
    try {
      const response = await apiRequest(`${API_ENDPOINTS.TEMPLATES}/${templateId}/set-default`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const updatedTemplate = await response.json();
        setTemplates(prev => prev.map(t => ({
          ...t,
          is_default: t.id === templateId
        })));
        return { success: true, template: updatedTemplate };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.detail || 'Failed to set default template' };
      }
    } catch (error) {
      console.error('Error setting default template:', error);
      return { success: false, error: 'Network error' };
    }
  };

  const deleteTemplate = async (templateId) => {
    try {
      const response = await apiRequest(`${API_ENDPOINTS.TEMPLATES}/${templateId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        setTemplates(prev => prev.filter(t => t.id !== templateId));
        return { success: true };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.detail || 'Failed to delete template' };
      }
    } catch (error) {
      console.error('Error deleting template:', error);
      return { success: false, error: 'Network error' };
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        await Promise.all([
          fetchStats(),
          fetchActivity(),
          fetchCampaignStats(),
          fetchTemplates()
        ]);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [fetchStats, fetchActivity, fetchCampaignStats, fetchTemplates]);

  const value = {
    stats,
    templates,
    loading,
    error,
    fetchStats,
    fetchActivity,
    fetchCampaignStats,
    fetchTemplates,
    createTemplate,
    updateTemplate,
    setDefaultTemplate,
    deleteTemplate
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
}; 