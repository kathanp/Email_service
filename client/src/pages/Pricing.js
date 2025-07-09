import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_ENDPOINTS } from '../config';
import './Pricing.css';

function Pricing() {
  const [plans, setPlans] = useState([]);
  const [currentSubscription, setCurrentSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [billingCycle, setBillingCycle] = useState('monthly');
  const navigate = useNavigate();

  useEffect(() => {
    fetchPlans();
    fetchCurrentSubscription();
    
    // Check for success parameter in URL (from payment success)
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('success') === 'true') {
      setSuccess('Payment successful! Your subscription has been upgraded.');
      // Clear the URL parameter
      window.history.replaceState({}, document.title, window.location.pathname);
      // Refresh current subscription data
      fetchCurrentSubscription();
    }
  }, []);

  // Add a listener for when user returns from payment
  useEffect(() => {
    const handleFocus = () => {
      // Refresh current subscription when user returns to the page
      fetchCurrentSubscription();
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, []);

  const fetchPlans = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.SUBSCRIPTIONS_V1}/plans`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setPlans(data || []); // The v1 endpoint returns the array directly
      } else {
        setError('Failed to load subscription plans');
      }
    } catch (error) {
      setError('Network error loading plans');
    }
  };

  const fetchCurrentSubscription = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.SUBSCRIPTIONS_V1}/current`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setCurrentSubscription(data);
      } else {
        setError('Failed to fetch subscription data');
      }
    } catch (error) {
      setError('Failed to fetch subscription data');
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (plan) => {
    setError('');
    
    // Redirect to payment page instead of creating subscription immediately
    navigate('/pricing/subscribe', { 
      state: { 
        plan: plan,
        billingCycle: billingCycle
      }
    });
  };

  const isCurrentPlan = (plan) => {
    return currentSubscription && currentSubscription.plan === plan.id;
  };

  if (loading) {
    return (
      <div className="pricing-container">
        <div className="loading">Loading plans...</div>
      </div>
    );
  }

  return (
    <div className="pricing-container">
      <div className="pricing-header">
        <h1>Choose Your Plan</h1>
        <p>Select the perfect plan for your email marketing needs</p>
        <button 
          onClick={fetchCurrentSubscription}
          style={{
            background: '#667eea',
            color: 'white',
            border: 'none',
            padding: '8px 16px',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          Refresh Plan Status
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <div className="billing-toggle">
        <span className={billingCycle === 'monthly' ? 'active' : ''}>Monthly</span>
        <label className="switch">
          <input
            type="checkbox"
            checked={billingCycle === 'yearly'}
            onChange={(e) => setBillingCycle(e.target.checked ? 'yearly' : 'monthly')}
          />
          <span className="slider"></span>
        </label>
        <span className={billingCycle === 'yearly' ? 'active' : ''}>Yearly</span>
        {billingCycle === 'yearly' && <span className="save-badge">Save 20%</span>}
      </div>

      <div className="plans-grid">
        {Array.isArray(plans) && plans.map((plan) => (
          plan && (
            <div 
              key={plan.id} 
              className={`plan-card ${isCurrentPlan(plan) ? 'current' : ''}`}
            >
              {isCurrentPlan(plan) && (
                <div className="current-badge">Current Plan</div>
              )}
              
              <div className="plan-header">
                <h3>{plan.name || 'Unnamed Plan'}</h3>
                <div className="price">
                  <span className="currency">$</span>
                  <span className="amount">
                    {billingCycle === 'monthly' ? (plan.price_monthly || 0) : (plan.price_yearly || 0)}
                  </span>
                  <span className="period">/{billingCycle === 'monthly' ? 'mo' : 'year'}</span>
                </div>
              </div>

              <div className="plan-features">
                <div className="feature">
                  <span className="feature-icon">📧</span>
                  <span className="feature-text">
                    {plan.features.email_limit === -1 ? 'Unlimited' : plan.features.email_limit.toLocaleString()} emails/month
                  </span>
                </div>
                <div className="feature">
                  <span className="feature-icon">📮</span>
                  <span className="feature-text">
                    {plan.features.sender_limit === -1 ? 'Unlimited' : plan.features.sender_limit} sender emails
                  </span>
                </div>
                <div className="feature">
                  <span className="feature-icon">📝</span>
                  <span className="feature-text">
                    {plan.features.template_limit === -1 ? 'Unlimited' : plan.features.template_limit} email templates
                  </span>
                </div>
                {plan.features.api_access && (
                  <div className="feature">
                    <span className="feature-icon">🔌</span>
                    <span className="feature-text">API Access</span>
                  </div>
                )}
                {plan.features.priority_support && (
                  <div className="feature">
                    <span className="feature-icon">🎯</span>
                    <span className="feature-text">Priority Support</span>
                  </div>
                )}
                {plan.features.white_label && (
                  <div className="feature">
                    <span className="feature-icon">🏷️</span>
                    <span className="feature-text">White Label</span>
                  </div>
                )}
                {plan.features.custom_integrations && (
                  <div className="feature">
                    <span className="feature-icon">🔗</span>
                    <span className="feature-text">Custom Integrations</span>
                  </div>
                )}
              </div>

              <button
                className={`plan-button ${isCurrentPlan(plan) ? 'current' : ''}`}
                onClick={() => handleSubscribe(plan)}
                disabled={isCurrentPlan(plan)}
              >
                {isCurrentPlan(plan) ? 'Current Plan' : 'Choose Plan'}
              </button>
            </div>
          )
        ))}
      </div>

      <div className="pricing-footer">
        <p>All plans include email delivery, analytics, and customer support.</p>
        <p>Need a custom plan? <a href="/contact">Contact us</a></p>
      </div>
    </div>
  );
}

export default Pricing; 