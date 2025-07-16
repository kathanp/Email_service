import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';

import './navbar.css';

function Navbar() {
  const [user, setUser] = useState(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const location = useLocation();

  useEffect(() => {
    // Get user data from localStorage
    const userData = localStorage.getItem('user');
    if (userData && userData !== 'null' && userData !== 'undefined') {
      try {
        setUser(JSON.parse(userData));
      } catch (error) {
        localStorage.removeItem('user');
      }
    }

    // Handle scroll effect
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  const getUserInitials = (email) => {
    if (!email) return 'U';
    return email.split('@')[0].substring(0, 2).toUpperCase();
  };

  const getUserDisplayName = () => {
    if (!user) return 'User';
    
    if (user.full_name) return user.full_name;
    if (user.name) return user.name;
    
    if (user.email) {
      const emailName = user.email.split('@')[0];
      return emailName
        .replace(/[._]/g, ' ')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    }
    
    return 'User';
  };

  const isActiveLink = (path) => {
    return location.pathname === path;
  };

  return (
    <>
      <nav className={`navbar ${isScrolled ? 'scrolled' : ''}`}>
        <div className="nav-container">
          
          {/* Brand Logo */}
          <Link to="/" className="nav-brand" onClick={closeMobileMenu}>
            <div className="logo-icon">
              <span>M</span>
            </div>
            <h2>MailsFlow</h2>
          </Link>

          {/* Desktop Navigation */}
          <div className="nav-menu desktop">
            <div className="nav-links">
              <Link to="/" className={`nav-link ${isActiveLink('/') ? 'active' : ''}`}>
                Home
              </Link>
              <Link to="/features" className={`nav-link ${isActiveLink('/features') ? 'active' : ''}`}>
                Features
              </Link>
              <Link to="/staticPricing" className={`nav-link ${isActiveLink('/staticPricing') ? 'active' : ''}`}>
                Pricing
              </Link>
              <Link to="/contact" className={`nav-link ${isActiveLink('/contact') ? 'active' : ''}`}>
                Contact
              </Link>
            </div>

            {/* User Section */}
            {user ? (
              <div className="nav-user-section">
                <div className="user-info">
                  <div className="user-avatar">
                    {getUserInitials(user.email)}
                  </div>
                  <div className="user-details">
                    <div className="user-name">{getUserDisplayName()}</div>
                    <div className="user-email">{user.email}</div>
                  </div>
                  <div className="user-dropdown-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
                
                <button 
                  onClick={handleLogout}
                  className="logout-btn"
                  title="Logout"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  <span>Logout</span>
                </button>
              </div>
            ) : (
              <Link to="/login" className="login-btn">
                <span>Login</span>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                </svg>
              </Link>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button 
            className={`mobile-menu-btn ${isMobileMenuOpen ? 'open' : ''}`}
            onClick={toggleMobileMenu}
            aria-label="Toggle mobile menu"
          >
            <div className="hamburger">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </button>
        </div>

        {/* Mobile Menu Overlay */}
        {isMobileMenuOpen && (
          <div 
            className="mobile-overlay"
            onClick={closeMobileMenu}
          />
        )}

        {/* Mobile Menu */}
        <div className={`mobile-menu ${isMobileMenuOpen ? 'open' : ''}`}>
          <div className="mobile-menu-content">
            
            {/* Mobile User Info */}
            {user && (
              <div className="mobile-user-info">
                <div className="user-info">
                  <div className="user-avatar">
                    {getUserInitials(user.email)}
                  </div>
                  <div className="user-details">
                    <div className="user-name">{getUserDisplayName()}</div>
                    <div className="user-email">{user.email}</div>
                  </div>
                </div>
              </div>
            )}

            {/* Mobile Navigation Links */}
            <div className="mobile-nav-links">
              <Link to="/" className={`mobile-nav-link ${isActiveLink('/') ? 'active' : ''}`} onClick={closeMobileMenu}>
                <span>Home</span>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
              <Link to="/features" className={`mobile-nav-link ${isActiveLink('/features') ? 'active' : ''}`} onClick={closeMobileMenu}>
                <span>Features</span>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
              <Link to="/staticPricing" className={`mobile-nav-link ${isActiveLink('/staticPricing') ? 'active' : ''}`} onClick={closeMobileMenu}>
                <span>Pricing</span>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
              <Link to="/contact" className={`mobile-nav-link ${isActiveLink('/contact') ? 'active' : ''}`} onClick={closeMobileMenu}>
                <span>Contact</span>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
              
              {!user && (
                <Link
                  to="/login"
                  className="mobile-nav-link login"
                  onClick={closeMobileMenu}
                >
                  <span>Login</span>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                  </svg>
                </Link>
              )}
            </div>

            {/* Mobile Logout Button */}
            {user && (
              <button 
                onClick={handleLogout}
                className="mobile-logout-btn"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                <span>Logout</span>
              </button>
            )}
          </div>
        </div>
      </nav>

      {/* Floating Action Button (when logged in) */}
      {user && (
        <div className="floating-actions">
          <button 
            className="fab main-fab"
            title="New Campaign"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          </button>
          
          <button 
            className="fab help-fab"
            title="Quick Help"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>
        </div>
      )}
    </>
  );
}

export default Navbar;