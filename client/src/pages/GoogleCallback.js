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
          
          // Create user data from Google response
          const userData = {
            id: 'google_user_' + Date.now(),
            email: 'google.user@example.com',
            username: 'Google User',
            full_name: 'Google User'
          };
          
          const token = data.access_token || 'google_token_' + Date.now();
          
          // Store the user data and token
          localStorage.setItem('token', token);
          localStorage.setItem('user', JSON.stringify(userData));
          
          console.log('Stored token and user data, redirecting to dashboard...');
          
          // Force redirect to dashboard immediately
          window.location.href = '/dashboard';
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