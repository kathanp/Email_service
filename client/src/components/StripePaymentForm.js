import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_ENDPOINTS } from '../config';
import './StripePaymentForm.css';

function StripePaymentForm({ plan, billingCycle, onSuccess, onError }) {
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [cardNumber, setCardNumber] = useState('');
  const [expiryDate, setExpiryDate] = useState('');
  const [cvc, setCvc] = useState('');
  const [cardType, setCardType] = useState('');
  const [fullName, setFullName] = useState('');
  const [zipCode, setZipCode] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!plan || !billingCycle) {
      navigate('/pricing');
      return;
    }
    fetchStripeKey();
  }, [plan, billingCycle, navigate]);

  const fetchStripeKey = async () => {
    try {
      const response = await fetch(`${API_ENDPOINTS.SUBSCRIPTIONS}/stripe-key`);
      if (response.ok) {
        const data = await response.json();
        console.log('Stripe key loaded:', data.publishable_key);
      } else {
        setError('Failed to load payment configuration');
      }
    } catch (error) {
      setError('Network error loading payment configuration');
    }
  };

  const detectCardType = (number) => {
    const cleanNumber = number.replace(/\s/g, '');
    
    if (/^4/.test(cleanNumber)) return 'visa';
    if (/^5[1-5]/.test(cleanNumber)) return 'mastercard';
    if (/^3[47]/.test(cleanNumber)) return 'amex';
    if (/^6/.test(cleanNumber)) return 'discover';
    if (/^35/.test(cleanNumber)) return 'jcb';
    if (/^2/.test(cleanNumber)) return 'mastercard'; // Mastercard 2-series
    
    return '';
  };

  const formatCardNumber = (value) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    const matches = v.match(/\d{4,16}/g);
    const match = matches && matches[0] || '';
    const parts = [];
    
    for (let i = 0, len = match.length; i < len; i += 4) {
      parts.push(match.substring(i, i + 4));
    }
    
    if (parts.length) {
      return parts.join(' ');
    } else {
      return v;
    }
  };

  const formatExpiry = (value) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    if (v.length >= 2) {
      return v.substring(0, 2) + '/' + v.substring(2, 4);
    }
    return v;
  };

  const handleCardNumberChange = (e) => {
    const formatted = formatCardNumber(e.target.value);
    setCardNumber(formatted);
    setCardType(detectCardType(formatted));
  };

  const handleExpiryChange = (e) => {
    setExpiryDate(formatExpiry(e.target.value));
  };

  const handleCvcChange = (e) => {
    setCvc(e.target.value.replace(/\D/g, '').substring(0, 4));
  };

  const validateForm = () => {
    if (!cardNumber.replace(/\s/g, '').match(/^\d{13,19}$/)) {
      setError('Please enter a valid card number');
      return false;
    }
    if (!expiryDate.match(/^(0[1-9]|1[0-2])\/([0-9]{2})$/)) {
      setError('Please enter a valid expiry date (MM/YY)');
      return false;
    }
    if (!cvc.match(/^\d{3,4}$/)) {
      setError('Please enter a valid CVC');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsProcessing(true);
    setError('');

    // Validate form
    if (!validateForm()) {
      setIsProcessing(false);
      return;
    }

    try {
      // For testing purposes, directly upgrade the subscription
      const token = localStorage.getItem('token');
      const upgradeResponse = await fetch('/api/v1/subscriptions/upgrade', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          plan: plan.id
        })
      });

      if (upgradeResponse.ok) {
        const result = await upgradeResponse.json();
        setSuccess('Payment successful! Your subscription has been upgraded.');
        // Navigate back to pricing page with success parameter
        setTimeout(() => {
          navigate('/pricing?success=true', { replace: true });
        }, 2000);
      } else {
        const errorData = await upgradeResponse.json();
        setError(errorData.detail || 'Payment failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const getCardIcon = () => {
    switch (cardType) {
      case 'visa': return '💳';
      case 'mastercard': return '💳';
      case 'amex': return '💳';
      case 'discover': return '💳';
      case 'jcb': return '💳';
      default: return '💳';
    }
  };

  if (!plan || !billingCycle) {
    return (
      <div className="payment-container">
        <div className="loading">Loading payment form...</div>
      </div>
    );
  }

  return (
    <div className="payment-container compact">
      <div className="payment-card compact">
        <div className="payment-header compact">
          <h2>Secure Payment</h2>
          <p className="small">Complete Your Subscription</p>
          <p className="smaller">{plan.name} plan &bull; {billingCycle}</p>
        </div>

        <form onSubmit={handleSubmit} className="payment-form compact">
          <h3>Payment Information</h3>
          
          <div className="card-input-section">
            <div className="input-group">
              <label>Full Name</label>
              <input
                type="text"
                className="cardholder-input"
                placeholder="John Doe"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
              />
            </div>

            <div className="input-group">
              <label>Card Number</label>
              <div className="card-input-wrapper">
                <input
                  type="text"
                  className="card-number-input"
                  placeholder="1234 5678 9012 3456"
                  value={cardNumber}
                  onChange={(e) => setCardNumber(e.target.value)}
                  maxLength="19"
                  required
                />
                {cardType && (
                  <div className="card-type-icon" data-type={cardType}>
                    {cardType.toUpperCase()}
                  </div>
                )}
              </div>
            </div>

            <div className="card-details-row">
              <div className="input-group">
                <label>Expiry Date</label>
                <input
                  type="text"
                  className="expiry-input"
                  placeholder="MM/YY"
                  value={expiryDate}
                  onChange={(e) => setExpiryDate(e.target.value)}
                  maxLength="5"
                  required
                />
              </div>
              <div className="input-group">
                <label>CVC</label>
                <input
                  type="text"
                  className="cvc-input"
                  placeholder="123"
                  value={cvc}
                  onChange={(e) => setCvc(e.target.value)}
                  maxLength="4"
                  required
                />
              </div>
            </div>

            <div className="input-group">
              <label>ZIP Code</label>
              <input
                type="text"
                className="zip-input"
                placeholder="12345"
                value={zipCode}
                onChange={(e) => setZipCode(e.target.value)}
                maxLength="10"
                required
              />
            </div>
          </div>

          {error && <div className="error-message small">{error}</div>}
          {success && <div className="success-message small">{success}</div>}

          <button
            type="submit"
            className="payment-button compact"
            disabled={isProcessing}
          >
            {isProcessing ? 'Processing...' : 'Complete Payment'}
          </button>
        </form>

        <div className="payment-footer compact">
          <p className="tiny">Your payment information is secure and encrypted.</p>
          <p className="tiny">By completing this payment, you agree to our Terms of Service and Privacy Policy.</p>
        </div>
      </div>
    </div>
  );
}

export default StripePaymentForm; 