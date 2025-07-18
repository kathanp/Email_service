import React, { useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../config';
import './SenderManagement.css';

function SenderManagement() {
  const [senders, setSenders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [newSender, setNewSender] = useState({ email: '', display_name: '' });
  const [isAdding, setIsAdding] = useState(false);

  useEffect(() => {
    fetchSenders();
    
    // Set up automatic refresh every 5 seconds to check for verification updates
    const interval = setInterval(() => {
      fetchSenders();
    }, 500);  

    // Cleanup interval on component unmount
    return () => clearInterval(interval);
  }, []); // Empty dependency array, no 'ok' needed

  // Add function to manually verify sender
  const handleVerifySender = async (senderId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.SENDERS}/${senderId}/verify`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        await fetchSenders(); // Refresh the list to show updated status
        setSuccess('Email verified successfully!');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to verify email');
      }
    } catch (error) {
      setError('Network error verifying email');
    }
  };

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
        // Backend returns array directly, not wrapped in data.senders
        setSenders(Array.isArray(data) ? data : []);
        
        // Clear success message after 5 seconds
        if (success) {
          setTimeout(() => setSuccess(''), 5000);
        }
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
    if (!newSender.email || !newSender.display_name) {
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
        // Refresh the senders list instead of trying to add to existing array
        await fetchSenders();
        setNewSender({ email: '', display_name: '' });
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
      <h2>Sender Email Management</h2>
      
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <div className="add-sender-form">
        <div className="form-container">
          <div className="input-group">
            <label>Email:</label>
            <input
              type="email"
              value={newSender.email}
              onChange={(e) => setNewSender(prev => ({ ...prev, email: e.target.value }))}
              required
            />
          </div>
          <div className="input-group">
            <label>Display Name:</label>
            <input
              type="text"
              value={newSender.display_name}
              onChange={(e) => setNewSender(prev => ({ ...prev, display_name: e.target.value }))}
              required
            />
          </div>
          <button type="button" onClick={handleAddSender} disabled={isAdding} className="add-button">
            {isAdding ? 'Adding...' : 'Add Sender'}
          </button>
        </div>
      </div>

      <div className="senders-list">
        <h3>Your Sender Emails</h3>
        {senders.length === 0 ? (
          <p>No sender emails added yet.</p>
        ) : (
          <ul>
            {senders.map(sender => (
              <li key={sender.id} className={`sender-item ${sender.verification_status}`}>
                <div className="sender-info">
                  <strong>{sender.display_name}</strong>
                  <span className="email">{sender.email}</span>
                  <span className="status" style={{ color: getStatusColor(sender.verification_status) }}>
                    {sender.verification_status}
                  </span>
                  {sender.is_default && <span className="default-badge">Default</span>}
                </div>
                <div className="sender-actions">
                  {sender.verification_status === 'pending' && (
                    <button onClick={() => handleResendVerification(sender.id)}>
                      Resend Verification
                    </button>
                  )}
                  {sender.verification_status === 'verified' && !sender.is_default && (
                    <button onClick={() => handleSetDefault(sender.id)}>
                      Set as Default
                    </button>
                  )}
                  <button onClick={() => handleDeleteSender(sender.id)} className="delete">
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default SenderManagement; 