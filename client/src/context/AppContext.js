import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { apiRequest } from '../services/authService';

const AppContext = createContext();

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};

export const AppProvider = ({ children }) => {
  const [templates, setTemplates] = useState([]);
  const [stats, setStats] = useState({
    totalCustomers: 0,
    scheduledEmails: 0,
    sentToday: 0,
    totalSent: 0,
    thisWeekSent: 0,
    monthChange: 0,
    todayChange: 0
  });
  const [recentActivity, setRecentActivity] = useState([]);
  const [recentCampaigns, setRecentCampaigns] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch templates
  const fetchTemplates = useCallback(async () => {
    try {
      const response = await apiRequest('http://localhost:8000/api/templates/');
      if (response && response.ok) {
        const data = await response.json();
        setTemplates(data);
      }
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  }, []);

  // Fetch dashboard stats
  const fetchStats = useCallback(async () => {
    try {
      const response = await apiRequest('http://localhost:8000/api/stats/summary');
      if (response && response.ok) {
        const data = await response.json();
        setStats({
          totalCustomers: data.totalCustomers || 0,
          scheduledEmails: data.scheduledEmails || 0,
          sentToday: data.sentToday || 0,
          totalSent: data.totalSent || 0,
          thisWeekSent: data.thisWeekSent || 0,
          monthChange: data.monthChange || 0,
          todayChange: data.todayChange || 0
        });
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  }, []);

  // Fetch recent activity
  const fetchRecentActivity = useCallback(async () => {
    try {
      const response = await apiRequest('http://localhost:8000/api/stats/activity');
      if (response && response.ok) {
        const data = await response.json();
        const formattedActivity = data.map((activity, index) => ({
          id: index + 1,
          type: activity.type,
          message: activity.message,
          time: new Date(activity.time).toLocaleString(),
          status: activity.status
        }));
        setRecentActivity(formattedActivity);
      }
    } catch (error) {
      console.error('Error fetching activity:', error);
    }
  }, []);

  // Fetch recent campaigns
  const fetchRecentCampaigns = useCallback(async () => {
    try {
      const response = await apiRequest('http://localhost:8000/api/stats/campaigns');
      if (response && response.ok) {
        const data = await response.json();
        setRecentCampaigns(data.slice(0, 5));
      }
    } catch (error) {
      console.error('Error fetching campaigns:', error);
    }
  }, []);

  // Refresh all data
  const refreshAllData = useCallback(async () => {
    setIsLoading(true);
    await Promise.all([
      fetchTemplates(),
      fetchStats(),
      fetchRecentActivity(),
      fetchRecentCampaigns()
    ]);
    setIsLoading(false);
  }, [fetchTemplates, fetchStats, fetchRecentActivity, fetchRecentCampaigns]);

  // Template operations
  const createTemplate = useCallback(async (templateData) => {
    try {
      const response = await apiRequest('http://localhost:8000/api/templates/', {
        method: 'POST',
        body: JSON.stringify(templateData)
      });

      if (response && response.ok) {
        const newTemplate = await response.json();
        setTemplates([newTemplate, ...templates]);
        return { success: true, template: newTemplate };
      } else if (response) {
        const errorData = await response.json();
        return { success: false, error: errorData.detail };
      }
    } catch (error) {
      return { success: false, error: 'Network error' };
    }
  }, [templates]);

  const deleteTemplate = useCallback(async (templateId) => {
    try {
      const response = await apiRequest(`http://localhost:8000/api/templates/${templateId}`, {
        method: 'DELETE'
      });

      if (response && response.ok) {
        setTemplates(templates.filter(template => template.id !== templateId));
        return { success: true };
      } else {
        return { success: false, error: 'Failed to delete template' };
      }
    } catch (error) {
      return { success: false, error: 'Network error' };
    }
  }, [templates]);

  const setTemplateAsDefault = useCallback(async (template) => {
    try {
      const response = await apiRequest(`http://localhost:8000/api/templates/${template.id}/set-default`, {
        method: 'POST'
      });

      if (response && response.ok) {
        setTemplates(templates.map(t => ({
          ...t,
          is_default: t.id === template.id ? true : false
        })));
        return { success: true };
      } else if (response) {
        const errorData = await response.json();
        return { success: false, error: errorData.detail };
      }
    } catch (error) {
      return { success: false, error: 'Network error' };
    }
  }, [templates]);

  // Initialize data on mount
  useEffect(() => {
    refreshAllData();
  }, [refreshAllData]);

  const value = {
    templates,
    stats,
    recentActivity,
    recentCampaigns,
    isLoading,
    refreshAllData,
    createTemplate,
    deleteTemplate,
    setTemplateAsDefault,
    fetchTemplates,
    fetchStats,
    fetchRecentActivity,
    fetchRecentCampaigns
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
}; 