import React, { useState } from 'react';
import { CardElement, useStripe, useElements } from '@stripe/react-stripe-js';
import './StripePaymentForm.css';

const CARD_ELEMENT_OPTIONS = {
  style: {
    base: {
      fontSize: '16px',
      color: '#424770',
      '::placeholder': {
        color: '#aab7c4',
      },
    },
    invalid: {
      color: '#9e2146',
    },
  },
  iconStyle: 'solid',
};

function StripePaymentForm({ plan, billingCycle, onSuccess, onError }) {
  const stripe = useStripe();
  const elements = useElements();
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [cardholderName, setCardholderName] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    if (!cardholderName.trim()) {
      setError('Please enter the cardholder name');
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      // Create payment method
      const { error: paymentMethodError, paymentMethod } = await stripe.createPaymentMethod({
        type: 'card',
        card: elements.getElement(CardElement),
        billing_details: {
          name: cardholderName,
        },
      });

      if (paymentMethodError) {
        setError(paymentMethodError.message);
        setIsProcessing(false);
        return;
      }

      // Create subscription with payment method
      const response = await fetch('http://localhost:8000/api/v1/subscriptions/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          plan: plan.plan_id,
          billing_cycle: billingCycle,
          stripe_payment_method_id: paymentMethod.id
        })
      });

      const result = await response.json();

      if (response.ok) {
        onSuccess(result);
        // Dispatch custom event for subscription change instead of page reload
        window.dispatchEvent(new CustomEvent('subscriptionChanged'));
        // Also refresh the page to ensure all components update
        setTimeout(() => {
          window.location.reload();
        }, 1000);
      } else {
        setError(result.detail || 'Failed to create subscription');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const getPlanPrice = (plan, billingCycle) => {
    return billingCycle === 'monthly' ? plan.price_monthly : plan.price_yearly;
  };

  return (
    <form onSubmit={handleSubmit} className="stripe-payment-form" autoComplete="off">
      <div className="form-group">
        <label>Cardholder Name</label>
        <input
          type="text"
          value={cardholderName}
          onChange={(e) => setCardholderName(e.target.value)}
          placeholder="John Doe"
          className="cardholder-input"
          required
          autoComplete="off"
        />
      </div>

      <div className="form-group">
        <label>Card Information</label>
        <div className="card-element-container">
          <CardElement options={CARD_ELEMENT_OPTIONS} />
        </div>
        <div className="card-info">
          <span className="card-info-text">💳 Card number, expiry date, CVC, and ZIP code</span>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <button 
        type="submit" 
        disabled={!stripe || isProcessing} 
        className="subscribe-btn"
      >
        {isProcessing ? 'Processing...' : `Subscribe Now - $${getPlanPrice(plan, billingCycle)}/${billingCycle === 'monthly' ? 'month' : 'year'}`}
      </button>
    </form>
  );
}

export default StripePaymentForm; 