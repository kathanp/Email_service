import React, { useState, useEffect } from 'react';
import Navigation from './Navigation';
import Sidebar from './Sidebar';
import './Layout.css';
import { Rocket } from 'lucide-react';

function Layout({ children }) {
  const [showTopSection, setShowTopSection] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowTopSection(false);
    }, 15000); // 15 seconds

    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="layout">
      {/* Top Section - Above Navbar */}
      {showTopSection && (
        <div className="top-section">
          <div className="top-content">
            <div className="top-message">
              <Rocket size={18} className="top-icon" />
              <span className="top-text">Welcome to Email Bot - Your Professional Email Campaign Solution</span>
            </div>
            <div className="top-actions">
              <button className="top-action-btn" onClick={() => window.location.href = '/pricing'}>
                View Plans
              </button>
            </div>
          </div>
        </div>
      )}
      
      <Navigation />
      <div className="content-wrapper">
        <Sidebar />
        <div className="main-content">
          <div className="page-content">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Layout; 