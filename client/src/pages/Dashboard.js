// Force redeploy: ensure Google OAuth Dashboard logic is up to date
import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';
import UsageStats from '../components/UsageStats';
import './Dashboard.css';

function Dashboard() {
  const [user, setUser] = useState(null);
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { 
    stats, 
    isLoading
  } = useAppContext();

  useEffect(() => {
    // Check for Google OAuth session in URL parameters
    const sessionId = searchParams.get('session');
    
    console.log('Dashboard useEffect - sessionId:', sessionId);
    console.log('Current URL:', window.location.href);
    
    if (sessionId) {
      console.log('Google OAuth session received, fetching authentication data...');
      
      // Fetch session data from backend
      fetch(`/api/auth/session/${sessionId}`)
        .then(response => {
          console.log('Session response status:', response.status);
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          console.log('Session data received:', data);
          
          // Store the token
          localStorage.setItem('token', data.access_token);
          console.log('Token stored:', data.access_token);
          
          // Store user data
          localStorage.setItem('user', JSON.stringify(data.user));
          console.log('User data stored:', data.user);
          
          setUser(data.user);
          
          // Force URL cleanup immediately
          console.log('Forcing URL cleanup...');
          window.location.replace('/dashboard');
          
          console.log('Authentication data stored, user logged in');
        })
        .catch(error => {
          console.error('Error fetching session:', error);
          // If session fetch fails, try to redirect to login
          alert('Google login failed. Please try again.');
          window.location.href = '/';
        });
    } else {
      // Get user data from localStorage (normal login)
      const userData = localStorage.getItem('user');
      console.log('No session, checking localStorage for user data:', userData);
      if (userData) {
        setUser(JSON.parse(userData));
      }
    }
  }, [searchParams]); // Include searchParams in dependency array

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