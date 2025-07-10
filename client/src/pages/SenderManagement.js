import React, { useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../config';
import './SenderManagement.css';

function SenderManagement() {
  const [senders, setSenders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [newSender, setNewSender] = useState({ email: '', name: '' });
  const [isAdding, setIsAdding] = useState(false);

  useEffect(() => {
    fetchSenders();
  }, []);

  const fetchSenders = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.SENDERS}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setSenders(data.senders || []);
      } else {
        setError('Failed to load sender emails');
      }
    } catch (error) {
      setError('Network error loading sender emails');
    } finally {
      setLoading(false);
    }
  };

  const handleAddSender = async (e) => {
    e.preventDefault();
    if (!newSender.email || !newSender.name) {
      setError('Please fill in all fields');
      return;
    }

    setIsAdding(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.SENDERS}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newSender)
      });

      if (response.ok) {
        const data = await response.json();
        setSenders(prev => [...prev, data.sender]);
        setNewSender({ email: '', name: '' });
        setSuccess(data.message || 'Sender email added successfully! Verification email sent.');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to add sender email');
      }
    } catch (error) {
      setError('Network error adding sender email');
    } finally {
      setIsAdding(false);
    }
  };

  const handleDeleteSender = async (senderId) => {
    if (!window.confirm('Are you sure you want to delete this sender email?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.SENDERS}/${senderId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setSenders(prev => prev.filter(sender => sender.id !== senderId));
        setSuccess('Sender email deleted successfully!');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to delete sender email');
      }
    } catch (error) {
      setError('Network error deleting sender email');
    }
  };

  const handleSetDefault = async (senderId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.SENDERS}/${senderId}/set-default`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setSenders(prev => prev.map(sender => ({
          ...sender,
          is_default: sender.id === senderId
        })));
        setSuccess('Default sender email updated successfully!');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to set default sender email');
      }
    } catch (error) {
      setError('Network error setting default sender email');
    }
  };

  const handleVerifyStatus = async (senderId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.SENDERS}/${senderId}/verify`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSenders(prev => prev.map(sender => 
          sender.id === senderId 
            ? { ...sender, verification_status: data.verification_status }
            : sender
        ));
        setSuccess(data.message || 'Verification status updated!');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to check verification status');
      }
    } catch (error) {
      setError('Network error checking verification status');
    }
  };

  const handleResendVerification = async (senderId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.SENDERS}/${senderId}/resend-verification`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setSuccess('Verification email sent successfully!');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to resend verification email');
      }
    } catch (error) {
      setError('Network error resending verification email');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'verified':
        return 'green';
      case 'pending':
        return 'orange';
      case 'failed':
        return 'red';
      default:
        return 'gray';
    }
  };

  if (loading) {
    return (
      <div className="sender-management-container">
        <div className="loading">Loading sender emails...</div>
      </div>
    );
  }

  return (
    <div className="sender-management-container">
      <div className="sender-management-header">
        <h1>Sender Management</h1>
        <p>Manage your verified sender emails for sending campaigns</p>
      </div>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      {/* Add New Sender Form */}
      <div className="add-sender-form">
        <h2>Add New Sender Email</h2>
        <form onSubmit={handleAddSender}>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="senderName">Sender Name</label>
              <input
                type="text"
                id="senderName"
                value={newSender.name}
                onChange={(e) => setNewSender({ ...newSender, name: e.target.value })}
                placeholder="Enter sender name"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="senderEmail">Email Address</label>
              <input
                type="email"
                id="senderEmail"
                value={newSender.email}
                onChange={(e) => setNewSender({ ...newSender, email: e.target.value })}
                placeholder="Enter email address"
                required
              />
            </div>
            <button 
              type="submit" 
              className="btn-primary"
              disabled={isAdding}
            >
              {isAdding ? 'Adding...' : 'Add Sender'}
            </button>
          </div>
        </form>
      </div>

      {/* Senders List */}
      <div className="senders-list">
        <h2>Your Sender Emails</h2>
        {(!senders || senders.length === 0) ? (
          <div className="no-senders">
            <p>No sender emails added yet. Add your first sender email above.</p>
          </div>
        ) : (
          <div className="senders-grid">
            {Array.isArray(senders) && senders.map((sender) => (
              <div key={sender.id} className="sender-card">
                <div className="sender-info">
                  <h3>{sender.display_name || sender.email}</h3>
                  <p className="sender-email">{sender.email}</p>
                  <div className="sender-status">
                    <span 
                      className={`status-badge status-${getStatusColor(sender.verification_status)}`}
                    >
                      {sender.verification_status || 'unknown'}
                    </span>
                    {sender.is_default && (
                      <span className="default-badge">Default</span>
                    )}
                  </div>
                </div>
                <div className="sender-actions">
                  <button
                    onClick={() => handleVerifyStatus(sender.id)}
                    className="btn-secondary"
                    title="Check verification status"
                  >
                    Check Status
                  </button>
                  {sender.verification_status === 'verified' && !sender.is_default && (
                    <button
                      onClick={() => handleSetDefault(sender.id)}
                      className="btn-secondary"
                    >
                      Set as Default
                    </button>
                  )}
                  {sender.verification_status === 'pending' && (
                    <button
                      onClick={() => handleResendVerification(sender.id)}
                      className="btn-secondary"
                    >
                      Resend Verification
                    </button>
                  )}
                  {!sender.is_default && (
                    <button
                      onClick={() => handleDeleteSender(sender.id)}
                      className="btn-danger"
                    >
                      Delete
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default SenderManagement; 