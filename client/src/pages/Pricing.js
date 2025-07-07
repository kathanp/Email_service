import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_ENDPOINTS } from '../config';
import './Pricing.css';

function Pricing() {
  const [plans, setPlans] = useState([]);
  const [currentSubscription, setCurrentSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [billingCycle, setBillingCycle] = useState('monthly');
  const navigate = useNavigate();

  useEffect(() => {
    fetchPlans();
    fetchCurrentSubscription();
  }, []);

  const fetchPlans = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.SUBSCRIPTIONS}/plans`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setPlans(data);
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
      const response = await fetch(`${API_ENDPOINTS.SUBSCRIPTIONS}/current`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setCurrentSubscription(data);
      }
    } catch (error) {
      console.error('Error fetching current subscription:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (plan) => {
    setSelectedPlan(plan);
    setError('');
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.SUBSCRIPTIONS}/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          plan: plan.id,
          billing_cycle: billingCycle
        })
      });

      if (response.ok) {
        const data = await response.json();
        navigate('/pricing/subscribe', { 
          state: { 
            subscription: data,
            plan: plan,
            billingCycle: billingCycle
          }
        });
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create subscription');
      }
    } catch (error) {
      setError('Network error creating subscription');
    }
  };

  const getCurrentPlan = () => {
    if (!currentSubscription) return null;
    return plans.find(plan => plan.id === currentSubscription.plan);
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
      </div>

      {error && <div className="error-message">{error}</div>}

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
        {plans.map((plan) => (
          <div 
            key={plan.id} 
            className={`plan-card ${isCurrentPlan(plan) ? 'current' : ''}`}
          >
            {isCurrentPlan(plan) && (
              <div className="current-badge">Current Plan</div>
            )}
            
            <div className="plan-header">
              <h3>{plan.name}</h3>
              <div className="price">
                <span className="currency">$</span>
                <span className="amount">
                  {billingCycle === 'monthly' ? plan.price_monthly : plan.price_yearly}
                </span>
                <span className="period">/{billingCycle === 'monthly' ? 'mo' : 'year'}</span>
              </div>
            </div>

            <div className="plan-features">
              <div className="feature">
                <span className="feature-label">Email Limit:</span>
                <span className="feature-value">{plan.features.email_limit.toLocaleString()} emails</span>
              </div>
              <div className="feature">
                <span className="feature-label">Sender Limit:</span>
                <span className="feature-value">{plan.features.sender_limit} senders</span>
              </div>
              <div className="feature">
                <span className="feature-label">Template Limit:</span>
                <span className="feature-value">{plan.features.template_limit} templates</span>
              </div>
              {plan.features.api_access && (
                <div className="feature">
                  <span className="feature-label">API Access:</span>
                  <span className="feature-value">✓ Included</span>
                </div>
              )}
              {plan.features.priority_support && (
                <div className="feature">
                  <span className="feature-label">Priority Support:</span>
                  <span className="feature-value">✓ Included</span>
                </div>
              )}
              {plan.features.white_label && (
                <div className="feature">
                  <span className="feature-label">White Label:</span>
                  <span className="feature-value">✓ Included</span>
                </div>
              )}
              {plan.features.custom_integrations && (
                <div className="feature">
                  <span className="feature-label">Custom Integrations:</span>
                  <span className="feature-value">✓ Included</span>
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