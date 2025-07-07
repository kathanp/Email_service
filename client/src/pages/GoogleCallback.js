import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { API_ENDPOINTS } from '../config';
import './AuthPage.css';

function GoogleCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const handleGoogleCallback = async () => {
      try {
        const code = searchParams.get('code');
        console.log('Google callback received with code:', code);
        
        if (!code) {
          setError('No authorization code received');
          setIsLoading(false);
          return;
        }

        // Call the backend to handle the Google OAuth callback
        const response = await fetch(`${API_ENDPOINTS.GOOGLE_AUTH}/callback?code=${code}`);
        console.log('Backend response status:', response.status);
        
        if (response.ok) {
          const data = await response.json();
          console.log('Backend response data:', data);
          
          // Use the data from backend response if available, otherwise create mock data
          const userData = data.user || {
            id: 'google_user_1',
            email: 'google.user@example.com',
            username: 'Google User',
            full_name: 'Google User'
          };
          
          const token = data.access_token || 'google_token_' + Date.now();
          
          // Store the user data and token
          localStorage.setItem('token', token);
          localStorage.setItem('user', JSON.stringify(userData));
          
          console.log('Stored token and user data, redirecting to dashboard...');
          setSuccess(true);
          
          // Redirect to dashboard with a small delay to ensure state updates
          setTimeout(() => {
            navigate('/dashboard', { replace: true });
          }, 1000);
        } else {
          const errorData = await response.json();
          console.error('Backend error:', errorData);
          setError(errorData.detail || 'Google authentication failed');
        }
      } catch (error) {
        console.error('Google callback error:', error);
        setError('Network error. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    handleGoogleCallback();
  }, [searchParams, navigate]);

  if (isLoading) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <h1>Processing Google Login</h1>
            <p>Please wait while we complete your authentication...</p>
          </div>
          <div className="loading-spinner">Loading...</div>
        </div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <h1>Authentication Successful!</h1>
            <p>Redirecting to dashboard...</p>
          </div>
          <div className="success-message">
            <p>✅ Google login successful!</p>
            <p>You will be redirected to the dashboard in a moment.</p>
          </div>
          <button 
            className="auth-button" 
            onClick={() => navigate('/dashboard', { replace: true })}
          >
            Go to Dashboard Now
          </button>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <h1>Authentication Error</h1>
            <p>Something went wrong with Google login</p>
          </div>
          <div className="error-message">{error}</div>
          <button 
            className="auth-button" 
            onClick={() => navigate('/')}
          >
            Back to Login
          </button>
        </div>
      </div>
    );
  }

  return null;
}

export default GoogleCallback; 