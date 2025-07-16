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
      throw new Error('API request failed');
    }
  }, []);

  const fetchStats = useCallback(async () => {
    try {
      // Fetch overview stats
      const overviewResponse = await apiRequest(`${API_ENDPOINTS.STATS}/summary`);
      if (overviewResponse.ok) {
        const overviewData = await overviewResponse.json();
        setStats(prevStats => ({
          ...prevStats,
          totalCustomers: overviewData.totalCustomers || 0,
          scheduledEmails: overviewData.scheduledEmails || 0,
          sentToday: overviewData.sentToday || 0,
          totalSent: overviewData.totalSent || 0,
          todayChange: overviewData.todayChange || 0,
          monthChange: overviewData.monthChange || 0,
          totalEmails: overviewData.totalSent || 0,
          totalCampaigns: overviewData.totalCampaigns || 0,
          emailsSentToday: overviewData.sentToday || 0,
          emailsSentThisMonth: overviewData.thisMonthSent || 0,
          successRate: overviewData.overallSuccessRate || 0
        }));
      }

      // Fetch campaign stats
      const campaignsResponse = await apiRequest(`${API_ENDPOINTS.STATS}/campaigns`);
      if (campaignsResponse.ok) {
        const campaignsData = await campaignsResponse.json();
        setStats(prevStats => ({
          ...prevStats,
          campaignStats: campaignsData.map(campaign => ({
            id: campaign.id,
            name: campaign.name,
            status: campaign.status,
            totalEmails: campaign.totalEmails,
            successful: campaign.successful,
            failed: campaign.failed,
            successRate: campaign.successRate,
            createdAt: campaign.createdAt
          }))
        }));
      }

      // Fetch recent activity
      const activityResponse = await apiRequest(`${API_ENDPOINTS.STATS}/activity`);
      if (activityResponse.ok) {
        const activityData = await activityResponse.json();
        setStats(prevStats => ({
          ...prevStats,
          recentActivity: activityData
        }));
      }
    } catch (error) {
      // Error handling without console
    }
  }, [apiRequest]);

  const fetchActivity = useCallback(async () => {
    try {
      // Activity is now fetched in fetchStats function
      // This function is kept for backward compatibility
    } catch (error) {
      // Error handling without console
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
      // Error handling without console
    }
  }, [apiRequest]);

  const fetchTemplates = useCallback(async () => {
    try {
      const response = await apiRequest(`${API_ENDPOINTS.TEMPLATES}`);
      if (response.ok) {
        const data = await response.json();
        setTemplates(data || []); // Backend returns direct array, not {templates: [...]}
      } else {
        await response.json().catch(() => ({}));
      }
    } catch (error) {
      // Error handling without console
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
        setTemplates(prev => [...(prev || []), newTemplate]);
        return { success: true, template: newTemplate };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.detail || 'Failed to create template' };
      }
    } catch (error) {
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
        setTemplates(prev => (prev || []).map(t => t.id === templateId ? updatedTemplate : t));
        return { success: true, template: updatedTemplate };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.detail || 'Failed to update template' };
      }
    } catch (error) {
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
        setTemplates(prev => (prev || []).map(t => ({
          ...t,
          is_default: t.id === templateId
        })));
        return { success: true, template: updatedTemplate };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.detail || 'Failed to set default template' };
      }
    } catch (error) {
      return { success: false, error: 'Network error' };
    }
  }, [apiRequest]);

  const deleteTemplate = useCallback(async (templateId) => {
    try {
      const response = await apiRequest(`${API_ENDPOINTS.TEMPLATES}/${templateId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        setTemplates(prev => (prev || []).filter(t => t.id !== templateId));
        return { success: true };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.detail || 'Failed to delete template' };
      }
    } catch (error) {
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