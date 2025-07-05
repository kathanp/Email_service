import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Settings.css';

function Settings() {
  const [user, setUser] = useState(null);
  const [subscription, setSubscription] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState(null);
  const [usage, setUsage] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('account');
  const navigate = useNavigate();

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Fetch all user data in parallel
      const [userResponse, subscriptionResponse, usageResponse] = await Promise.all([
        fetch('http://localhost:8000/api/auth/me', {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch('http://localhost:8000/api/v1/subscriptions/current', {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch('http://localhost:8000/api/v1/subscriptions/usage', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

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

      // Fetch payment method if user has a subscription
      if (subscriptionResponse.ok) {
        const subscriptionData = await subscriptionResponse.json();
        if (subscriptionData.stripe_subscription_id) {
          const paymentResponse = await fetch('http://localhost:8000/api/v1/subscriptions/payment-method', {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          if (paymentResponse.ok) {
            const paymentData = await paymentResponse.json();
            setPaymentMethod(paymentData);
          }
        }
      }

    } catch (err) {
      setError('Failed to load user data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getPlanName = (plan) => {
    const planNames = {
      'free': 'Free',
      'starter': 'Starter',
      'professional': 'Professional',
      'enterprise': 'Enterprise'
    };
    return planNames[plan] || plan;
  };

  const getCardBrandIcon = (brand) => {
    const icons = {
      'visa': '💳',
      'mastercard': '💳',
      'amex': '💳',
      'discover': '💳',
      'default': '💳'
    };
    return icons[brand?.toLowerCase()] || icons.default;
  };

  if (isLoading) {
    return (
      <div className="settings-wrapper">
        <div className="settings">
          <div className="loading">Loading settings...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="settings-wrapper">
      <div className="settings">
        <div className="settings-header">
          <h1>Settings</h1>
          <p>Manage your account, subscription, and payment information</p>
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="settings-content">
          {/* Navigation Tabs */}
          <div className="settings-tabs">
            <button 
              className={`tab ${activeTab === 'account' ? 'active' : ''}`}
              onClick={() => setActiveTab('account')}
            >
              👤 Account
            </button>
            <button 
              className={`tab ${activeTab === 'subscription' ? 'active' : ''}`}
              onClick={() => setActiveTab('subscription')}
            >
              📦 Subscription
            </button>
            <button 
              className={`tab ${activeTab === 'payment' ? 'active' : ''}`}
              onClick={() => setActiveTab('payment')}
            >
              💳 Payment
            </button>
            <button 
              className={`tab ${activeTab === 'usage' ? 'active' : ''}`}
              onClick={() => setActiveTab('usage')}
            >
              📊 Usage
            </button>
          </div>

          {/* Account Tab */}
          {activeTab === 'account' && (
            <div className="tab-content">
              <div className="section">
                <h3>Account Information</h3>
                <div className="info-grid">
                  <div className="info-item">
                    <label>Name</label>
                    <span>{user?.full_name || 'Not set'}</span>
                  </div>
                  <div className="info-item">
                    <label>Email</label>
                    <span>{user?.email || 'Not set'}</span>
                  </div>
                  <div className="info-item">
                    <label>Account Created</label>
                    <span>{user?.created_at ? formatDate(user.created_at) : 'Unknown'}</span>
                  </div>
                  <div className="info-item">
                    <label>Last Login</label>
                    <span>{user?.last_login ? formatDate(user.last_login) : 'Unknown'}</span>
                  </div>
                </div>
              </div>

              <div className="section">
                <h3>Account Actions</h3>
                <div className="action-buttons">
                  <button className="btn-secondary">Edit Profile</button>
                  <button className="btn-secondary">Change Password</button>
                  <button className="btn-danger" onClick={handleLogout}>Logout</button>
                </div>
              </div>
            </div>
          )}

          {/* Subscription Tab */}
          {activeTab === 'subscription' && (
            <div className="tab-content">
              <div className="section">
                <h3>Current Subscription</h3>
                {subscription ? (
                  <div className="subscription-details">
                    <div className="subscription-card">
                      <div className="plan-info">
                        <h4>{getPlanName(subscription.plan)} Plan</h4>
                        <div className="plan-price">
                          ${subscription.features.email_limit === 100 ? '0' : 
                             subscription.features.email_limit === 1000 ? '4.99' :
                             subscription.features.email_limit === 10000 ? '14.99' : '25.99'}/month
                        </div>
                        <div className="plan-status">
                          <span className={`status-badge ${subscription.status}`}>
                            {subscription.status}
                          </span>
                        </div>
                      </div>
                      
                      <div className="billing-info">
                        <div className="billing-item">
                          <label>Billing Cycle:</label>
                          <span>{subscription.billing_cycle}</span>
                        </div>
                        <div className="billing-item">
                          <label>Next Billing:</label>
                          <span>{formatDate(subscription.current_period_end)}</span>
                        </div>
                        {subscription.cancel_at_period_end && (
                          <div className="billing-item warning">
                            <label>⚠️ Cancellation:</label>
                            <span>Plan will cancel at period end</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="no-subscription">
                    <p>No active subscription found.</p>
                    <button className="btn-primary" onClick={() => navigate('/pricing')}>
                      View Plans
                    </button>
                  </div>
                )}
              </div>

              {subscription && (
                <div className="section">
                  <h3>Subscription Actions</h3>
                  <div className="action-buttons">
                    <button className="btn-primary" onClick={() => navigate('/pricing')}>
                      Upgrade Plan
                    </button>
                    {!subscription.cancel_at_period_end && (
                      <button className="btn-secondary">Cancel Subscription</button>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Payment Tab */}
          {activeTab === 'payment' && (
            <div className="tab-content">
              <div className="section">
                <h3>Payment Method</h3>
                {paymentMethod ? (
                  <div className="payment-card">
                    <div className="card-info">
                      <div className="card-icon">
                        {getCardBrandIcon(paymentMethod.card?.brand)}
                      </div>
                      <div className="card-details">
                        <div className="card-number">
                          •••• •••• •••• {paymentMethod.card?.last4}
                        </div>
                        <div className="card-meta">
                          {paymentMethod.card?.brand?.toUpperCase()} • Expires {paymentMethod.card?.exp_month}/{paymentMethod.card?.exp_year}
                        </div>
                      </div>
                    </div>
                    <div className="card-actions">
                      <button className="btn-secondary">Update Card</button>
                      <button className="btn-danger">Remove Card</button>
                    </div>
                  </div>
                ) : (
                  <div className="no-payment">
                    <p>No payment method on file.</p>
                    <button className="btn-primary" onClick={() => navigate('/pricing')}>
                      Add Payment Method
                    </button>
                  </div>
                )}
              </div>

              {subscription && (
                <div className="section">
                  <h3>Billing History</h3>
                  <div className="billing-history">
                    <div className="history-item">
                      <div className="history-date">{formatDate(subscription.current_period_start)}</div>
                      <div className="history-amount">
                        ${subscription.features.email_limit === 100 ? '0.00' : 
                           subscription.features.email_limit === 1000 ? '4.99' :
                           subscription.features.email_limit === 10000 ? '14.99' : '25.99'}
                      </div>
                      <div className="history-status">Paid</div>
                    </div>
                    <p className="history-note">Billing history will appear here as payments are processed.</p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Usage Tab */}
          {activeTab === 'usage' && (
            <div className="tab-content">
              <div className="section">
                <h3>Current Usage</h3>
                {usage && subscription ? (
                  <div className="usage-overview">
                    <div className="usage-item">
                      <div className="usage-label">Emails Sent This Month</div>
                      <div className="usage-value">
                        {usage.emails_sent_this_month.toLocaleString()} / {subscription.features.email_limit === -1 ? 'Unlimited' : subscription.features.email_limit.toLocaleString()}
                      </div>
                      <div className="usage-bar">
                        <div 
                          className="usage-progress" 
                          style={{
                            width: `${subscription.features.email_limit === -1 ? 0 : (usage.emails_sent_this_month / subscription.features.email_limit) * 100}%`
                          }}
                        ></div>
                      </div>
                    </div>

                    <div className="usage-item">
                      <div className="usage-label">Sender Emails</div>
                      <div className="usage-value">
                        {usage.senders_used} / {subscription.features.sender_limit === -1 ? 'Unlimited' : subscription.features.sender_limit}
                      </div>
                      <div className="usage-bar">
                        <div 
                          className="usage-progress" 
                          style={{
                            width: `${subscription.features.sender_limit === -1 ? 0 : (usage.senders_used / subscription.features.sender_limit) * 100}%`
                          }}
                        ></div>
                      </div>
                    </div>

                    <div className="usage-item">
                      <div className="usage-label">Email Templates</div>
                      <div className="usage-value">
                        {usage.templates_created} / {subscription.features.template_limit === -1 ? 'Unlimited' : subscription.features.template_limit}
                      </div>
                      <div className="usage-bar">
                        <div 
                          className="usage-progress" 
                          style={{
                            width: `${subscription.features.template_limit === -1 ? 0 : (usage.templates_created / subscription.features.template_limit) * 100}%`
                          }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="no-usage">
                    <p>No usage data available.</p>
                  </div>
                )}
              </div>

              <div className="section">
                <h3>Usage Actions</h3>
                <div className="action-buttons">
                  <button className="btn-primary" onClick={() => navigate('/customers')}>
                    Send More Emails
                  </button>
                  <button className="btn-secondary" onClick={() => navigate('/templates')}>
                    Create Templates
                  </button>
                  <button className="btn-secondary" onClick={() => navigate('/senders')}>
                    Manage Senders
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Settings; 