import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { loadStripe } from '@stripe/stripe-js';
import { Elements } from '@stripe/react-stripe-js';
import StripePaymentForm from '../components/StripePaymentForm';
import './SubscriptionSummary.css';

// Load Stripe with your publishable key
const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY);

function SubscriptionSummary() {
  const location = useLocation();
  const navigate = useNavigate();
  const { plan, billingCycle } = location.state || {};

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

  return (
    <div className="subscription-summary-wrapper">
      <div className="subscription-summary-container">
        <button className="back-button" onClick={handleBack}>
          ← Back to Plans
        </button>
        
        <div className="subscription-summary">
          <div className="payment-section">
            <h3>Secure Payment</h3>
            <Elements stripe={stripePromise}>
              <StripePaymentForm
                plan={plan}
                billingCycle={billingCycle}
                onSuccess={handleSubscriptionSuccess}
                onError={handleSubscriptionError}
              />
            </Elements>
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