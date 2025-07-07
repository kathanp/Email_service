import React, { useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../config';
import './FileManager.css';

function FileManager() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewData, setPreviewData] = useState(null);
  const [showPreview, setShowPreview] = useState(false);

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.FILES}/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setFiles(data);
      } else {
        setError('Failed to load files');
      }
    } catch (error) {
      setError('Network error loading files');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setError('');
    setSuccess('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.FILES}/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        setFiles(prev => [data, ...prev]);
        setSuccess('File uploaded successfully!');
        e.target.value = ''; // Clear the input
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to upload file');
      }
    } catch (error) {
      setError('Network error uploading file');
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteFile = async (fileId) => {
    if (!window.confirm('Are you sure you want to delete this file?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.FILES}/${fileId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setFiles(prev => prev.filter(file => file.id !== fileId));
        setSuccess('File deleted successfully!');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to delete file');
      }
    } catch (error) {
      setError('Network error deleting file');
    }
  };

  const handleProcessFile = async (fileId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.FILES}/${fileId}/process`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSuccess(`File processed successfully! Found ${data.total_contacts} contacts.`);
        // Refresh files to get updated status
        fetchFiles();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to process file');
      }
    } catch (error) {
      setError('Network error processing file');
    }
  };

  const handlePreviewFile = async (fileId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.FILES}/${fileId}/preview`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setPreviewData(data);
        setShowPreview(true);
      } else {
        const errorData = await response.json();
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

  const getFileStatusColor = (status) => {
    switch (status) {
      case 'processed':
        return 'green';
      case 'processing':
        return 'orange';
      case 'error':
        return 'red';
      default:
        return 'gray';
    }
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
            disabled={uploading}
            style={{ display: 'none' }}
          />
          <label htmlFor="file-upload" className="upload-button">
            {uploading ? 'Uploading...' : 'Choose File'}
          </label>
          <p className="upload-hint">
            Supported formats: Excel (.xlsx, .xls), CSV (.csv)
          </p>
        </div>
      </div>

      {/* Files List */}
      <div className="files-list">
        <h2>Your Files</h2>
        {files.length === 0 ? (
          <div className="no-files">
            <p>No files uploaded yet. Upload your first file above.</p>
          </div>
        ) : (
          <div className="files-grid">
            {files.map((file) => (
              <div key={file.id} className="file-card">
                <div className="file-info">
                  <h3>{file.filename}</h3>
                  <p className="file-size">{file.size} bytes</p>
                  <p className="file-uploaded">
                    Uploaded: {new Date(file.uploaded_at).toLocaleDateString()}
                  </p>
                  <div className="file-status">
                    <span 
                      className={`status-badge status-${getFileStatusColor(file.status)}`}
                    >
                      {file.status}
                    </span>
                    {file.total_contacts && (
                      <span className="contacts-count">
                        {file.total_contacts} contacts
                      </span>
                    )}
                  </div>
                </div>
                <div className="file-actions">
                  {file.status === 'uploaded' && (
                    <button
                      onClick={() => handleProcessFile(file.id)}
                      className="btn-secondary"
                    >
                      Process
                    </button>
                  )}
                  <button
                    onClick={() => handlePreviewFile(file.id)}
                    className="btn-secondary"
                  >
                    Preview
                  </button>
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
        <div className="preview-modal">
          <div className="preview-content">
            <div className="preview-header">
              <h3>File Preview</h3>
              <button onClick={closePreview} className="close-button">×</button>
            </div>
            <div className="preview-body">
              <div className="preview-info">
                <p><strong>Total Contacts:</strong> {previewData.total_contacts}</p>
                <p><strong>Columns:</strong> {previewData.columns.join(', ')}</p>
              </div>
              <div className="preview-table">
                <table>
                  <thead>
                    <tr>
                      {previewData.columns.map((column, index) => (
                        <th key={index}>{column}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {previewData.sample_data.map((row, rowIndex) => (
                      <tr key={rowIndex}>
                        {previewData.columns.map((column, colIndex) => (
                          <td key={colIndex}>{row[column] || ''}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default FileManager; 