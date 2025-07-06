import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './Sidebar.css';
import { Home, Users, Mail, File, Inbox, Settings, BarChart2 } from 'lucide-react';

function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const sidebarItems = [
    { path: '/dashboard', label: 'Dashboard', icon: Home },
    { path: '/files', label: 'Files', icon: File },
    { path: '/customers', label: 'Campaigns', icon: Users },
    { path: '/email-templates', label: 'Templates', icon: Mail },
    { path: '/sender-management', label: 'Senders', icon: Inbox },
    { path: '/pricing', label: 'Pricing', icon: BarChart2 },
    { path: '/reports', label: 'Reports', icon: BarChart2 },
    { path: '/settings', label: 'Settings', icon: Settings }
  ];

  const isActive = (path) => {
    return location.pathname === path;
  };

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  return (
    <div className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="sidebar-brand">
          {!isCollapsed && <h3>Email Bot</h3>}
        </div>
        <button className="sidebar-toggle" onClick={toggleSidebar}>
          {isCollapsed ? '→' : '←'}
        </button>
      </div>
      
      <nav className="sidebar-nav">
        {sidebarItems.map((item) => {
          const IconComponent = item.icon;
          return (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={`sidebar-item ${isActive(item.path) ? 'active' : ''}`}
              title={isCollapsed ? item.label : ''}
            >
              <span className="sidebar-icon">
                <IconComponent size={20} />
              </span>
              {!isCollapsed && <span className="sidebar-label">{item.label}</span>}
            </button>
          );
        })}
      </nav>
      
      <div className="sidebar-footer">
        {!isCollapsed && (
          <div className="sidebar-info">
            <p>Email Bot v1.0</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Sidebar; 