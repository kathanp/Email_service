import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_ENDPOINTS } from '../config';
import './Settings.css';

function Settings() {
  const [user, setUser] = useState(null);
  const [subscription, setSubscription] = useState(null);
  const [usage, setUsage] = useState(null);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
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

      // Fetch payment methods
      const paymentMethodsResponse = await fetch(`${API_ENDPOINTS.SUBSCRIPTIONS_V1}/payment-methods`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      // Fetch default payment method
      const defaultPaymentMethodResponse = await fetch(`${API_ENDPOINTS.SUBSCRIPTIONS_V1}/payment-methods/default`, {
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

      if (paymentMethodsResponse.ok) {
        const paymentMethodsData = await paymentMethodsResponse.json();
        setPaymentMethods(paymentMethodsData.payment_methods || []);
      }

      if (defaultPaymentMethodResponse.ok) {
        await defaultPaymentMethodResponse.json();
        // Default payment method data retrieved but not currently used
      }
    } catch (error) {
      setError('Failed to load user data');
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = () => {
    navigate('/pricing');
  };

  const handleSetDefaultPaymentMethod = async (paymentMethodId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.SUBSCRIPTIONS_V1}/payment-methods/${paymentMethodId}/set-default`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        // Refresh payment methods data
        fetchUserData();
      } else {
        setError('Failed to update default payment method');
      }
    } catch (error) {
      setError('Failed to update default payment method');
    }
  };

  const deletePaymentMethod = async (paymentMethodId) => {
    if (!window.confirm('Are you sure you want to remove this payment method?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.SUBSCRIPTIONS_V1}/payment-methods/${paymentMethodId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        // Refresh payment methods data
        fetchUserData();
      } else {
        setError('Failed to remove payment method');
      }
    } catch (error) {
      setError('Failed to remove payment method');
    }
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
        {error && <div className="error-message">{error}</div>}

      <div className="settings-grid">
        {/* User Information */}
        <div className="settings-card">
          <h2>User Information</h2>
          {user && (
            <div className="user-info-layered">
              <div className="info-layer">
                <div className="info-label">Name:</div>
                <div className="info-value">{user.full_name}</div>
              </div>
              
              <div className="info-layer">
                <div className="info-label">Email:</div>
                <div className="info-value">{user.email}</div>
              </div>
              
              <div className="info-layer">
                <div className="info-label">Member Since:</div>
                <div className="info-value">
                  {new Date(user.created_at).toLocaleDateString()}
                </div>
              </div>
              
              <div className="info-layer">
                <div className="info-label">Password:</div>
                <div className="info-value password-field">
                  <span className="password-display">
                    {showPassword ? 'mypassword123' : '••••••••••••'}
                  </span>
                  <button 
                    className="password-toggle"
                    onClick={() => setShowPassword(!showPassword)}
                    type="button"
                    title={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? (
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                        <line x1="1" y1="1" x2="23" y2="23"/>
                      </svg>
                    ) : (
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                        <circle cx="12" cy="12" r="3"/>
                      </svg>
                    )}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Subscription Information */}
        <div className="settings-card">
          <h2>Subscription Details</h2>
                {subscription ? (
            <div className="subscription-info">
              <div className="info-row">
                <span className="label">Current Plan:</span>
                <span className="value plan-name">{subscription.plan_id ? subscription.plan_id.charAt(0).toUpperCase() + subscription.plan_id.slice(1) : 'Free'}</span>
              </div>
              <div className="info-row">
                <span className="label">Billing Cycle:</span>
                <span className="value">{subscription.billing_cycle ? subscription.billing_cycle.charAt(0).toUpperCase() + subscription.billing_cycle.slice(1) : 'N/A'}</span>
                        </div>
              <div className="info-row">
                <span className="label">Status:</span>
                <span className={`value status-${subscription.status ? subscription.status.toLowerCase() : 'unknown'}`}>
                            {subscription.status ? subscription.status.charAt(0).toUpperCase() + subscription.status.slice(1) : 'Unknown'}
                          </span>
                        </div>
              {subscription.current_period_start && (
                <div className="info-row">
                  <span className="label">Billing Period Start:</span>
                  <span className="value">
                    {new Date(subscription.current_period_start).toLocaleDateString()}
                  </span>
                </div>
              )}
              {subscription.current_period_end && (
                <div className="info-row">
                  <span className="label">Next Billing Date:</span>
                  <span className="value">
                    {new Date(subscription.current_period_end).toLocaleDateString()}
                  </span>
                </div>
              )}
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

        {/* Payment Methods */}
        <div className="settings-card">
          <h2>Payment Methods</h2>
          {paymentMethods.length > 0 ? (
            <div className="payment-methods-info">
              {paymentMethods.map((method) => (
                <div key={method.id} className={`payment-method-item ${method.is_default ? 'default' : ''}`}>
                  <div className="payment-method-details">
                    <div className="card-info">
                      <span className="card-brand">{method.brand ? method.brand.toUpperCase() : 'CARD'}</span>
                      <span className="card-number">•••• •••• •••• {method.last4}</span>
                    </div>
                    <div className="card-expiry">
                      Expires {method.exp_month}/{method.exp_year}
                    </div>
                    {method.is_default && (
                      <span className="default-badge">Default</span>
                    )}
                  </div>
                  <div className="payment-method-actions">
                    {!method.is_default && (
                      <button 
                        className="btn-small btn-secondary"
                        onClick={() => handleSetDefaultPaymentMethod(method.id)}
                      >
                        Set as Default
                      </button>
                    )}
                    <button 
                      className="btn-small btn-danger"
                      onClick={() => deletePaymentMethod(method.id)}
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}
              <button className="btn-secondary add-payment-method" onClick={() => navigate('/pricing')}>
                Add Payment Method
              </button>
            </div>
          ) : (
            <div className="no-payment-methods">
              <p>No payment methods on file</p>
              <button className="btn-primary" onClick={() => navigate('/pricing')}>
                Add Payment Method
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
                <span className="label">Emails Sent (Current Billing Period):</span>
                <span className="value">{usage.emails_sent_this_billing_period || usage.emails_sent_this_month}</span>
                  </div>
              {usage.billing_period_start && usage.billing_period_end && (
                <div className="info-row billing-period">
                  <span className="label">Billing Period:</span>
                  <span className="value">
                    {new Date(usage.billing_period_start).toLocaleDateString()} - {new Date(usage.billing_period_end).toLocaleDateString()}
                  </span>
                </div>
              )}
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


      </div>
    </div>
  );
}

export default Settings; 