// Force redeploy: ensure Google OAuth Dashboard logic is up to date
import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
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
    const sessionId = new URLSearchParams(window.location.search).get('session_id');
    
    if (sessionId) {
      // Handle Google OAuth session
      const fetchSession = async () => {
        try {
          const response = await fetch(`/api/v1/google-auth/session?session_id=${sessionId}`);
          
          if (response.ok) {
            const data = await response.json();
            
            // Store authentication data
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('user', JSON.stringify(data.user));
            
            // Clean up URL
            window.history.replaceState({}, document.title, '/dashboard');
            
            // Force re-render
            window.location.reload();
          } else {
            // setError('Failed to complete authentication'); // This line was removed
          }
        } catch (error) {
          // setError('Network error during authentication'); // This line was removed
        }
      };
      
      fetchSession();
    } else {
      // Check if user is already logged in
      const userData = localStorage.getItem('user');
      if (userData) {
        try {
          const user = JSON.parse(userData);
          setUser(user);
        } catch (error) {
          // setError('Error loading user data'); // This line was removed
        }
      }
    }
  }, []);

  // Remove the additional effect since we're using window.location.replace()


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