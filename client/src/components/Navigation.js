import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Navigation.css';
import { LogOut } from 'lucide-react';

function Navigation() {
  const [user, setUser] = useState(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Get user data from localStorage
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }

    // Listen for sidebar state changes
    const handleSidebarToggle = () => {
      setIsSidebarCollapsed(prev => !prev);
    };

    // Check for sidebar state in localStorage
    const sidebarState = localStorage.getItem('sidebarCollapsed');
    if (sidebarState) {
      setIsSidebarCollapsed(JSON.parse(sidebarState));
    }

    // Add event listener for sidebar toggle
    window.addEventListener('sidebarToggle', handleSidebarToggle);

    return () => {
      window.removeEventListener('sidebarToggle', handleSidebarToggle);
    };
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
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

  // Helper function to get user's display name
  const getUserDisplayName = () => {
    if (!user) return 'User';
    
    // Check for full_name first (from Google OAuth)
    if (user.full_name) return user.full_name;
    
    // Check for name field
    if (user.name) return user.name;
    
    // Check for first name from email (fallback)
    if (user.email) {
      const emailName = user.email.split('@')[0];
      // Capitalize first letter and replace dots/underscores with spaces
      return emailName
        .replace(/[._]/g, ' ')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    }
    
    return 'User';
  };

  return (
    <nav className="navigation">
      <div className={`nav-container ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        <div className="nav-brand">
          <h2>Email Bot</h2>
        </div>

        {/* Desktop Menu */}
        <div className="nav-menu desktop">
          {user && (
            <div className="nav-user-section">
              <div className="user-info" onClick={closeMobileMenu}>
                <div className="user-avatar">
                  {getUserInitials(user.email)}
                </div>
                <div className="user-details">
                  <div className="user-name">{getUserDisplayName()}</div>
                  <div className="user-email">{user.email}</div>
                </div>
                <span className="user-arrow">▼</span>
              </div>
              <button 
                className="nav-item logout" 
                onClick={handleLogout}
                title="Logout"
              >
                <LogOut size={20} className="nav-icon" />
                <span className="nav-label">Logout</span>
              </button>
            </div>
          )}
        </div>

        {/* Mobile Menu Button */}
        <button 
          className="mobile-menu-btn" 
          onClick={toggleMobileMenu}
          aria-label="Toggle mobile menu"
        >
          <div className={`hamburger ${isMobileMenuOpen ? 'open' : ''}`}></div>
        </button>

        {/* Mobile Menu */}
        <div className={`nav-menu mobile ${isMobileMenuOpen ? 'open' : ''}`}>
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
          <button 
            className="nav-item logout" 
            onClick={handleLogout}
          >
            <LogOut size={20} className="nav-icon" />
            <span className="nav-label">Logout</span>
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navigation; 