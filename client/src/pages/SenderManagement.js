import React, { useState, useEffect } from 'react';
import './SenderManagement.css';

function SenderManagement() {
  const [senders, setSenders] = useState([]);
  const [newSender, setNewSender] = useState({
    email: '',
    display_name: '',
    is_default: false
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const fetchSenders = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/senders/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSenders(data);
      } else {
        setError('Failed to load sender emails');
      }
    } catch (err) {
      setError('Network error loading sender emails');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!newSender.email.trim()) {
      setError('Please enter an email address');
      return;
    }

    setIsSubmitting(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/senders/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          email: newSender.email,
          display_name: newSender.display_name || newSender.email,
          is_default: newSender.is_default
        })
      });

      if (response.ok) {
        const result = await response.json();
        setSenders([result, ...senders]);
        setNewSender({ email: '', display_name: '', is_default: false });
        setSuccess(result.message);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to add sender email');
      }
    } catch (err) {
      setError('Network error adding sender email');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (senderId) => {
    if (!window.confirm('Are you sure you want to delete this sender email?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/senders/${senderId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setSenders(senders.filter(sender => sender.id !== senderId));
        setSuccess('Sender email deleted successfully!');
      } else {
        setError('Failed to delete sender email');
      }
    } catch (err) {
      setError('Network error deleting sender email');
    }
  };

  const handleSetDefault = async (senderId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/senders/${senderId}/set-default`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const result = await response.json();
        setSenders(senders.map(sender => ({
          ...sender,
          is_default: sender.id === senderId
        })));
        setSuccess(result.message);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to set default sender');
      }
    } catch (err) {
      setError('Network error setting default sender');
    }
  };

  const handleResendVerification = async (senderId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/senders/${senderId}/resend-verification`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const result = await response.json();
        setSuccess(result.message);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to resend verification');
      }
    } catch (err) {
      setError('Network error resending verification');
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'verified':
        return <span className="status-badge verified">✅ Verified</span>;
      case 'pending':
        return <span className="status-badge pending">⏳ Pending</span>;
      case 'failed':
        return <span className="status-badge failed">❌ Failed</span>;
      default:
        return <span className="status-badge unknown">❓ Unknown</span>;
    }
  };

  useEffect(() => {
    fetchSenders();
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
      <div className="sender-management">
        <div className="loading">Loading sender emails...</div>
      </div>
    );
  }

  return (
    <div className="sender-management-wrapper">
      <div className="sender-management">
        <div className="sender-header">
          <h2>Sender Email Management</h2>
          <p>Add and manage your verified sender emails for campaigns</p>
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        <div className="sender-form-container">
          <h3>Add New Sender Email</h3>
          <form onSubmit={handleSubmit} className="sender-form">
            <div className="form-group">
              <label htmlFor="senderEmail">Email Address *</label>
              <input
                id="senderEmail"
                type="email"
                placeholder="Enter email address (e.g., ceo@mycompany.com)"
                value={newSender.email}
                onChange={(e) => setNewSender({...newSender, email: e.target.value})}
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="displayName">Display Name (Optional)</label>
              <input
                id="displayName"
                type="text"
                placeholder="Enter display name (e.g., CEO, Marketing Team)"
                value={newSender.display_name}
                onChange={(e) => setNewSender({...newSender, display_name: e.target.value})}
              />
            </div>
            
            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={newSender.is_default}
                  onChange={(e) => setNewSender({...newSender, is_default: e.target.checked})}
                />
                Set as default sender
              </label>
            </div>
            
            <button type="submit" disabled={isSubmitting} className="save-button">
              {isSubmitting ? 'Adding...' : 'Add Sender Email'}
            </button>
          </form>
        </div>

        <div className="senders-list-container">
          <h3>Your Sender Emails ({senders.length})</h3>
          {senders.length === 0 ? (
            <div className="no-senders">
              <p>No sender emails added yet. Add your first sender email above!</p>
              <div className="info-box">
                <h4>How it works:</h4>
                <ol>
                  <li>Add your business email address</li>
                  <li>Check your email for the verification link</li>
                  <li>Click the verification link to verify your email</li>
                  <li>Once verified, you can use it to send campaigns</li>
                </ol>
              </div>
            </div>
          ) : (
            <div className="senders-grid">
              {senders.map((sender) => (
                <div key={sender.id} className={`sender-card ${sender.is_default ? 'default-sender' : ''}`}>
                  <div className="sender-header">
                    <h4>
                      {sender.display_name || sender.email}
                      {sender.is_default && <span className="default-badge">Default</span>}
                    </h4>
                    <div className="sender-actions">
                      {sender.verification_status === 'verified' && !sender.is_default && (
                        <button
                          onClick={() => handleSetDefault(sender.id)}
                          className="set-default-button"
                          title="Set as default"
                        >
                          ⭐
                        </button>
                      )}
                      {sender.verification_status === 'pending' && (
                        <button
                          onClick={() => handleResendVerification(sender.id)}
                          className="resend-button"
                          title="Resend verification email"
                        >
                          📧
                        </button>
                      )}
                      <button
                        onClick={() => handleDelete(sender.id)}
                        className="delete-button"
                        title="Delete sender email"
                      >
                        ×
                      </button>
                    </div>
                  </div>
                  <div className="sender-content">
                    <p className="sender-email">
                      <strong>Email:</strong> {sender.email}
                    </p>
                    <p className="sender-status">
                      <strong>Status:</strong> {getStatusBadge(sender.verification_status)}
                    </p>
                    <p className="sender-date">
                      Added: {formatDate(sender.created_at)}
                    </p>
                    {sender.verification_status === 'pending' && (
                      <div className="verification-info">
                        <p>📬 Check your email for the verification link</p>
                        <p>Click the link to verify this sender email</p>
                      </div>
                    )}
                    {sender.verification_status === 'verified' && (
                      <div className="verified-info">
                        <p>✅ This email is verified and ready to use</p>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default SenderManagement; 