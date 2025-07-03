import React, { useState, useEffect } from 'react';
import { FaUpload, FaFileExcel, FaFilePdf, FaTrash, FaCog, FaDownload } from 'react-icons/fa';
import './FileManager.css';

const FileManager = () => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/files/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setFiles(data);
      } else {
        setError('Failed to fetch files');
      }
    } catch (error) {
      setError('Error fetching files');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      const allowedTypes = ['.xlsx', '.xls', '.pdf'];
      const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
      
      if (!allowedTypes.includes(fileExtension)) {
        setError('Please select a valid file type (Excel or PDF)');
        return;
      }

      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }

      setSelectedFile(file);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file to upload');
      return;
    }

    try {
      setUploading(true);
      setError('');

      const formData = new FormData();
      formData.append('file', selectedFile);
      if (description) {
        formData.append('description', description);
      }

      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/files/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        const uploadedFile = await response.json();
        setFiles([uploadedFile, ...files]);
        setSelectedFile(null);
        setDescription('');
        setError('');
        // Reset file input
        document.getElementById('file-input').value = '';
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Upload failed');
      }
    } catch (error) {
      setError('Error uploading file');
      console.error('Error:', error);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (fileId) => {
    if (!window.confirm('Are you sure you want to delete this file?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/files/${fileId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setFiles(files.filter(file => file.id !== fileId));
      } else {
        setError('Failed to delete file');
      }
    } catch (error) {
      setError('Error deleting file');
      console.error('Error:', error);
    }
  };

  const handleProcess = async (fileId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/files/${fileId}/process`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const result = await response.json();
        // Update the file in the list with processed status
        setFiles(files.map(file => 
          file.id === fileId 
            ? { ...file, processed: true, contacts_count: result.contacts_count }
            : file
        ));
        alert(`File processed successfully! Found ${result.contacts_count} contacts.`);
      } else {
        setError('Failed to process file');
      }
    } catch (error) {
      setError('Error processing file');
      console.error('Error:', error);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getFileIcon = (fileType) => {
    switch (fileType) {
      case 'excel':
        return <FaFileExcel className="file-icon excel" />;
      case 'pdf':
        return <FaFilePdf className="file-icon pdf" />;
      default:
        return <FaFileExcel className="file-icon" />;
    }
  };

  if (loading) {
    return (
      <div className="file-manager">
        <div className="loading">Loading files...</div>
      </div>
    );
  }

  return (
    <div className="file-manager">
      <div className="file-manager-header">
        <h1>File Manager</h1>
        <p>Upload and manage your contact files</p>
      </div>

      {/* Upload Section */}
      <div className="upload-section">
        <div className="upload-card">
          <div className="upload-area">
            <FaUpload className="upload-icon" />
            <h3>Upload Contact File</h3>
            <p>Supported formats: Excel (.xlsx, .xls) and PDF (.pdf)</p>
            <p>Maximum file size: 10MB</p>
            
            <div className="file-input-container">
              <input
                id="file-input"
                type="file"
                accept=".xlsx,.xls,.pdf"
                onChange={handleFileSelect}
                className="file-input"
              />
              <label htmlFor="file-input" className="file-input-label">
                Choose File
              </label>
            </div>

            {selectedFile && (
              <div className="selected-file">
                <p>Selected: {selectedFile.name}</p>
                <p>Size: {formatFileSize(selectedFile.size)}</p>
              </div>
            )}

            <div className="description-input">
              <input
                type="text"
                placeholder="File description (optional)"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="description-field"
              />
            </div>

            {error && <div className="error-message">{error}</div>}

            <button
              onClick={handleUpload}
              disabled={!selectedFile || uploading}
              className="upload-button"
            >
              {uploading ? 'Uploading...' : 'Upload File'}
            </button>
          </div>
        </div>
      </div>

      {/* Files List */}
      <div className="files-section">
        <h2>Your Files</h2>
        {files.length === 0 ? (
          <div className="no-files">
            <p>No files uploaded yet. Upload your first contact file to get started.</p>
          </div>
        ) : (
          <div className="files-grid">
            {files.map((file) => (
              <div key={file.id} className="file-card">
                <div className="file-header">
                  {getFileIcon(file.file_type)}
                  <div className="file-info">
                    <h4>{file.filename}</h4>
                    <p className="file-meta">
                      {formatFileSize(file.file_size)} • {file.file_type.toUpperCase()}
                    </p>
                  </div>
                </div>

                {file.description && (
                  <p className="file-description">{file.description}</p>
                )}

                <div className="file-details">
                  <p>Uploaded: {formatDate(file.upload_date)}</p>
                  {file.contacts_count !== null && (
                    <p>Contacts: {file.contacts_count}</p>
                  )}
                </div>

                <div className="file-status">
                  <span className={`status-badge ${file.processed ? 'processed' : 'pending'}`}>
                    {file.processed ? 'Processed' : 'Pending'}
                  </span>
                </div>

                <div className="file-actions">
                  {!file.processed && (
                    <button
                      onClick={() => handleProcess(file.id)}
                      className="action-button process"
                      title="Process file to extract contacts"
                    >
                      <FaCog /> Process
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(file.id)}
                    className="action-button delete"
                    title="Delete file"
                  >
                    <FaTrash /> Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default FileManager; 