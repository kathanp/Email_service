import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { API_ENDPOINTS } from '../config';
import './StripePaymentForm.css';

function StripePaymentForm() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [stripeKey, setStripeKey] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  const subscription = location.state?.subscription;
  const plan = location.state?.plan;
  const billingCycle = location.state?.billingCycle;

  useEffect(() => {
    if (!subscription || !plan) {
      navigate('/pricing');
      return;
    }

    fetchStripeKey();
  }, [subscription, plan, navigate]);

  const fetchStripeKey = async () => {
    try {
      const response = await fetch(`${API_ENDPOINTS.SUBSCRIPTIONS}/stripe-key`);
      if (response.ok) {
        const data = await response.json();
        setStripeKey(data.publishable_key);
      } else {
        setError('Failed to load payment configuration');
      }
    } catch (error) {
      setError('Network error loading payment configuration');
    }
  };

  const handlePaymentSuccess = () => {
    setSuccess('Payment successful! Your subscription is now active.');
    setTimeout(() => {
      navigate('/dashboard');
    }, 2000);
  };

  const handlePaymentError = (error) => {
    setError(error.message || 'Payment failed. Please try again.');
  };

  if (!subscription || !plan) {
    return (
      <div className="payment-container">
        <div className="loading">Loading payment form...</div>
      </div>
    );
  }

  return (
    <div className="payment-container">
      <div className="payment-card">
        <div className="payment-header">
          <h1>Complete Your Subscription</h1>
          <p>Set up payment for your {plan.name} plan</p>
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        <div className="subscription-summary">
          <h2>Subscription Details</h2>
          <div className="summary-item">
            <span className="label">Plan:</span>
            <span className="value">{plan.name}</span>
          </div>
          <div className="summary-item">
            <span className="label">Billing Cycle:</span>
            <span className="value">{billingCycle}</span>
          </div>
          <div className="summary-item">
            <span className="label">Amount:</span>
            <span className="value">
              ${billingCycle === 'monthly' ? plan.price_monthly : plan.price_yearly}
              /{billingCycle === 'monthly' ? 'month' : 'year'}
            </span>
          </div>
        </div>

        <div className="payment-form">
          <h2>Payment Information</h2>
          <p>Your payment information is secure and encrypted.</p>
          
          {/* Stripe Elements would go here in a real implementation */}
          <div className="stripe-placeholder">
            <p>Stripe payment form would be integrated here</p>
            <p>For demo purposes, this is a placeholder</p>
          </div>

          <button
            className="btn-primary payment-button"
            onClick={() => handlePaymentSuccess()}
            disabled={loading}
          >
            {loading ? 'Processing...' : 'Complete Payment'}
          </button>
        </div>

        <div className="payment-footer">
          <p>By completing this payment, you agree to our Terms of Service and Privacy Policy.</p>
          <button
            className="btn-secondary"
            onClick={() => navigate('/pricing')}
          >
            Back to Plans
          </button>
        </div>
      </div>
    </div>
  );
}

export default StripePaymentForm; 