import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';
import UsageStats from '../components/UsageStats';
import './Dashboard.css';

function Dashboard() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();
  const { 
    stats, 
    recentActivity, 
    recentCampaigns, 
    isLoading,
    refreshAllData 
  } = useAppContext();

  useEffect(() => {
    // Get user data from localStorage
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }

    // Refresh data when component mounts
    refreshAllData();
  }, [refreshAllData]);

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

  // Helper function to get user's display name
  const getUserDisplayName = () => {
    if (!user) return 'User';
    
    // Check for full_name first (from Google OAuth)
    if (user.full_name) return user.full_name;
    
    // Check for name field
    if (user.name) return user.name;
    
    // Check for first name from email (fallback)
    if (user.email) {
      const emailName = user.email.split('@')[0];
      // Capitalize first letter and replace dots/underscores with spaces
      return emailName
        .replace(/[._]/g, ' ')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    }
    
    return 'User';
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
          <h1>Welcome back, {getUserDisplayName()}! 👋</h1>
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


    </div>
  );
}

export default Dashboard; 