import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { API_ENDPOINTS } from '../config';
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
        
        // Call the backend to handle the Google OAuth callback
        const response = await fetch(`${API_ENDPOINTS.GOOGLE_AUTH}/callback?code=${code}`);
        
        if (response.ok) {
          const data = await response.json();
          console.log('Google callback response:', data);
          
          // Store the token and user data from backend response
          localStorage.setItem('token', data.access_token);
          localStorage.setItem('user', JSON.stringify(data.user));
          
          console.log('Stored token, redirecting to dashboard...');
          
          // Force redirect to dashboard
          window.location.href = '/dashboard';
        } else {
          const errorData = await response.json();
          setError(errorData.detail || 'Google authentication failed');
          setIsLoading(false);
        }
        
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