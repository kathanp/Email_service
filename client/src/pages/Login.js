import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { FaEye, FaEyeSlash, FaGoogle } from 'react-icons/fa';
import './AuthPage.css';
import { register as apiRegister, login as apiLogin } from '../services/authService';

function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [loginData, setLoginData] = useState({
    email: '',
    password: ''
  });
  const [registerData, setRegisterData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  
  // Password visibility states
  const [showLoginPassword, setShowLoginPassword] = useState(false);
  const [showRegisterPassword, setShowRegisterPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  const navigate = useNavigate();
  const location = useLocation();

  // Handle Google OAuth callback
  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const token = urlParams.get('token');
    
    if (token) {
      console.log('Google OAuth token received:', token);
      
      // Store the token
      localStorage.setItem('token', token);
      
      // Get user info from the backend using the token
      const getUserInfo = async () => {
        try {
          console.log('Fetching user info...');
          
          // Check if we should use development endpoint
          const isDevMode = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
          const endpoint = isDevMode ? 'http://localhost:8000/api/auth/me/dev' : 'http://localhost:8000/api/auth/me';
          
          const response = await fetch(endpoint, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          
          console.log('Response status:', response.status);
          
          if (response.ok) {
            const userData = await response.json();
            console.log('User data received:', userData);
            localStorage.setItem('user', JSON.stringify(userData));
            
            // Clear the URL parameters
            window.history.replaceState({}, document.title, window.location.pathname);
            
            console.log('Navigating to dashboard...');
            // Navigate to dashboard
            navigate('/dashboard');
          } else {
            const errorData = await response.json();
            console.error('Failed to get user info:', errorData);
            setErrors({ general: 'Failed to get user information' });
          }
        } catch (error) {
          console.error('Error getting user info:', error);
          setErrors({ general: 'Failed to get user information' });
        }
      };
      
      getUserInfo();
    }
  }, [location, navigate]);

  const validateForm = () => {
    const newErrors = {};
    
    if (isLogin) {
      if (!loginData.email) newErrors.email = 'Email is required';
      if (!loginData.password) newErrors.password = 'Password is required';
    } else {
      if (!registerData.name) newErrors.name = 'Name is required';
      if (!registerData.email) newErrors.email = 'Email is required';
      if (!registerData.password) newErrors.password = 'Password is required';
      if (registerData.password !== registerData.confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match';
      }
      if (registerData.password.length < 6) {
        newErrors.password = 'Password must be at least 6 characters';
      }
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    setLoading(true);
    setErrors({});
    try {
      const result = await apiLogin(loginData);
      localStorage.setItem('token', result.access_token);
      localStorage.setItem('user', JSON.stringify(result.user));
      navigate('/dashboard');
    } catch (error) {
      setErrors({ general: error.message });
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    setLoading(true);
    setErrors({});
    try {
      await apiRegister(registerData);
      // After registration, auto-login
      const result = await apiLogin({ email: registerData.email, password: registerData.password });
      localStorage.setItem('token', result.access_token);
      localStorage.setItem('user', JSON.stringify(result.user));
      navigate('/dashboard');
    } catch (error) {
      setErrors({ general: error.message });
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setGoogleLoading(true);
    setErrors({});
    try {
      // Get Google OAuth URL from backend
      const response = await fetch('http://localhost:8000/api/v1/google-auth/login-url');
      const data = await response.json();
      
      if (data.success) {
        // Redirect to Google OAuth with prompt=select_account to force account picker
        let url = data.authorization_url;
        if (!url.includes('prompt=')) {
          url += (url.includes('?') ? '&' : '?') + 'prompt=select_account';
        }
        window.location.href = url;
      } else {
        setErrors({ general: 'Failed to get Google login URL' });
      }
    } catch (error) {
      setErrors({ general: 'Failed to initiate Google login' });
    } finally {
      setGoogleLoading(false);
    }
  };

  const switchMode = () => {
    setIsLogin(!isLogin);
    setErrors({});
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Email Bot</h1>
          <p>Manage your email campaigns efficiently</p>
        </div>
        
        <div className="auth-tabs">
          <button 
            className={`tab ${isLogin ? 'active' : ''}`}
            onClick={() => setIsLogin(true)}
          >
            Login
          </button>
          <button 
            className={`tab ${!isLogin ? 'active' : ''}`}
            onClick={() => setIsLogin(false)}
          >
            Register
          </button>
        </div>

        {errors.general && (
          <div className="error-message">
            {errors.general}
          </div>
        )}

        {isLogin ? (
          <>
            <form onSubmit={handleLogin} className="auth-form">
              <div className="form-group">
                <input
                  type="email"
                  placeholder="Email"
                  value={loginData.email}
                  onChange={(e) => setLoginData({...loginData, email: e.target.value})}
                  className={errors.email ? 'error' : ''}
                  disabled={loading}
                />
                {errors.email && <span className="error-text">{errors.email}</span>}
              </div>
              
              <div className="form-group password-group">
                <input
                  type={showLoginPassword ? "text" : "password"}
                  placeholder="Password"
                  value={loginData.password}
                  onChange={(e) => setLoginData({...loginData, password: e.target.value})}
                  className={errors.password ? 'error' : ''}
                  disabled={loading}
                />
                <span
                  className="password-toggle"
                  onClick={() => setShowLoginPassword(!showLoginPassword)}
                >
                  {showLoginPassword ? <FaEyeSlash /> : <FaEye />}
                </span>
                {errors.password && <span className="error-text">{errors.password}</span>}
              </div>
              
              <button type="submit" className={`auth-button${loading ? ' disabled' : ''}`} disabled={loading}>
                {loading ? 'Logging in...' : 'Login'}
              </button>
            </form>

            <div className="divider">
              <span>or</span>
            </div>

            <button 
              onClick={handleGoogleLogin} 
              className={`google-auth-button${googleLoading ? ' disabled' : ''}`} 
              disabled={googleLoading}
            >
              <FaGoogle />
              {googleLoading ? 'Connecting to Google...' : 'Sign in with Google'}
            </button>
          </>
        ) : (
          <form onSubmit={handleRegister} className="auth-form">
            <div className="form-group">
              <input
                type="text"
                placeholder="Full Name"
                value={registerData.name}
                onChange={(e) => setRegisterData({...registerData, name: e.target.value})}
                className={errors.name ? 'error' : ''}
                disabled={loading}
              />
              {errors.name && <span className="error-text">{errors.name}</span>}
            </div>
            
            <div className="form-group">
              <input
                type="email"
                placeholder="Email"
                value={registerData.email}
                onChange={(e) => setRegisterData({...registerData, email: e.target.value})}
                className={errors.email ? 'error' : ''}
                disabled={loading}
              />
              {errors.email && <span className="error-text">{errors.email}</span>}
            </div>
            
            <div className="form-group password-group">
              <input
                type={showRegisterPassword ? "text" : "password"}
                placeholder="Password"
                value={registerData.password}
                onChange={(e) => setRegisterData({...registerData, password: e.target.value})}
                className={errors.password ? 'error' : ''}
                disabled={loading}
              />
              <span
                className="password-toggle"
                onClick={() => setShowRegisterPassword(!showRegisterPassword)}
              >
                {showRegisterPassword ? <FaEyeSlash /> : <FaEye />}
              </span>
              {errors.password && <span className="error-text">{errors.password}</span>}
            </div>
            
            <div className="form-group password-group">
              <input
                type={showConfirmPassword ? "text" : "password"}
                placeholder="Confirm Password"
                value={registerData.confirmPassword}
                onChange={(e) => setRegisterData({...registerData, confirmPassword: e.target.value})}
                className={errors.confirmPassword ? 'error' : ''}
                disabled={loading}
              />
              <span
                className="password-toggle"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              >
                {showConfirmPassword ? <FaEyeSlash /> : <FaEye />}
              </span>
              {errors.confirmPassword && <span className="error-text">{errors.confirmPassword}</span>}
            </div>
            
            <button type="submit" className={`auth-button${loading ? ' disabled' : ''}`} disabled={loading}>
              {loading ? 'Registering...' : 'Register'}
            </button>
          </form>
        )}

        <div className="auth-footer">
          <p>
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button type="button" onClick={switchMode} className="switch-mode" disabled={loading}>
              {isLogin ? 'Register here' : 'Login here'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}

export default AuthPage; 