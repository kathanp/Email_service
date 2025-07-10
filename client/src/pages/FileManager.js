import React, { useState, useEffect, useCallback } from 'react';
import { API_ENDPOINTS } from '../config';
import './FileManager.css';
import { useNavigate } from 'react-router-dom';

function FileManager() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [previewData, setPreviewData] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const navigate = useNavigate();

  const fetchFiles = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('No authentication token found');
        return;
      }

      const response = await fetch(`${API_ENDPOINTS.FILES}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setFiles(data.files || []); // Backend returns {files: [...]}
      } else if (response.status === 401) {
        setError('Authentication failed. Please log in again.');
        navigate('/login');
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.detail || 'Failed to load files');
      }
    } catch (error) {
      setError('Network error loading files');
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    fetchFiles();
  }, [fetchFiles]);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const token = localStorage.getItem('token');
    if (!token) {
      setError('No authentication token found');
      return;
    }

    // Read file content as base64
    const reader = new FileReader();
    reader.onload = async () => {
      const base64Data = reader.result.split(',')[1]; // Remove data URL prefix

    try {
      const response = await fetch(`${API_ENDPOINTS.FILES}/upload`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
          body: JSON.stringify({
            filename: file.name,
            file_size: file.size,
            file_type: file.type,
            file_data: base64Data
          })
      });

      if (response.ok) {
        setSuccess('File uploaded successfully!');
        fetchFiles(); // Refresh the file list
      } else if (response.status === 401) {
        setError('Authentication failed. Please log in again.');
        navigate('/login');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Upload failed');
      }
    } catch (error) {
      setError('Network error during upload');
    }
    };
    
    reader.onerror = () => {
      setError('Failed to read file');
    };
    
    reader.readAsDataURL(file);
  };

  const handleDeleteFile = async (fileId) => {
    if (!window.confirm('Are you sure you want to delete this file?')) {
      return;
    }

    const token = localStorage.getItem('token');
    if (!token) {
      setError('No authentication token found');
      return;
    }

    try {
      const response = await fetch(`${API_ENDPOINTS.FILES}/${fileId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setFiles(prev => prev.filter(file => file.id !== fileId));
        setSuccess('File deleted successfully!');
      } else if (response.status === 401) {
        setError('Authentication failed. Please log in again.');
        navigate('/login');
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.detail || 'Failed to delete file');
      }
    } catch (error) {
      setError('Network error deleting file');
    }
  };

  const handleProcessFile = async (fileId) => {
    const token = localStorage.getItem('token');
    if (!token) {
      setError('No authentication token found');
      return;
    }

    try {
      setSuccess('Processing file...');
      const response = await fetch(`${API_ENDPOINTS.FILES}/${fileId}/process`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSuccess(`File processed successfully! Found ${data.contacts_count || 0} contacts.`);
        // Refresh files to get updated status
        fetchFiles();
      } else if (response.status === 401) {
        setError('Authentication failed. Please log in again.');
        navigate('/login');
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.detail || 'Failed to process file');
      }
    } catch (error) {
      setError('Network error processing file');
    }
  };

  const handlePreviewFile = async (fileId) => {
    const token = localStorage.getItem('token');
    if (!token) {
      setError('No authentication token found');
      return;
    }

    try {
      const response = await fetch(`${API_ENDPOINTS.FILES}/${fileId}/preview`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setPreviewData(data);
        setShowPreview(true);
      } else if (response.status === 401) {
        setError('Authentication failed. Please log in again.');
        navigate('/login');
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.detail || 'Failed to preview file');
      }
    } catch (error) {
      setError('Network error previewing file');
    }
  };

  const closePreview = () => {
    setShowPreview(false);
    setPreviewData(null);
  };

  const getFileStatusColor = (processed) => {
    return processed ? 'green' : 'orange';
  };

  const getFileStatusText = (processed) => {
    return processed ? 'Processed' : 'Not Processed';
  };

  if (loading) {
    return (
      <div className="file-manager-container">
        <div className="loading">Loading files...</div>
      </div>
    );
  }

  return (
    <div className="file-manager-container">
        <div className="file-manager-header">
          <h1>File Manager</h1>
        <p>Upload and manage your contact lists</p>
        </div>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      {/* File Upload */}
      <div className="file-upload-section">
        <h2>Upload New File</h2>
          <div className="upload-area">
              <input
                type="file"
            id="file-upload"
            accept=".xlsx,.xls,.csv"
            onChange={handleFileUpload}
            disabled={false}
            style={{ display: 'none' }}
          />
          <label htmlFor="file-upload" className="upload-button">
            Choose File
              </label>
          <p className="upload-hint">
            Supported formats: Excel (.xlsx, .xls), CSV (.csv)
          </p>
        </div>
      </div>

      {/* Files List */}
      <div className="files-list">
        <h2>Your Files</h2>
        {!Array.isArray(files) || files.length === 0 ? (
          <div className="no-files">
            <p>No files uploaded yet. Upload your first file above.</p>
          </div>
        ) : (
          <div className="files-grid">
            {files.map((file) => (
              <div key={file.id} className="file-card">
                  <div className="file-info">
                  <h3>{file.filename || file.name || 'Untitled File'}</h3>
                  <p className="file-size">{(file.file_size || file.size || 0).toLocaleString()} bytes</p>
                  <p className="file-uploaded">
                    Uploaded: {new Date(file.upload_date || file.created_at || file.uploaded_at).toLocaleDateString()}
                  </p>
                  <div className="file-status">
                    <span 
                      className={`status-badge status-${getFileStatusColor(file.processed)}`}
                    >
                      {getFileStatusText(file.processed)}
                    </span>
                    {file.contacts_count && file.processed && (
                      <span className="contacts-count">
                        {file.contacts_count} contacts
                      </span>
                    )}
                  </div>
                </div>
                <div className="file-actions">
                  {!file.processed && (
                    <button
                      onClick={() => handleProcessFile(file.id)}
                      className="btn-primary"
                    >
                      Process File
                    </button>
                  )}
                  {file.processed && (
                    <button
                      onClick={() => handlePreviewFile(file.id)}
                      className="btn-secondary"
                    >
                      Preview
                    </button>
                  )}
                  <button
                    onClick={() => handleDeleteFile(file.id)}
                    className="btn-danger"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Preview Modal */}
      {showPreview && previewData && (
        <div className="preview-modal-overlay" onClick={closePreview}>
          <div className="preview-modal" onClick={(e) => e.stopPropagation()}>
            <div className="preview-modal-header">
              <h3>File Preview</h3>
              <button onClick={closePreview} className="close-button">×</button>
            </div>
            <div className="preview-modal-content">
              <div className="preview-table-container">
                {previewData.contacts && previewData.contacts.length > 0 ? (
                  <div>
                    <table className="preview-table">
                      <thead>
                        <tr>
                          {Object.keys(previewData.contacts[0]).map((header) => (
                            <th key={header}>{header.charAt(0).toUpperCase() + header.slice(1)}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {previewData.contacts.slice(0, 50).map((contact, rowIndex) => (
                          <tr key={rowIndex}>
                            {Object.values(contact).map((value, colIndex) => (
                              <td key={colIndex}>{value || ''}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {previewData.contacts.length > 50 && (
                      <p className="preview-note">
                        Showing first 50 contacts out of {previewData.contacts.length} total contacts
                      </p>
                    )}
                  </div>
                ) : (
                  <div className="no-preview-data">
                    <p>No preview data available</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default FileManager; 