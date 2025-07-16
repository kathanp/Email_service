// file name: Footer.js
import React from 'react';
import './Footer.css';

function Footer() {
  return (
    <footer className="app-footer">
      <div className="footer-content">
        <div className="footer-info">
          <div className="footer-bottom">
            <p>&copy; 2024 MailsFlow. All rights reserved.</p>
          </div>
          <div className="footer-social">
            <div className="social-links">
              <a href="https://facebook.com/mailsflow" target="_blank" rel="noopener noreferrer" className="social-link">
                <span className="social-icon">📘</span>
              </a>
              <a href="https://twitter.com/mailsflow" target="_blank" rel="noopener noreferrer" className="social-link">
                <span className="social-icon">🐦</span>
              </a>
              <a href="https://linkedin.com/company/mailsflow" target="_blank" rel="noopener noreferrer" className="social-link">
                <span className="social-icon">💼</span>
              </a>
              <a href="https://instagram.com/mailsflow" target="_blank" rel="noopener noreferrer" className="social-link">
                <span className="social-icon">📸</span>
              </a>
              <a href="https://youtube.com/mailsflow" target="_blank" rel="noopener noreferrer" className="social-link">
                <span className="social-icon">📺</span>
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer; 