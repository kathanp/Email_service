import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navigation from '../components/Navigation';
import { fetchStats, fetchRecentActivity } from '../services/statsService';
import './Dashboard.css';

function Dashboard() {
  const [user, setUser] = useState(null);
  const [stats, setStats] = useState({
    totalCustomers: 0,
    scheduledEmails: 0,
    sentToday: 0,
    totalSent: 0,
    thisWeekSent: 0
  });
  const [recentActivity, setRecentActivity] = useState([]);
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
        const [statsData, activityData] = await Promise.all([
          fetchStats(),
          fetchRecentActivity()
        ]);

        setStats({
          totalCustomers: statsData.totalCustomers || 0,
          scheduledEmails: statsData.scheduledEmails || 0,
          sentToday: statsData.sentToday || 0,
          totalSent: statsData.totalSent || 0,
          thisWeekSent: statsData.thisWeekSent || 0
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
        setIsLoading(false);
      } catch (error) {
        console.error('Error loading dashboard data:', error);
        // Fallback to default data if API fails
        setStats({
          totalCustomers: 0,
          scheduledEmails: 0,
          sentToday: 0,
          totalSent: 0,
          thisWeekSent: 0
        });
        setRecentActivity([]);
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

  if (isLoading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-wrapper">
      <Navigation />
      <div className="dashboard-container">
        {/* Statistics Cards */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon customers">👥</div>
            <div className="stat-content">
              <h3>Total Customers</h3>
              <p className="stat-number">{stats.totalCustomers}</p>
              <span className="stat-change positive">+12% from last month</span>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon scheduled">⏰</div>
            <div className="stat-content">
              <h3>Scheduled Emails</h3>
              <p className="stat-number">{stats.scheduledEmails}</p>
              <span className="stat-change neutral">Next: Today 9:00 AM</span>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon sent">📤</div>
            <div className="stat-content">
              <h3>Sent Today</h3>
              <p className="stat-number">{stats.sentToday}</p>
              <span className="stat-change positive">+8 from yesterday</span>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon total">📈</div>
            <div className="stat-content">
              <h3>Total Sent</h3>
              <p className="stat-number">{stats.totalSent}</p>
              <span className="stat-change positive">+{stats.thisWeekSent} this week</span>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="dashboard-grid">
          {/* Recent Activity */}
          <div className="dashboard-card activity-card">
            <div className="card-header">
              <h3>Recent Activity</h3>
              <button className="view-all-btn">View All</button>
            </div>
            <div className="activity-list">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="activity-item">
                  <div 
                    className="activity-icon"
                    style={{ backgroundColor: getStatusColor(activity.status) }}
                  >
                    {getStatusIcon(activity.status)}
                  </div>
                  <div className="activity-content">
                    <p className="activity-message">{activity.message}</p>
                    <span className="activity-time">{activity.time}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Email Performance */}
          <div className="dashboard-card performance-card">
            <div className="card-header">
              <h3>Email Performance</h3>
              <span className="period-selector">Last 7 days</span>
            </div>
            <div className="performance-stats">
              <div className="performance-item">
                <span className="performance-label">Open Rate</span>
                <span className="performance-value">68.5%</span>
              </div>
              <div className="performance-item">
                <span className="performance-label">Click Rate</span>
                <span className="performance-value">12.3%</span>
              </div>
              <div className="performance-item">
                <span className="performance-label">Bounce Rate</span>
                <span className="performance-value">2.1%</span>
              </div>
              <div className="performance-item">
                <span className="performance-label">Response Rate</span>
                <span className="performance-value">8.7%</span>
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="dashboard-card quick-stats-card">
            <div className="card-header">
              <h3>Quick Stats</h3>
            </div>
            <div className="quick-stats-grid">
              <div className="quick-stat">
                <span className="quick-stat-number">23</span>
                <span className="quick-stat-label">Active Campaigns</span>
              </div>
              <div className="quick-stat">
                <span className="quick-stat-number">89%</span>
                <span className="quick-stat-label">Delivery Rate</span>
              </div>
              <div className="quick-stat">
                <span className="quick-stat-number">156</span>
                <span className="quick-stat-label">New Contacts</span>
              </div>
              <div className="quick-stat">
                <span className="quick-stat-number">$2.4k</span>
                <span className="quick-stat-label">Revenue Generated</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard; 