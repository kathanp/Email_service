import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
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
    totalCustomers: 0,
    scheduledEmails: 0,
    sentToday: 0,
    totalSent: 0,
    todayChange: 0,
    monthChange: 0,
    totalEmails: 0,
    totalCampaigns: 0,
    totalTemplates: 0,
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

  const apiRequest = useCallback(async (url, options = {}) => {
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
  }, []);

  const fetchStats = useCallback(async () => {
    try {
      const response = await apiRequest(`${API_ENDPOINTS.STATS}/overview`);
      if (response.ok) {
        const data = await response.json();
        setStats(prevStats => ({
          ...prevStats,
          totalCustomers: data.total_customers || 0,
          scheduledEmails: data.total_campaigns || 0,
          sentToday: 25, // Mock data for now
          totalSent: data.total_campaigns * 100 || 0, // Mock calculation
          todayChange: 12, // Mock data
          monthChange: 8, // Mock data
          totalEmails: data.total_campaigns || 0,
          totalCampaigns: data.total_campaigns || 0,
          totalTemplates: data.total_templates || 0,
          totalSenders: data.total_senders || 0,
          emailsSentToday: 25, // Mock data
          emailsSentThisMonth: data.total_campaigns * 100 || 0, // Mock calculation
          successRate: 95 // Default success rate
        }));
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  }, [apiRequest]);

  const fetchActivity = useCallback(async () => {
    try {
      // For now, create mock activity data since we don't have this endpoint
      const mockActivity = [
        {
          id: 1,
          type: 'campaign_sent',
          message: 'Welcome campaign sent to 150 customers',
          timestamp: new Date().toISOString()
        },
        {
          id: 2,
          type: 'template_created',
          message: 'New template "Newsletter Template" created',
          timestamp: new Date(Date.now() - 86400000).toISOString()
        }
      ];
      
      setStats(prevStats => ({
        ...prevStats,
        recentActivity: mockActivity
      }));
    } catch (error) {
      console.error('Error fetching activity:', error);
    }
  }, []);

  const fetchCampaignStats = useCallback(async () => {
    try {
      const response = await apiRequest(`${API_ENDPOINTS.STATS}/campaigns`);
      if (response.ok) {
        const data = await response.json();
        setStats(prevStats => ({
          ...prevStats,
          campaignStats: [
            {
              total: data.total_campaigns || 0,
              active: data.active_campaigns || 0,
              completed: data.completed_campaigns || 0,
              draft: data.draft_campaigns || 0
            }
          ]
        }));
      }
    } catch (error) {
      console.error('Error fetching campaign stats:', error);
    }
  }, [apiRequest]);

  const fetchTemplates = useCallback(async () => {
    try {
      const response = await apiRequest(`${API_ENDPOINTS.TEMPLATES}/`);
      if (response.ok) {
        const data = await response.json();
        setTemplates(data);
      }
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  }, [apiRequest]);

  const createTemplate = useCallback(async (templateData) => {
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
  }, [apiRequest]);

  const updateTemplate = useCallback(async (templateId, templateData) => {
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
  }, [apiRequest]);

  const setDefaultTemplate = useCallback(async (templateId) => {
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
  }, [apiRequest]);

  const deleteTemplate = useCallback(async (templateId) => {
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
  }, [apiRequest]);

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