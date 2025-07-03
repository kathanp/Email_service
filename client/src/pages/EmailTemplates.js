import React, { useState, useEffect } from 'react';
import './EmailTemplates.css';

function EmailTemplates() {
  const [templates, setTemplates] = useState([]);
  const [newTemplate, setNewTemplate] = useState({
    name: '',
    subject: '',
    body: ''
  });
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!newTemplate.name.trim() || !newTemplate.subject.trim() || !newTemplate.body.trim()) {
      setError('Please fill in all fields');
      return;
    }

    setIsSubmitting(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/templates/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name: newTemplate.name,
          subject: newTemplate.subject,
          body: newTemplate.body
        })
      });

      if (response.ok) {
        const createdTemplate = await response.json();
        setTemplates([createdTemplate, ...templates]);
        setNewTemplate({ name: '', subject: '', body: '' });
        setSuccess('Template created successfully!');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create template');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (templateId) => {
    if (!window.confirm('Are you sure you want to delete this template?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/templates/${templateId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setTemplates(templates.filter(template => template.id !== templateId));
        setSuccess('Template deleted successfully!');
      } else {
        setError('Failed to delete template');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
  };

  const fetchTemplates = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/templates/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setTemplates(data);
      } else {
        setError('Failed to load templates');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Get user data from localStorage
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }

    fetchTemplates();
  }, []);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (isLoading) {
    return (
      <div className="email-templates">
        <div className="loading">Loading templates...</div>
      </div>
    );
  }

  return (
    <div className="email-templates">
      <div className="templates-header">
        <h2>Email Templates</h2>
        <p>Create and manage your email templates for campaigns</p>
      </div>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <div className="template-form-container">
        <h3>Create New Template</h3>
        <form onSubmit={handleSubmit} className="template-form">
          <div className="form-group">
            <label htmlFor="templateName">Template Name *</label>
            <input
              id="templateName"
              type="text"
              placeholder="Enter template name"
              value={newTemplate.name}
              onChange={(e) => setNewTemplate({...newTemplate, name: e.target.value})}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="emailSubject">Email Subject *</label>
            <input
              id="emailSubject"
              type="text"
              placeholder="Enter email subject"
              value={newTemplate.subject}
              onChange={(e) => setNewTemplate({...newTemplate, subject: e.target.value})}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="emailBody">Email Body *</label>
            <textarea
              id="emailBody"
              placeholder="Enter email body content"
              value={newTemplate.body}
              onChange={(e) => setNewTemplate({...newTemplate, body: e.target.value})}
              rows="6"
              required
            />
          </div>
          
          <button type="submit" disabled={isSubmitting} className="save-button">
            {isSubmitting ? 'Saving...' : 'Save Template'}
          </button>
        </form>
      </div>

      <div className="templates-list-container">
        <h3>Your Templates ({templates.length})</h3>
        {templates.length === 0 ? (
          <div className="no-templates">
            <p>No templates created yet. Create your first template above!</p>
          </div>
        ) : (
          <div className="templates-grid">
            {templates.map((template) => (
              <div key={template.id} className="template-card">
                <div className="template-header">
                  <h4>{template.name}</h4>
                  <button
                    onClick={() => handleDelete(template.id)}
                    className="delete-button"
                    title="Delete template"
                  >
                    ×
                  </button>
                </div>
                <div className="template-content">
                  <p className="template-subject">
                    <strong>Subject:</strong> {template.subject}
                  </p>
                  <p className="template-body">
                    <strong>Body:</strong> {template.body.length > 100 
                      ? `${template.body.substring(0, 100)}...` 
                      : template.body}
                  </p>
                  <p className="template-date">
                    Created: {formatDate(template.created_at)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default EmailTemplates; 