import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
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
    
    // Check if this is a downgrade to free plan
    if (plan.id === 'free' && currentSubscription && currentSubscription.plan_id !== 'free') {
      // Handle downgrade to free plan directly
      await handleDowngradeToFree(plan);
      return;
    }
    
    // Redirect to payment page for paid plans
    navigate('/pricing/subscribe', { 
      state: { 
        plan: plan,
        billingCycle: billingCycle
      }
    });
  };

  const handleDowngradeToFree = async (plan) => {
    setError('');
    
    if (!window.confirm('Are you sure you want to downgrade to the Free plan? You will lose access to premium features.')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.SUBSCRIPTIONS_V1}/change-plan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          plan_id: 'free',
          billing_cycle: billingCycle
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setSuccess('Successfully downgraded to Free plan!');
          // Refresh subscription data
          await fetchCurrentSubscription();
        } else {
          setError(data.message || 'Failed to downgrade subscription');
        }
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to downgrade subscription');
      }
    } catch (error) {
      setError('Network error during downgrade. Please try again.');
    }
  };

  const isCurrentPlan = (plan) => {
    return currentSubscription && currentSubscription.plan_id === plan.id;
  };

  const getPlanPrice = (plan) => {
    return billingCycle === 'monthly' ? plan.price_monthly : plan.price_yearly;
  };

  const getSavingsPercentage = (monthly, yearly) => {
    if (monthly === 0 || yearly === 0) return 0;
    const monthlyCost = monthly * 12;
    const savings = ((monthlyCost - yearly) / monthlyCost) * 100;
    return Math.round(savings);
  };

  const formatFeatureValue = (value) => {
    if (value === -1) return 'Unlimited';
    if (typeof value === 'number') return value.toLocaleString();
    return value;
  };

  const getPopularPlan = () => {
    // Mark Professional as popular
    return 'professional';
  };

  if (loading) {
    return (
      <Layout>
        <div className="pricing-loading">
          <div className="loading-spinner"></div>
          <p>Loading subscription plans...</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="pricing-container">
        <div className="pricing-header">
          <h1>Choose Your Perfect Plan</h1>
          <p>Unlock the full potential of your email marketing campaigns with our flexible pricing options</p>
          

        </div>

        {error && (
          <div className="message error-message">
            <span className="message-icon">⚠️</span>
            {error}
          </div>
        )}
        
        {success && (
          <div className="message success-message">
            <span className="message-icon">✅</span>
            {success}
          </div>
        )}

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
          {billingCycle === 'yearly' && (
            <div className="savings-badge">
              <span className="savings-text">Save up to 20%</span>
            </div>
          )}
        </div>

        <div className="plans-grid">
          {Array.isArray(plans) && plans.map((plan) => (
            plan && (
              <div 
                key={plan.id} 
                className={`plan-card ${isCurrentPlan(plan) ? 'current-plan' : ''} ${plan.id === getPopularPlan() ? 'popular-plan' : ''}`}
              >
                {plan.id === getPopularPlan() && (
                  <div className="popular-badge">Most Popular</div>
                )}
                
                {isCurrentPlan(plan) && (
                  <div className="current-badge">Current Plan</div>
                )}
                
                <div className="plan-header">
                  <h3>{plan.name || 'Unnamed Plan'}</h3>
                  <div className="plan-price">
                    <span className="currency">$</span>
                    <span className="amount">{getPlanPrice(plan)}</span>
                    <span className="period">/{billingCycle === 'monthly' ? 'month' : 'year'}</span>
                  </div>
                  {billingCycle === 'yearly' && plan.price_monthly > 0 && (
                    <div className="savings-info">
                      Save {getSavingsPercentage(plan.price_monthly, plan.price_yearly)}% annually
                    </div>
                  )}
                </div>

                <div className="plan-features">
                  <div className="features-list">
                    <ul>
                      <li>
                        <span className="feature-icon">📧</span>
                        <span className="feature-text">{formatFeatureValue(plan.features.email_limit)}/mo emails</span>
                      </li>
                      <li>
                        <span className="feature-icon">👤</span>
                        <span className="feature-text">{formatFeatureValue(plan.features.sender_limit)} senders</span>
                      </li>
                      <li>
                        <span className="feature-icon">📝</span>
                        <span className="feature-text">{formatFeatureValue(plan.features.template_limit)} templates</span>
                      </li>
                      {plan.features.api_access && (
                        <li>
                          <span className="feature-icon">🔌</span>
                          <span className="feature-text">API Access</span>
                        </li>
                      )}
                      {plan.features.priority_support && (
                        <li>
                          <span className="feature-icon">⚡</span>
                          <span className="feature-text">Priority Support</span>
                        </li>
                      )}
                      {plan.features.white_label && (
                        <li>
                          <span className="feature-icon">🏷️</span>
                          <span className="feature-text">White Label</span>
                        </li>
                      )}
                      {plan.features.custom_integrations && (
                        <li>
                          <span className="feature-icon">🔗</span>
                          <span className="feature-text">Custom Integrations</span>
                        </li>
                      )}
                    </ul>
                  </div>
                </div>

                <div className="plan-action">
                  <button
                    className={`plan-button ${isCurrentPlan(plan) ? 'current' : plan.id === getPopularPlan() ? 'popular' : ''}`}
                    onClick={() => handleSubscribe(plan)}
                    disabled={isCurrentPlan(plan)}
                  >
                    {isCurrentPlan(plan) ? (
                      <>
                        <span className="button-icon">✓</span>
                        Current Plan
                      </>
                    ) : (
                      <>
                        <span className="button-icon">
                          {plan.id === 'free' && currentSubscription && currentSubscription.plan_id !== 'free' ? '⬇️' : '🚀'}
                        </span>
                        {plan.id === 'free' && currentSubscription && currentSubscription.plan_id !== 'free' 
                          ? `Downgrade to ${plan.name}` 
                          : `Choose ${plan.name}`}
                      </>
                    )}
                  </button>
                </div>
              </div>
            )
          ))}
        </div>
      </div>
    </Layout>
  );
}

export default Pricing; 