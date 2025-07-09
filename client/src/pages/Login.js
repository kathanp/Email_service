import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_ENDPOINTS } from '../config';
import './AuthPage.css';

function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const navigate = useNavigate();

  const checkAuthStatus = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await fetch(`${API_ENDPOINTS.AUTH}/me`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          
          if (response.ok) {
            const userData = await response.json();
            localStorage.setItem('user', JSON.stringify(userData));
            navigate('/dashboard');
          } else {
        // Token is invalid, remove it
        localStorage.removeItem('token');
        localStorage.removeItem('user');
          }
        } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  }, [navigate]);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    if (token) {
      checkAuthStatus();
    }
  }, [checkAuthStatus]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setIsLoading(true);

    try {
      if (!isLogin && formData.password !== formData.confirmPassword) {
        setError('Passwords do not match');
        setIsLoading(false);
        return;
      }

      const endpoint = isLogin ? `${API_ENDPOINTS.AUTH}/login` : `${API_ENDPOINTS.AUTH}/register`;
      const body = isLogin 
        ? { email: formData.email, password: formData.password }
        : { name: formData.name, email: formData.email, password: formData.password };

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
      });

      const data = await response.json();

      if (response.ok) {
        if (isLogin) {
          console.log('Login successful, storing token:', data.access_token);
          localStorage.setItem('token', data.access_token);
          localStorage.setItem('user', JSON.stringify(data.user));
          setSuccess('Login successful! Redirecting...');
          navigate('/dashboard');
        } else {
          // After successful registration, automatically log the user in
          console.log('Registration successful, storing token:', data.access_token);
          console.log('User data:', data.user);
          
          // Store token and user data
          localStorage.setItem('token', data.access_token);
          localStorage.setItem('user', JSON.stringify(data.user));
          
          // Verify token was stored correctly
          const storedToken = localStorage.getItem('token');
          const storedUser = localStorage.getItem('user');
          console.log('Stored token:', storedToken);
          console.log('Stored user:', storedUser);
          
          setSuccess('Registration successful! Redirecting to dashboard...');
          
          // Small delay to ensure storage is complete
          setTimeout(() => {
            navigate('/dashboard');
          }, 100);
        }
      } else {
        setError(data.detail || (isLogin ? 'Login failed' : 'Registration failed'));
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setIsGoogleLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_ENDPOINTS.GOOGLE_AUTH}/login-url`);
      
      if (response.ok) {
        const data = await response.json();
        window.location.href = data.auth_url;
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to initiate Google login');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setIsGoogleLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setError('');
    setSuccess('');
    setFormData({ name: '', email: '', password: '', confirmPassword: '' });
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>{isLogin ? 'Welcome Back' : 'Create Account'}</h1>
          <p>{isLogin ? 'Sign in to your account' : 'Join us today'}</p>
        </div>
        
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          {!isLogin && (
            <div className="form-group">
              <label htmlFor="name">Full Name</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required={!isLogin}
                placeholder="Enter your full name"
              />
            </div>
          )}
            
            <div className="form-group">
            <label htmlFor="email">Email</label>
              <input
                type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
              placeholder="Enter your email"
            />
            </div>
            
          <div className="form-group">
            <label htmlFor="password">Password</label>
              <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              required
              placeholder="Enter your password"
            />
            </div>
            
          {!isLogin && (
            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                required={!isLogin}
                placeholder="Confirm your password"
              />
            </div>
          )}

          <button 
            type="submit" 
            className="btn-primary auth-btn"
            disabled={isLoading}
          >
            {isLoading ? 'Loading...' : (isLogin ? 'Sign In' : 'Create Account')}
            </button>
          </form>

        <div className="auth-divider">
          <span>or</span>
        </div>

        <button 
          onClick={handleGoogleLogin}
          className="btn-google auth-btn"
          disabled={isGoogleLoading}
        >
          {isGoogleLoading ? 'Loading...' : 'Continue with Google'}
        </button>

        <div className="auth-footer">
          <p>
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button 
              type="button" 
              onClick={toggleMode}
              className="link-button"
            >
              {isLogin ? 'Sign up' : 'Sign in'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}

export default AuthPage; 