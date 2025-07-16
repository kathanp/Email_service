// Force redeploy: ensure Google OAuth Dashboard logic is up to date
import React, { useEffect } from 'react';
import { useAppContext } from '../context/AppContext';
import UsageStats from '../components/UsageStats';
import './Dashboard.css';

function Dashboard() {
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
            JSON.parse(userData);
          } catch (error) {
            // setError('Error loading user data'); // This line was removed
          }
        }
    }
  }, []);

  // Remove the additional effect since we're using window.location.replace()

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