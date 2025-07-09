import React, { useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../config';
import './UsageStats.css';
import { Mail, MailCheck, Edit } from 'lucide-react';

function UsageStats() {
  const [usageData, setUsageData] = useState({
    emails_sent_this_month: 0,
    senders_used: 0,
    templates_used: 0
  });
  const [planData, setPlanData] = useState({
    plan: 'free',
    features: {
      email_limit: 100,
      sender_limit: 1,
      template_limit: 3
    }
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchUsageData();
  }, []);

  const fetchUsageData = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('No authentication token found');
        setLoading(false);
        return;
      }

      // Fetch current subscription
      const subscriptionResponse = await fetch(`${API_ENDPOINTS.SUBSCRIPTIONS_V1}/current`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      // Fetch usage stats
      const usageResponse = await fetch(`${API_ENDPOINTS.SUBSCRIPTIONS_V1}/usage`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (subscriptionResponse.ok) {
        const subscriptionData = await subscriptionResponse.json();
        setPlanData({
          plan: subscriptionData.plan || 'free',
          features: subscriptionData.features || {
            email_limit: 100,
            sender_limit: 1,
            template_limit: 3
          }
        });
      }

      if (usageResponse.ok) {
        const usageResponseData = await usageResponse.json();
        setUsageData({
          emails_sent_this_month: usageResponseData.emails_sent_this_month || 0,
          senders_used: usageResponseData.senders_used || 0,
          templates_used: usageResponseData.templates_created || 0
        });
      }
    } catch (error) {
      setError('Failed to load usage data');
    } finally {
      setLoading(false);
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

  const emailPercentage = getUsagePercentage(usageData.emails_sent_this_month, planData.features.email_limit);
  const senderPercentage = getUsagePercentage(usageData.senders_used, planData.features.sender_limit);
  const templatePercentage = getUsagePercentage(usageData.templates_used, planData.features.template_limit);

  if (loading) {
    return (
      <div className="usage-stats">
        <div className="usage-header">
          <h3>📊 Usage & Limits</h3>
          <div className="plan-badge">Loading...</div>
        </div>
        <div className="usage-loading">Loading usage data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="usage-stats">
        <div className="usage-header">
          <h3>�� Usage & Limits</h3>
          <div className="plan-badge">Error</div>
        </div>
        <div className="usage-error">{error}</div>
      </div>
    );
  }

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
          <div className="usage-icon"><Mail size={24} /></div>
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
          <div className="usage-icon"><MailCheck size={24} /></div>
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
          <div className="usage-icon"><Edit size={24} /></div>
          <div className="usage-content">
            <div className="usage-title">Email Templates</div>
            <div className="usage-numbers">
              <span className="usage-current">{usageData.templates_used}</span>
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
                  {Math.max(0, planData.features.template_limit - usageData.templates_used)} remaining
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default UsageStats; 