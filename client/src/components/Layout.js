import React from 'react';
import Navigation from './Navigation';
import Sidebar from './Sidebar';
import './Layout.css';

function Layout({ children }) {
  return (
    <div className="layout">
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