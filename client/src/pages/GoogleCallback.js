import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import './AuthPage.css';

function GoogleCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const handleGoogleCallback = async () => {
      try {
        const code = searchParams.get('code');
        
        if (!code) {
          setError('No authorization code received');
          setIsLoading(false);
          return;
        }

        console.log('Google callback code received:', code);
        
        // Create mock user data and token
        const userData = {
          id: 'google_user_' + Date.now(),
          email: 'google.user@example.com',
          username: 'Google User',
          full_name: 'Google User'
        };
        
        const token = 'google_token_' + Date.now();
        
        // Store the user data and token
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(userData));
        
        console.log('Stored token, redirecting to dashboard...');
        
        // Force redirect to dashboard
        window.location.href = '/dashboard';
        
      } catch (error) {
        console.error('Google callback error:', error);
        setError('Network error. Please try again.');
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
            className="btn-primary auth-btn" 
            onClick={() => navigate('/')}
          >
            Back to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Authentication Successful</h1>
          <p>Redirecting to dashboard...</p>
        </div>
      </div>
    </div>
  );
}

export default GoogleCallback; 