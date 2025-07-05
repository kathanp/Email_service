import React, { useState, useEffect } from 'react';
import './Pricing.css';
import { useNavigate } from 'react-router-dom';

function Pricing() {
  const [plans, setPlans] = useState([]);
  const [currentPlan, setCurrentPlan] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [billingCycle, setBillingCycle] = useState('monthly');
  const navigate = useNavigate();

  useEffect(() => {
    fetchPlans();
    fetchCurrentSubscription();
  }, []);

  const fetchPlans = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/subscriptions/plans', {
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
    } catch (err) {
      setError('Network error loading plans');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchCurrentSubscription = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/subscriptions/current', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentPlan(data);
      }
    } catch (err) {
      console.error('Error fetching current subscription:', err);
    }
  };

  const handlePlanSelect = (plan) => {
    navigate('/pricing/subscribe', { state: { plan, billingCycle } });
  };

  const handleSubscribe = async () => {
    if (!selectedPlan) {
      setError('Please select a plan');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/subscriptions/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          plan: selectedPlan.plan_id,
          billing_cycle: billingCycle
        })
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentPlan(data);
        setSelectedPlan(null);
        setError('');
        alert('Subscription created successfully!');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create subscription');
      }
    } catch (err) {
      setError('Network error creating subscription');
    }
  };

  const getPlanPrice = (plan) => {
    return billingCycle === 'monthly' ? plan.price_monthly : plan.price_yearly;
  };

  const getPlanSavings = (plan) => {
    if (billingCycle === 'yearly' && plan.price_yearly < plan.price_monthly * 12) {
      const savings = (plan.price_monthly * 12 - plan.price_yearly) / (plan.price_monthly * 12) * 100;
      return Math.round(savings);
    }
    return 0;
  };

  if (isLoading) {
    return (
      <div className="pricing-wrapper">
        <div className="pricing">
          <div className="loading">Loading pricing plans...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="pricing-wrapper">
      <div className="pricing">
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
          <span className={billingCycle === 'yearly' ? 'active' : ''}>
            Yearly <span className="savings">Save up to 17%</span>
          </span>
        </div>

        <div className="plans-grid">
          {plans.map((plan) => {
            const isCurrentPlan = currentPlan && currentPlan.plan === plan.plan_id;
            const isSelected = selectedPlan && selectedPlan.plan_id === plan.plan_id;
            const savings = getPlanSavings(plan);
            
            return (
              <div 
                key={plan.plan_id} 
                className={`plan-card ${isCurrentPlan ? 'current-plan' : ''} ${isSelected ? 'selected-plan' : ''}`}
                onClick={() => !isCurrentPlan && handlePlanSelect(plan)}
              >
                {isCurrentPlan && <div className="current-badge">Current Plan</div>}
                {savings > 0 && billingCycle === 'yearly' && (
                  <div className="savings-badge">Save {savings}%</div>
                )}
                
                <div className="plan-header">
                  <h3>{plan.name}</h3>
                  <div className="plan-price">
                    <span className="currency">$</span>
                    <span className="amount">{getPlanPrice(plan)}</span>
                    <span className="period">/{billingCycle === 'monthly' ? 'mo' : 'year'}</span>
                  </div>
                  {plan.price_monthly === 0 && (
                    <p className="free-forever">Free Forever</p>
                  )}
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

                <div className="plan-actions">
                  {isCurrentPlan ? (
                    <button className="current-plan-btn" disabled>
                      Current Plan
                    </button>
                  ) : (
                    <button 
                      className={`select-plan-btn ${isSelected ? 'selected' : ''}`}
                      onClick={(e) => {
                        e.stopPropagation();
                        handlePlanSelect(plan);
                      }}
                    >
                      {isSelected ? 'Selected' : 'Select Plan'}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {selectedPlan && (
          <div className="subscription-summary">
            <h3>Subscription Summary</h3>
            <div className="summary-details">
              <p><strong>Plan:</strong> {selectedPlan.name}</p>
              <p><strong>Billing Cycle:</strong> {billingCycle === 'monthly' ? 'Monthly' : 'Yearly'}</p>
              <p><strong>Price:</strong> ${getPlanPrice(selectedPlan)}/{billingCycle === 'monthly' ? 'month' : 'year'}</p>
              {getPlanSavings(selectedPlan) > 0 && (
                <p><strong>Savings:</strong> {getPlanSavings(selectedPlan)}% with yearly billing</p>
              )}
            </div>
            <button className="subscribe-btn" onClick={handleSubscribe}>
              Subscribe Now
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default Pricing; 