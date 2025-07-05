import React, { useState, useEffect } from 'react';
import './UsageStats.css';

function UsageStats() {
  const [usageData, setUsageData] = useState(null);
  const [planData, setPlanData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchUsageData();
  }, []);

  const fetchUsageData = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Fetch current subscription and usage
      const [subscriptionResponse, usageResponse] = await Promise.all([
        fetch('http://localhost:8000/api/subscriptions/current', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }),
        fetch('http://localhost:8000/api/subscriptions/usage', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
      ]);

      if (subscriptionResponse.ok && usageResponse.ok) {
        const subscription = await subscriptionResponse.json();
        const usage = await usageResponse.json();
        
        setPlanData(subscription);
        setUsageData(usage);
      } else {
        setError('Failed to load usage data');
      }
    } catch (err) {
      setError('Network error loading usage data');
    } finally {
      setIsLoading(false);
    }
  };

  const getUsagePercentage = (used, limit) => {
    if (limit === -1) return 0; // Unlimited
    if (limit === 0) return 100;
    return Math.min((used / limit) * 100, 100);
  };

  const getUsageColor = (percentage) => {
    if (percentage >= 90) return '#ef4444'; // Red
    if (percentage >= 75) return '#f59e0b'; // Yellow
    return '#10b981'; // Green
  };

  const formatLimit = (limit) => {
    if (limit === -1) return 'Unlimited';
    return limit.toLocaleString();
  };

  if (isLoading) {
    return (
      <div className="usage-stats">
        <div className="usage-loading">Loading usage data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="usage-stats">
        <div className="usage-error">{error}</div>
      </div>
    );
  }

  if (!planData || !usageData) {
    return (
      <div className="usage-stats">
        <div className="usage-error">No usage data available</div>
      </div>
    );
  }

  const emailPercentage = getUsagePercentage(usageData.emails_sent_this_month, planData.features.email_limit);
  const senderPercentage = getUsagePercentage(usageData.senders_used, planData.features.sender_limit);
  const templatePercentage = getUsagePercentage(usageData.templates_created, planData.features.template_limit);

  return (
    <div className="usage-stats">
      <div className="usage-header">
        <h3>📊 Usage & Limits</h3>
        <div className="plan-badge">
          {planData.plan.charAt(0).toUpperCase() + planData.plan.slice(1)} Plan
        </div>
      </div>
      
      <div className="usage-grid">
        {/* Email Usage */}
        <div className="usage-card">
          <div className="usage-icon">📧</div>
          <div className="usage-content">
            <div className="usage-title">Emails Sent</div>
            <div className="usage-numbers">
              <span className="usage-current">{usageData.emails_sent_this_month.toLocaleString()}</span>
              <span className="usage-separator">/</span>
              <span className="usage-limit">{formatLimit(planData.features.email_limit)}</span>
            </div>
            <div className="usage-bar">
              <div 
                className="usage-progress" 
                style={{
                  width: `${emailPercentage}%`,
                  backgroundColor: getUsageColor(emailPercentage)
                }}
              ></div>
            </div>
            <div className="usage-remaining">
              {planData.features.email_limit !== -1 && (
                <span>
                  {Math.max(0, planData.features.email_limit - usageData.emails_sent_this_month).toLocaleString()} remaining
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Sender Usage */}
        <div className="usage-card">
          <div className="usage-icon">📮</div>
          <div className="usage-content">
            <div className="usage-title">Sender Emails</div>
            <div className="usage-numbers">
              <span className="usage-current">{usageData.senders_used}</span>
              <span className="usage-separator">/</span>
              <span className="usage-limit">{formatLimit(planData.features.sender_limit)}</span>
            </div>
            <div className="usage-bar">
              <div 
                className="usage-progress" 
                style={{
                  width: `${senderPercentage}%`,
                  backgroundColor: getUsageColor(senderPercentage)
                }}
              ></div>
            </div>
            <div className="usage-remaining">
              {planData.features.sender_limit !== -1 && (
                <span>
                  {Math.max(0, planData.features.sender_limit - usageData.senders_used)} remaining
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Template Usage */}
        <div className="usage-card">
          <div className="usage-icon">📝</div>
          <div className="usage-content">
            <div className="usage-title">Email Templates</div>
            <div className="usage-numbers">
              <span className="usage-current">{usageData.templates_created}</span>
              <span className="usage-separator">/</span>
              <span className="usage-limit">{formatLimit(planData.features.template_limit)}</span>
            </div>
            <div className="usage-bar">
              <div 
                className="usage-progress" 
                style={{
                  width: `${templatePercentage}%`,
                  backgroundColor: getUsageColor(templatePercentage)
                }}
              ></div>
            </div>
            <div className="usage-remaining">
              {planData.features.template_limit !== -1 && (
                <span>
                  {Math.max(0, planData.features.template_limit - usageData.templates_created)} remaining
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Plan Features */}
      <div className="plan-features">
        <h4>Plan Features</h4>
        <div className="features-grid">
          <div className={`feature-item ${planData.features.api_access ? 'enabled' : 'disabled'}`}>
            <span className="feature-icon">{planData.features.api_access ? '🔌' : '🔌'}</span>
            <span className="feature-text">API Access</span>
          </div>
          <div className={`feature-item ${planData.features.priority_support ? 'enabled' : 'disabled'}`}>
            <span className="feature-icon">{planData.features.priority_support ? '🎯' : '🎯'}</span>
            <span className="feature-text">Priority Support</span>
          </div>
          <div className={`feature-item ${planData.features.white_label ? 'enabled' : 'disabled'}`}>
            <span className="feature-icon">{planData.features.white_label ? '🏷️' : '🏷️'}</span>
            <span className="feature-text">White Label</span>
          </div>
          <div className={`feature-item ${planData.features.custom_integrations ? 'enabled' : 'disabled'}`}>
            <span className="feature-icon">{planData.features.custom_integrations ? '🔗' : '🔗'}</span>
            <span className="feature-text">Custom Integrations</span>
          </div>
        </div>
      </div>

      {/* Upgrade CTA */}
      {planData.plan === 'free' && (
        <div className="upgrade-cta">
          <p>Need more features? Upgrade your plan to unlock unlimited possibilities!</p>
          <button className="upgrade-button" onClick={() => window.location.href = '/pricing'}>
            View Plans
          </button>
        </div>
      )}
    </div>
  );
}

export default UsageStats; 