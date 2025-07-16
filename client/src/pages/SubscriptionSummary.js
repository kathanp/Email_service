import React, { useState, useEffect, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { loadStripe } from '@stripe/stripe-js';
import { Elements } from '@stripe/react-stripe-js';
import StripePaymentForm from '../components/StripePaymentForm';
import { API_ENDPOINTS } from '../config';
import './SubscriptionSummary.css';

// Load Stripe with your publishable key from environment variables
const stripeKey = process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY;
const stripePromise = stripeKey ? loadStripe(stripeKey).catch(error => {
  // eslint-disable-next-line no-console
  console.error('Failed to load Stripe:', error);
  return null;
}) : Promise.resolve(null);

function SubscriptionSummary() {
  const location = useLocation();
  const navigate = useNavigate();
  const { plan, billingCycle } = location.state || {};
  const [clientSecret, setClientSecret] = useState('');
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  const createPaymentIntent = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.SUBSCRIPTIONS_V1}/create-payment-intent`, {
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

      if (!response.ok) {
        const errorData = await response.json();
                  // eslint-disable-next-line no-console
          console.log('Payment intent error:', errorData);
        // Show form anyway for demonstration
        setShowForm(true);
        setLoading(false);
        return;
      }

      const data = await response.json();
      setClientSecret(data.client_secret);
      setShowForm(true);
      setLoading(false);
    } catch (err) {
      // eslint-disable-next-line no-console
      console.log('Network error:', err);
      // Show form anyway for demonstration
      setShowForm(true);
      setLoading(false);
    }
  }, [plan, billingCycle]);

  useEffect(() => {
    if (!plan || !billingCycle) {
      navigate('/pricing');
      return;
    }
    createPaymentIntent();
  }, [plan, billingCycle, navigate, createPaymentIntent]);

  if (!plan || !billingCycle) {
    navigate('/pricing');
    return null;
  }

  const getPlanPrice = (plan, billingCycle) => {
    return billingCycle === 'monthly' ? plan.price_monthly : plan.price_yearly;
  };

  const handleBack = () => {
    navigate('/pricing');
  };

  const handleSubscriptionSuccess = (result) => {
    alert('Subscription created successfully!');
    navigate('/settings');
  };

  const handleSubscriptionError = (error) => {
    // Handle subscription error
  };

  if (loading) {
    return (
      <div className="subscription-summary-wrapper">
        <div className="subscription-summary-container">
          <div className="loading">Creating payment session...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="subscription-summary-wrapper">
      <div className="subscription-summary-container">
        <button className="back-button" onClick={handleBack}>
          ← Back to Plans
        </button>
        
        <div className="subscription-summary">
          <div className="payment-section">
            <h3>Secure Payment</h3>
            {showForm && (
              <Elements 
                stripe={stripePromise} 
                options={{
                  clientSecret: clientSecret || undefined,
                  appearance: {
                    theme: 'stripe',
                  },
                }}
              >
                <StripePaymentForm
                  plan={plan}
                  billingCycle={billingCycle}
                  onSuccess={handleSubscriptionSuccess}
                  onError={handleSubscriptionError}
                />
              </Elements>
            )}
          </div>

          <div className="summary-section">
            <h2 className="summary-title">Subscription Summary</h2>
            
            <div className="summary-details">
              <div className="summary-item">
                <span className="label">Plan:</span>
                <span className="value">{plan.name}</span>
              </div>
              <div className="summary-item">
                <span className="label">Billing Cycle:</span>
                <span className="value">{billingCycle === 'monthly' ? 'Monthly' : 'Yearly'}</span>
              </div>
              <div className="summary-item">
                <span className="label">Price:</span>
                <span className="value">${getPlanPrice(plan, billingCycle)}/{billingCycle === 'monthly' ? 'month' : 'year'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SubscriptionSummary; 