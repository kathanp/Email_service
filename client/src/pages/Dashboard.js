import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchStats, fetchRecentActivity } from '../services/statsService';
import UsageStats from '../components/UsageStats';
import './Dashboard.css';

function Dashboard() {
  const [user, setUser] = useState(null);
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
  const navigate = useNavigate();

  useEffect(() => {
    // Get user data from localStorage
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }

    // Fetch real data from API
    const loadDashboardData = async () => {
      try {
        const [statsData, activityData, campaignsData] = await Promise.all([
          fetchStats(),
          fetchRecentActivity(),
          fetchRecentCampaigns()
        ]);

        setStats({
          totalCustomers: statsData.totalCustomers || 0,
          scheduledEmails: statsData.scheduledEmails || 0,
          sentToday: statsData.sentToday || 0,
          totalSent: statsData.totalSent || 0,
          thisWeekSent: statsData.thisWeekSent || 0,
          monthChange: statsData.monthChange || 0,
          todayChange: statsData.todayChange || 0
        });

        // Convert API activity data to dashboard format
        const formattedActivity = activityData.map((activity, index) => ({
          id: index + 1,
          type: activity.type,
          message: activity.message,
          time: new Date(activity.time).toLocaleString(),
          status: activity.status
        }));

        setRecentActivity(formattedActivity);
        setRecentCampaigns(campaignsData);
        setIsLoading(false);
      } catch (error) {
        console.error('Error loading dashboard data:', error);
        // Fallback to default data if API fails
        setStats({
          totalCustomers: 0,
          scheduledEmails: 0,
          sentToday: 0,
          totalSent: 0,
          thisWeekSent: 0,
          monthChange: 0,
          todayChange: 0
        });
        setRecentActivity([]);
        setRecentCampaigns([]);
        setIsLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return '✅';
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      case 'info':
        return 'ℹ️';
      default:
        return '📧';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success':
        return '#10b981';
      case 'error':
        return '#ef4444';
      case 'warning':
        return '#f59e0b';
      case 'info':
        return '#3b82f6';
      default:
        return '#6b7280';
    }
  };

  const getCampaignStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return '✅';
      case 'sending':
        return '📤';
      case 'failed':
        return '❌';
      case 'pending':
        return '⏳';
      default:
        return '📧';
    }
  };

  const getCampaignStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return '#10b981';
      case 'sending':
        return '#3b82f6';
      case 'failed':
        return '#ef4444';
      case 'pending':
        return '#f59e0b';
      default:
        return '#6b7280';
    }
  };

  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const fetchRecentCampaigns = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/stats/campaigns', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        return data.slice(0, 5); // Get last 5 campaigns
      } else {
        return [];
      }
    } catch (error) {
      console.error('Error fetching recent campaigns:', error);
      return [];
    }
  };

  if (isLoading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Welcome Section */}
      <div className="welcome-section">
        <div className="welcome-content">
          <h1>Welcome back, {user?.name || 'User'}! 👋</h1>
          <p>Here's what's happening with your email campaigns today.</p>
        </div>
        <div className="welcome-actions">
          <button 
            className="action-button primary"
            onClick={() => navigate('/customers')}
          >
            📧 Start New Campaign
          </button>
          <button 
            className="action-button secondary"
            onClick={() => navigate('/templates')}
          >
            📝 Create Template
          </button>
        </div>
      </div>

      {/* Usage Stats Section */}
      <UsageStats />

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <h3>{stats.totalCustomers.toLocaleString()}</h3>
            <p>Total Customers</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">📅</div>
          <div className="stat-content">
            <h3>{stats.scheduledEmails.toLocaleString()}</h3>
            <p>Scheduled Emails</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">📤</div>
          <div className="stat-content">
            <h3>{stats.sentToday.toLocaleString()}</h3>
            <p>Sent Today</p>
            <span className={`stat-change ${stats.todayChange >= 0 ? 'positive' : 'negative'}`}>
              {stats.todayChange >= 0 ? '+' : ''}{stats.todayChange}%
            </span>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <h3>{stats.totalSent.toLocaleString()}</h3>
            <p>Total Sent</p>
            <span className={`stat-change ${stats.monthChange >= 0 ? 'positive' : 'negative'}`}>
              {stats.monthChange >= 0 ? '+' : ''}{stats.monthChange}%
            </span>
          </div>
        </div>
      </div>

      {/* Dashboard Content Grid */}
      <div className="dashboard-content">
        {/* Recent Activity Section */}
        <div className="activity-section">
          <div className="section-header">
            <h3>📊 Recent Activity</h3>
            <button className="view-all-btn" onClick={() => navigate('/reports')}>
              View All
            </button>
          </div>
          <div className="activity-list">
            {recentActivity.length === 0 ? (
              <div className="no-activity">
                <div className="empty-state">
                  <span className="empty-icon">📊</span>
                  <p>No recent activity</p>
                  <small>Your activity will appear here</small>
                </div>
              </div>
            ) : (
              recentActivity.map((activity) => (
                <div key={activity.id} className="activity-item">
                  <div className="activity-icon" style={{ color: getStatusColor(activity.status) }}>
                    {getStatusIcon(activity.status)}
                  </div>
                  <div className="activity-content">
                    <p className="activity-message">{activity.message}</p>
                    <span className="activity-time">{activity.time}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Recent Campaigns Section */}
        <div className="campaigns-section">
          <div className="section-header">
            <h3>📧 Recent Campaigns</h3>
            <button className="view-all-btn" onClick={() => navigate('/customers')}>
              View All
            </button>
          </div>
          <div className="campaigns-list">
            {recentCampaigns.length === 0 ? (
              <div className="no-campaigns">
                <div className="empty-state">
                  <span className="empty-icon">📧</span>
                  <p>No recent campaigns</p>
                  <small>Start your first campaign to see results here</small>
                </div>
              </div>
            ) : (
              recentCampaigns.map((campaign) => (
                <div key={campaign.id} className="campaign-item">
                  <div className="campaign-header">
                    <h4>{campaign.name}</h4>
                    <span 
                      className="campaign-status"
                      style={{ color: getCampaignStatusColor(campaign.status) }}
                    >
                      {getCampaignStatusIcon(campaign.status)} {campaign.status}
                    </span>
                  </div>
                  <div className="campaign-details">
                    <div className="campaign-stat">
                      <span className="stat-label">Recipients:</span>
                      <span className="stat-value">{campaign.recipients_count || 0}</span>
                    </div>
                    <div className="campaign-stat">
                      <span className="stat-label">Sent:</span>
                      <span className="stat-value success">{campaign.sent_count || 0}</span>
                    </div>
                    <div className="campaign-stat">
                      <span className="stat-label">Failed:</span>
                      <span className="stat-value error">{campaign.failed_count || 0}</span>
                    </div>
                    {campaign.duration && (
                      <div className="campaign-stat">
                        <span className="stat-label">Duration:</span>
                        <span className="stat-value">{formatDuration(campaign.duration)}</span>
                      </div>
                    )}
                    <div className="campaign-stat">
                      <span className="stat-label">Created:</span>
                      <span className="stat-value">{new Date(campaign.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Quick Actions Section */}
        <div className="quick-actions-section">
          <div className="section-header">
            <h3>⚡ Quick Actions</h3>
          </div>
          <div className="quick-actions-grid">
            <button 
              className="quick-action-card"
              onClick={() => navigate('/customers')}
            >
              <div className="action-icon">📧</div>
              <h4>New Campaign</h4>
              <p>Create and send a new email campaign</p>
            </button>
            
            <button 
              className="quick-action-card"
              onClick={() => navigate('/files')}
            >
              <div className="action-icon">📁</div>
              <h4>Upload Contacts</h4>
              <p>Upload customer contact files</p>
            </button>
            
            <button 
              className="quick-action-card"
              onClick={() => navigate('/email-templates')}
            >
              <div className="action-icon">📝</div>
              <h4>Create Template</h4>
              <p>Design a new email template</p>
            </button>
            
            <button 
              className="quick-action-card"
              onClick={() => navigate('/sender-management')}
            >
              <div className="action-icon">📮</div>
              <h4>Manage Senders</h4>
              <p>Add or verify sender emails</p>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard; 