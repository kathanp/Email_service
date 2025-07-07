import React, { useState, useEffect } from 'react';
import { useAppContext } from '../context/AppContext';
import { API_ENDPOINTS } from '../config';
import './UsageStats.css';
import { Mail, MailCheck, Edit } from 'lucide-react';

function UsageStats() {
  const [usageData, setUsageData] = useState(null);
  const [planData, setPlanData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const { templates } = useAppContext();

  useEffect(() => {
    const fetchUsageData = async () => {
      try {
        const token = localStorage.getItem('token');
        
        // Don't make API calls if no token (user not authenticated)
        if (!token) {
          // Use development endpoints for mock data
          const [subscriptionResponse, usageResponse] = await Promise.all([
            fetch(`${API_ENDPOINTS.SUBSCRIPTIONS}/current/dev`),
            fetch(`${API_ENDPOINTS.SUBSCRIPTIONS}/usage/dev`)
          ]);

          if (subscriptionResponse.ok && usageResponse.ok) {
            const subscription = await subscriptionResponse.json();
            const usage = await usageResponse.json();
            
            setPlanData(subscription);
            setUsageData(usage);
          } else {
            setError('Failed to load development data');
          }
          setIsLoading(false);
          return;
        }
        
        // Fetch current subscription and usage
        const [subscriptionResponse, usageResponse] = await Promise.all([
          fetch(`${API_ENDPOINTS.SUBSCRIPTIONS}/current`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }),
          fetch(`${API_ENDPOINTS.SUBSCRIPTIONS}/usage`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          })
        ]);

        // Check for auth errors
        if (subscriptionResponse.status === 401 || usageResponse.status === 401) {
          setError('Authentication required');
          setIsLoading(false);
          return;
        }

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

    fetchUsageData();
    
    // Listen for subscription changes
    const handleSubscriptionChange = () => {
      fetchUsageData();
    };
    
    window.addEventListener('subscriptionChanged', handleSubscriptionChange);
    
    return () => {
      window.removeEventListener('subscriptionChanged', handleSubscriptionChange);
    };
  }, []); // Empty dependency array to run only once on mount



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

  // Use actual templates count from context instead of API
  const actualTemplatesCount = templates.length;
  const emailPercentage = getUsagePercentage(usageData.emails_sent_this_month, planData.features.email_limit);
  const senderPercentage = getUsagePercentage(usageData.senders_used, planData.features.sender_limit);
  const templatePercentage = getUsagePercentage(actualTemplatesCount, planData.features.template_limit);

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
              <span className="usage-current">{actualTemplatesCount}</span>
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
                  {Math.max(0, planData.features.template_limit - actualTemplatesCount)} remaining
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