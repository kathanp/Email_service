import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './Navigation.css';

function Navigation() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [user, setUser] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/files', label: 'Files', icon: '📁' },
    { path: '/customers', label: 'Customers', icon: '👥' },
    { path: '/email-templates', label: 'Templates', icon: '📝' },
    { path: '/reports', label: 'Reports', icon: '📈' },
    { path: '/settings', label: 'Settings', icon: '⚙️' }
  ];

  useEffect(() => {
    // Get user data from localStorage
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  const isActive = (path) => {
    return location.pathname === path;
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <nav className="navigation">
      <div className="nav-container">
        <div className="nav-brand">
          <h2>Email Bot</h2>
        </div>

        {/* Desktop Navigation */}
        <div className="nav-menu desktop">
          {navItems.map((item) => (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={`nav-item ${isActive(item.path) ? 'active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </button>
          ))}
          
          {/* User Info and Logout - Desktop */}
          <div className="nav-user-section">
            <div className="user-info">
              <span className="user-avatar">
                {user?.name ? user.name.charAt(0).toUpperCase() : 'U'}
              </span>
              <span className="user-email">{user?.email || 'User'}</span>
            </div>
            <button onClick={handleLogout} className="nav-item logout">
              <span className="nav-icon">🚪</span>
              <span className="nav-label">Logout</span>
            </button>
          </div>
        </div>

        {/* Mobile Menu Button */}
        <button 
          className="mobile-menu-btn"
          onClick={toggleMobileMenu}
          aria-label="Toggle mobile menu"
        >
          <span className={`hamburger ${isMobileMenuOpen ? 'open' : ''}`}></span>
        </button>

        {/* Mobile Navigation */}
        <div className={`nav-menu mobile ${isMobileMenuOpen ? 'open' : ''}`}>
          {/* User Info - Mobile */}
          <div className="mobile-user-info">
            <div className="user-info">
              <span className="user-avatar">
                {user?.name ? user.name.charAt(0).toUpperCase() : 'U'}
              </span>
              <div className="user-details">
                <span className="user-name">{user?.name || 'User'}</span>
                <span className="user-email">{user?.email || 'user@example.com'}</span>
              </div>
            </div>
          </div>
          
          {navItems.map((item) => (
            <button
              key={item.path}
              onClick={() => {
                navigate(item.path);
                setIsMobileMenuOpen(false);
              }}
              className={`nav-item ${isActive(item.path) ? 'active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </button>
          ))}
          <button onClick={handleLogout} className="nav-item logout">
            <span className="nav-icon">🚪</span>
            <span className="nav-label">Logout</span>
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navigation; 