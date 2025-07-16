import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useStripe, useElements, CardElement } from '@stripe/react-stripe-js';
import { API_ENDPOINTS } from '../config';
import './StripePaymentForm.css';

function StripePaymentForm({ plan, billingCycle, onSuccess, onError }) {
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [debugInfo, setDebugInfo] = useState('');
  const navigate = useNavigate();
  
  const stripe = useStripe();
  const elements = useElements();

  useEffect(() => {
    if (!plan || !billingCycle) {
      navigate('/pricing');
      return;
    }
  }, [plan, billingCycle, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsProcessing(true);
    setError('');
    setSuccess('');
    setDebugInfo('Starting payment process...');

    if (!stripe || !elements) {
      setError('Stripe has not loaded yet. Please try again.');
      setIsProcessing(false);
      return;
    }

    try {
      setDebugInfo('Creating payment intent...');
      // Create payment intent on the backend
      const token = localStorage.getItem('token');
      const paymentIntentResponse = await fetch(`${API_ENDPOINTS.SUBSCRIPTIONS_V1}/create-payment-intent`, {
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

      if (!paymentIntentResponse.ok) {
        const errorData = await paymentIntentResponse.json();
        // eslint-disable-next-line no-console
        console.error('Payment intent creation failed:', errorData);
        setError(errorData.detail || 'Failed to create payment intent');
        setDebugInfo(`Payment intent failed: ${errorData.detail || 'Unknown error'}`);
        setIsProcessing(false);
        return;
      }

      const paymentData = await paymentIntentResponse.json();
      const { client_secret, is_free_plan, plan_id, billing_cycle: responseBillingCycle } = paymentData;
      
      // Handle free plan - no payment needed
      if (is_free_plan || plan_id === 'free') {
        setDebugInfo('Free plan selected, updating subscription...');
        
        // Confirm subscription change without payment
        const confirmResponse = await fetch(`${API_ENDPOINTS.SUBSCRIPTIONS_V1}/confirm-payment`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            plan_id: plan_id,
            billing_cycle: responseBillingCycle,
            is_free_plan: true
          })
        });

        if (confirmResponse.ok) {
          const confirmData = await confirmResponse.json();
          // eslint-disable-next-line no-console
          console.log('Subscription updated:', confirmData);
          setSuccess(`Successfully changed to ${plan.name} plan!`);
          setDebugInfo('Subscription updated successfully!');
          
          // Navigate back to pricing page with success parameter
          setTimeout(() => {
            navigate('/pricing?success=true', { replace: true });
          }, 2000);
        } else {
          const errorData = await confirmResponse.json();
          // eslint-disable-next-line no-console
          console.error('Subscription update failed:', errorData);
          setError(errorData.detail || 'Failed to update subscription. Please contact support.');
          setDebugInfo(`Subscription update failed: ${errorData.detail || 'Unknown error'}`);
        }
        
        setIsProcessing(false);
        return;
      }

      // Handle paid plans - process payment
      if (!client_secret) {
        setError('Payment setup failed. Please try again.');
        setDebugInfo('No client secret received for paid plan');
        setIsProcessing(false);
        return;
      }

      setDebugInfo('Payment intent created, confirming payment...');
      const cardElement = elements.getElement(CardElement);

      // Confirm the payment with Stripe
      const { error: stripeError, paymentIntent } = await stripe.confirmCardPayment(client_secret, {
        payment_method: {
          card: cardElement,
          billing_details: {
            name: 'Customer',
          }
        }
      });

      if (stripeError) {
        // eslint-disable-next-line no-console
        console.error('Stripe payment error:', stripeError);
        setError(stripeError.message || 'Payment failed');
        setDebugInfo(`Stripe error: ${stripeError.message}`);
      } else if (paymentIntent.status === 'succeeded') {
        setDebugInfo('Payment succeeded, updating subscription...');
        // eslint-disable-next-line no-console
        console.log('Payment succeeded:', paymentIntent.id);
        
        // Confirm payment on backend and update subscription
        try {
          const confirmResponse = await fetch(`${API_ENDPOINTS.SUBSCRIPTIONS_V1}/confirm-payment`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
              payment_intent_id: paymentIntent.id,
              plan_id: plan.id,
              billing_cycle: billingCycle,
              is_free_plan: false
            })
          });

          if (confirmResponse.ok) {
            const confirmData = await confirmResponse.json();
            // eslint-disable-next-line no-console
            console.log('Subscription updated:', confirmData);
        setSuccess('Payment successful! Your subscription has been upgraded.');
            setDebugInfo('Subscription updated successfully!');
            
        // Navigate back to pricing page with success parameter
        setTimeout(() => {
          navigate('/pricing?success=true', { replace: true });
            }, 3000);
          } else {
            const errorData = await confirmResponse.json();
            // eslint-disable-next-line no-console
            console.error('Subscription update failed:', errorData);
            setError(errorData.detail || 'Failed to confirm payment. Please contact support.');
            setDebugInfo(`Subscription update failed: ${errorData.detail || 'Unknown error'}`);
      }
        } catch (confirmError) {
          // eslint-disable-next-line no-console
          console.error('Confirmation request failed:', confirmError);
          setError('Failed to confirm payment. Please contact support.');
          setDebugInfo(`Confirmation request failed: ${confirmError.message}`);
        }
      } else {
        setError('Payment was not successful. Please try again.');
        setDebugInfo(`Payment status: ${paymentIntent.status}`);
      }
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Payment process error:', error);
      setError('An error occurred during payment. Please try again.');
      setDebugInfo(`Payment process error: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  if (!plan || !billingCycle) {
    return (
      <div className="payment-container">
        <div className="loading">Loading payment form...</div>
      </div>
    );
  }

  const cardElementOptions = {
    style: {
      base: {
        fontSize: '16px',
        color: '#424770',
        '::placeholder': {
          color: '#aab7c4',
        },
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        fontSmoothing: 'antialiased',
      },
      invalid: {
        color: '#9e2146',
        iconColor: '#9e2146',
      },
    },
    hidePostalCode: false,
  };

  return (
    <div className="payment-container compact">
        <form onSubmit={handleSubmit} className="payment-form compact">
          <div className="stripe-card-section">
            <label htmlFor="card-element">
              Card Information
            </label>
            <div className="stripe-card-element-wrapper">
              <CardElement
                id="card-element"
                options={cardElementOptions}
                onChange={(event) => {
                  if (event.error) {
                    setError(event.error.message);
                  } else {
                    setError('');
                  }
                }}
              />
            </div>
          </div>

          {error && <div className="error-message small">{error}</div>}
          {success && <div className="success-message small">{success}</div>}
          {debugInfo && <div className="debug-info small">{debugInfo}</div>}

          <button
            type="submit"
            className="payment-button compact"
            disabled={isProcessing || !stripe}
          >
            {isProcessing ? 'Processing...' : 'Complete Payment'}
          </button>
        </form>

        <div className="payment-footer compact">
          <div className="stripe-powered">
            <p className="tiny">Powered by Stripe</p>
          </div>
          <p className="tiny">Your payment information is secure and encrypted.</p>
      </div>
    </div>
  );
}

export default StripePaymentForm; 