import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_ENDPOINTS } from '../config';
import './Settings.css';

function Settings() {
  const [user, setUser] = useState(null);
  const [subscription, setSubscription] = useState(null);
  const [usage, setUsage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Fetch user info
      const userResponse = await fetch(`${API_ENDPOINTS.AUTH}/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      // Fetch subscription info
      const subscriptionResponse = await fetch(`${API_ENDPOINTS.SUBSCRIPTIONS}/current`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      // Fetch usage stats
      const usageResponse = await fetch(`${API_ENDPOINTS.SUBSCRIPTIONS}/usage`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (userResponse.ok) {
        const userData = await userResponse.json();
        setUser(userData);
      }

      if (subscriptionResponse.ok) {
        const subscriptionData = await subscriptionResponse.json();
        setSubscription(subscriptionData);
      }

      if (usageResponse.ok) {
        const usageData = await usageResponse.json();
        setUsage(usageData);
      }
    } catch (error) {
      setError('Failed to load user data');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const handleUpgrade = () => {
    navigate('/pricing');
  };

  if (loading) {
    return (
      <div className="settings-container">
          <div className="loading">Loading settings...</div>
      </div>
    );
  }

  return (
    <div className="settings-container">
        <div className="settings-header">
        <h1>Account Settings</h1>
        <p>Manage your account and subscription</p>
        </div>

        {error && <div className="error-message">{error}</div>}

      <div className="settings-grid">
        {/* User Information */}
        <div className="settings-card">
          <h2>User Information</h2>
          {user && (
            <div className="user-info">
              <div className="info-row">
                <span className="label">Name:</span>
                <span className="value">{user.full_name}</span>
          </div>
              <div className="info-row">
                <span className="label">Email:</span>
                <span className="value">{user.email}</span>
              </div>
              <div className="info-row">
                <span className="label">Member Since:</span>
                <span className="value">
                  {new Date(user.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Subscription Information */}
        <div className="settings-card">
          <h2>Subscription</h2>
                {subscription ? (
            <div className="subscription-info">
              <div className="info-row">
                <span className="label">Plan:</span>
                <span className="value">{subscription.plan}</span>
              </div>
              <div className="info-row">
                <span className="label">Billing Cycle:</span>
                <span className="value">{subscription.billing_cycle}</span>
                        </div>
              <div className="info-row">
                <span className="label">Status:</span>
                <span className={`value status-${subscription.status.toLowerCase()}`}>
                            {subscription.status}
                          </span>
                        </div>
              <div className="info-row">
                <span className="label">Next Billing:</span>
                <span className="value">
                  {new Date(subscription.current_period_end).toLocaleDateString()}
                </span>
                      </div>
              <button className="btn-secondary" onClick={handleUpgrade}>
                Manage Subscription
              </button>
                  </div>
                ) : (
                  <div className="no-subscription">
              <p>No active subscription</p>
              <button className="btn-primary" onClick={handleUpgrade}>
                Choose a Plan
                    </button>
                  </div>
                )}
              </div>

        {/* Usage Statistics */}
        <div className="settings-card">
          <h2>Usage Statistics</h2>
          {usage ? (
            <div className="usage-info">
              <div className="info-row">
                <span className="label">Emails Sent (This Month):</span>
                <span className="value">{usage.emails_sent_this_month}</span>
                  </div>
              <div className="info-row">
                <span className="label">Emails Sent (Total):</span>
                <span className="value">{usage.emails_sent_total}</span>
                </div>
              <div className="info-row">
                <span className="label">Senders Used:</span>
                <span className="value">{usage.senders_used}</span>
              </div>
              <div className="info-row">
                <span className="label">Templates Created:</span>
                <span className="value">{usage.templates_created}</span>
              </div>
              <div className="info-row">
                <span className="label">Campaigns Created:</span>
                <span className="value">{usage.campaigns_created}</span>
              </div>
            </div>
          ) : (
            <p>No usage data available</p>
          )}
        </div>

        {/* Account Actions */}
        <div className="settings-card">
          <h2>Account Actions</h2>
          <div className="action-buttons">
            <button className="btn-secondary" onClick={() => navigate('/customers')}>
              Manage Campaigns
            </button>
            <button className="btn-secondary" onClick={() => navigate('/email-templates')}>
              Email Templates
            </button>
            <button className="btn-secondary" onClick={() => navigate('/sender-management')}>
              Sender Management
            </button>
            <button className="btn-danger" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Settings; 