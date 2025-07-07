import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import './AuthPage.css';

function SetToken() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const handleSetToken = async () => {
      try {
        const token = searchParams.get('token');
        const userEmail = searchParams.get('user');
        
        if (!token || !userEmail) {
          setError('Missing token or user information');
          setIsLoading(false);
          return;
        }

        console.log('Setting Google OAuth token...');
        
        // Store the token
        localStorage.setItem('token', token);
        
        // Create user object
        const userData = {
          id: `google_user_${userEmail.split('@')[0]}`,
          email: userEmail,
          username: 'Google User',
          full_name: 'Google User'
        };
        
        // Store user data
        localStorage.setItem('user', JSON.stringify(userData));
        
        console.log('Token and user data stored successfully');
        
        // Redirect to clean dashboard URL
        window.location.href = '/dashboard';
        
      } catch (error) {
        console.error('Set token error:', error);
        setError('Failed to set authentication token');
        setIsLoading(false);
      }
    };

    handleSetToken();
  }, [searchParams, navigate]);

  if (isLoading) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <h1>Completing Login</h1>
            <p>Setting up your account...</p>
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
          <h1>Login Successful</h1>
          <p>Redirecting to dashboard...</p>
        </div>
      </div>
    </div>
  );
}

export default SetToken; 