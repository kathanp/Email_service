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
        const token = searchParams.get('token');
        const userEmail = searchParams.get('user');
        
        if (!token) {
          setError('No authentication token received');
          setIsLoading(false);
          return;
        }

        console.log('Google callback token received:', token);
        console.log('User email:', userEmail);
        
        // Store the token
        localStorage.setItem('token', token);
        
        // Create a basic user object with the email
        const userData = {
          email: userEmail,
          full_name: userEmail.split('@')[0], // Use email prefix as name
          google_email: userEmail
        };
        localStorage.setItem('user', JSON.stringify(userData));
        
        console.log('Stored token, redirecting to dashboard...');
        
        // Redirect to dashboard using React Router
        navigate('/dashboard', { replace: true });
        
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