// Force redeploy: ensure Google OAuth Dashboard logic is up to date
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
    isLoading
  } = useAppContext();

  useEffect(() => {
    // Get user data from localStorage
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []); // Empty dependency array to run only once on mount



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