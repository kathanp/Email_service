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
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  // New states for edit functionality
  const [isEditMode, setIsEditMode] = useState(false);
  const [newRecord, setNewRecord] = useState({});
  const [editedData, setEditedData] = useState(null);
  const [isUpdating, setIsUpdating] = useState(false);
  const [newColumn, setNewColumn] = useState('');
  const [newColumnData, setNewColumnData] = useState([]);
  // File renaming states
  const [editingFileId, setEditingFileId] = useState(null);
  const [editingFilename, setEditingFilename] = useState('');
  const [isRenamingFile, setIsRenamingFile] = useState(false);
  // Folder management states
  const [folders, setFolders] = useState([]);
  const [selectedFolder, setSelectedFolder] = useState(null); // null = show all files
  const [showCreateFolder, setShowCreateFolder] = useState(false);
  const [newFolderData, setNewFolderData] = useState({ name: '', description: '', color: '#007bff' });
  const [isCreatingFolder, setIsCreatingFolder] = useState(false);
  // Drag and drop states
  const [draggedFile, setDraggedFile] = useState(null);
  const [dragOverFolder, setDragOverFolder] = useState(null);
  // Folder navigation states
  const [folderPath, setFolderPath] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  // Helper function to format error messages
  const formatErrorMessage = (errorData) => {
    if (Array.isArray(errorData.detail)) {
      // Handle validation errors array
      return errorData.detail.map(err => `${err.loc?.join('.') || 'Field'}: ${err.msg}`).join(', ');
    } else if (typeof errorData.detail === 'string') {
      return errorData.detail;
    } else {
      return 'An error occurred';
    }
  };

  const fetchFiles = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('No authentication token found');
        return;
      }

      // Determine which endpoint to use based on selected folder
      let endpoint = `${API_ENDPOINTS.FILES}`;
      if (selectedFolder === 'uncategorized') {
        endpoint = `${API_ENDPOINTS.FILES}/uncategorized`;
      } else if (selectedFolder) {
        endpoint = `${API_ENDPOINTS.FILES}/folder/${selectedFolder}`;
      }

      const response = await fetch(endpoint, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setFiles(data || []); // Backend returns direct array
      } else if (response.status === 401) {
        setError('Authentication failed. Please log in again.');
        navigate('/login');
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(formatErrorMessage(errorData));
      }
    } catch (error) {
      setError('Network error loading files');
    } finally {
      setLoading(false);
    }
  }, [navigate, selectedFolder]);

  const fetchFolders = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await fetch(`${API_ENDPOINTS.BASE_URL}/api/folders`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setFolders(data || []);
      } else if (response.status === 401) {
        navigate('/login');
      }
    } catch (error) {
      // Error handled without console logging
    }
  }, [navigate]);

  useEffect(() => {
    fetchFiles();
    fetchFolders();
  }, [fetchFiles, fetchFolders]);

  // Folder management functions
  const handleCreateFolder = async () => {
    if (!newFolderData.name.trim()) {
      setError('Folder name is required');
      return;
    }

    setIsCreatingFolder(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('No authentication token found');
        return;
      }

      const response = await fetch(`${API_ENDPOINTS.BASE_URL}/api/folders`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newFolderData)
      });

      if (response.ok) {
        setSuccess('Folder created successfully!');
        setShowCreateFolder(false);
        setNewFolderData({ name: '', description: '', color: '#007bff' });
        fetchFolders();
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(formatErrorMessage(errorData));
      }
    } catch (error) {
      setError('Network error creating folder');
    } finally {
      setIsCreatingFolder(false);
    }
  };

  const handleDeleteFolder = async (folderId) => {
    if (!window.confirm('Are you sure you want to delete this folder? Files will be moved to uncategorized.')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('No authentication token found');
        return;
      }

      const response = await fetch(`${API_ENDPOINTS.BASE_URL}/api/folders/${folderId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setSuccess('Folder deleted successfully!');
        if (selectedFolder === folderId) {
          setSelectedFolder(null); // Switch to all files view
        }
        fetchFolders();
        fetchFiles();
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(formatErrorMessage(errorData));
      }
    } catch (error) {
      setError('Network error deleting folder');
    }
  };

  const handleMoveFileToFolder = async (fileId, folderId) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('No authentication token found');
        return;
      }

      let endpoint;
      if (folderId) {
        endpoint = `${API_ENDPOINTS.BASE_URL}/api/folders/${folderId}/files/${fileId}`;
      } else {
        endpoint = `${API_ENDPOINTS.BASE_URL}/api/folders/uncategorized/files/${fileId}`;
      }

      const response = await fetch(endpoint, {
        method: folderId ? 'PUT' : 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setSuccess('File moved successfully!');
        fetchFiles();
        fetchFolders(); // Update file counts
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(formatErrorMessage(errorData));
      }
    } catch (error) {
      setError('Network error moving file');
    }
  };

  // Drag and drop event handlers for file organization
  const handleFileDragStart = (e, file) => {
    setDraggedFile(file);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleFileDragEnd = () => {
    setDraggedFile(null);
    setDragOverFolder(null);
  };

  const handleFolderDragOver = (e, folderId) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverFolder(folderId);
  };

  const handleFolderDragLeave = () => {
    setDragOverFolder(null);
  };

  const handleFolderDrop = async (e, folderId) => {
    e.preventDefault();
    setDragOverFolder(null);
    
    if (draggedFile) {
      await handleMoveFileToFolder(draggedFile.id, folderId);
      setDraggedFile(null);
    }
  };

  // Enhanced folder navigation
  const handleFolderSelect = (folderId, folderName) => {
    setSelectedFolder(folderId);
    if (folderId && folderId !== 'uncategorized') {
      const newPath = [...folderPath];
      const existingIndex = newPath.findIndex(p => p.id === folderId);
      if (existingIndex >= 0) {
        // If folder already in path, truncate to that point
        setFolderPath(newPath.slice(0, existingIndex + 1));
      } else {
        // Add to path
        newPath.push({ id: folderId, name: folderName });
        setFolderPath(newPath);
      }
    } else {
      setFolderPath([]);
    }
  };

  const handleBreadcrumbClick = (index) => {
    if (index === -1) {
      // Clicked "All Files"
      setSelectedFolder(null);
      setFolderPath([]);
    } else {
      const folder = folderPath[index];
      setSelectedFolder(folder.id);
      setFolderPath(folderPath.slice(0, index + 1));
    }
  };

  // Filtered files based on search
  const filteredFiles = searchTerm 
    ? files.filter(file => 
        (file.filename || file.name || '').toLowerCase().includes(searchTerm.toLowerCase())
      )
    : files;

  // Color options for folder creation
  const folderColors = [
    '#007bff', '#28a745', '#dc3545', '#ffc107', '#17a2b8', 
    '#6f42c1', '#e83e8c', '#fd7e14', '#20c997', '#6c757d'
  ];

  const uploadFile = async (file) => {
    const token = localStorage.getItem('token');
    if (!token) {
      setError('No authentication token found');
      return;
    }

    // Validate file type
    const allowedTypes = ['.xlsx', '.xls', '.csv'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    if (!allowedTypes.includes(fileExtension)) {
      setError('Please upload only Excel (.xlsx, .xls) or CSV (.csv) files');
      return;
    }

    // Create FormData for multipart upload
    const formData = new FormData();
    formData.append('file', file);
    formData.append('description', 'Uploaded file');

    setUploading(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch(`${API_ENDPOINTS.FILES}/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
          // Don't set Content-Type, let browser set it with boundary for FormData
        },
        body: formData
      });

      if (response.ok) {
        await response.json();
        setSuccess(`File "${file.name}" uploaded successfully!`);
        fetchFiles(); // Refresh the file list
      } else if (response.status === 401) {
        setError('Authentication failed. Please log in again.');
        navigate('/login');
      } else {
        const errorData = await response.json();
        setError(formatErrorMessage(errorData));
      }
    } catch (error) {
      setError('Network error during upload');
    } finally {
      setUploading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    await uploadFile(file);
    // Reset the input
    event.target.value = '';
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    if (droppedFiles.length > 0) {
      uploadFile(droppedFiles[0]); // Upload the first file
    }
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
        setError(formatErrorMessage(errorData));
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
        setError(formatErrorMessage(errorData));
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
        // Ensure file_id is included in preview data
        const previewDataWithId = {
          ...data,
          file_id: fileId
        };
        setPreviewData(previewDataWithId);
        setShowPreview(true);
      } else if (response.status === 401) {
        setError('Authentication failed. Please log in again.');
        navigate('/login');
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(formatErrorMessage(errorData));
      }
    } catch (error) {
      setError('Network error previewing file');
    }
  };

  const closePreview = () => {
    setShowPreview(false);
    setPreviewData(null);
    // Reset edit mode states
    setIsEditMode(false);
    setNewRecord({});
    setEditedData(null);
    setIsUpdating(false);
    setNewColumn('');
    setNewColumnData([]);
  };

  // New edit mode functions
  const handleEditMode = () => {
    setIsEditMode(true);
    setEditedData({ ...previewData });
    
    // Reset new column states to allow adding more columns
    setNewColumn('');
    
    // Initialize newRecord with empty values based on table headers
    if (previewData.contacts && previewData.contacts.length > 0) {
      const headers = Object.keys(previewData.contacts[0]);
      const emptyRecord = {};
      headers.forEach(header => {
        emptyRecord[header] = '';
      });
      setNewRecord(emptyRecord);
    } else {
      // If no contacts exist, initialize with empty record
      setNewRecord({});
    }
    
    // Always initialize newColumnData for the new column inputs - ensure it matches contact count
    const contactsCount = previewData.contacts ? previewData.contacts.length : 0;
    setNewColumnData(new Array(contactsCount).fill(''));
  };

  const handleCancelEdit = () => {
    setIsEditMode(false);
    setNewRecord({});
    setEditedData(null);
    setNewColumn('');
    setNewColumnData([]);
  };

  const handleNewRecordChange = (field, value) => {
    setNewRecord(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleNewColumnChange = (rowIndex, value) => {
    setNewColumnData(prev => {
      const newData = [...prev];
      // Ensure the array is long enough to accommodate the rowIndex
      while (newData.length <= rowIndex) {
        newData.push('');
      }
      newData[rowIndex] = value;
      return newData;
    });
  };

  const handleAddRecord = () => {
    // Check if at least one field is filled (excluding the new column if it's empty)
    const recordToAdd = { ...newRecord };
    
    // If there's a new column being created but it's empty, don't include it
    if (newColumn && newColumn.trim() !== '' && (!newRecord[newColumn.trim()] || newRecord[newColumn.trim()].trim() === '')) {
      delete recordToAdd[newColumn.trim()];
    }
    
    const hasData = Object.values(recordToAdd).some(value => value && value.trim() !== '');
    
    if (!hasData) {
      setError('Please fill at least one field to add a record');
      return;
    }

    // Add the new record to the edited data
    const updatedContacts = [...editedData.contacts, recordToAdd];
    setEditedData(prev => ({
      ...prev,
      contacts: updatedContacts
    }));

    // Reset the new record form but keep the structure for existing columns
    const existingHeaders = editedData.contacts.length > 0 ? Object.keys(editedData.contacts[0]) : [];
    const emptyRecord = {};
    existingHeaders.forEach(header => {
      emptyRecord[header] = '';
    });
    
    // Add new column field if it exists
    if (newColumn && newColumn.trim() !== '') {
      emptyRecord[newColumn.trim()] = '';
    }
    
    setNewRecord(emptyRecord);
    
    // Add empty value to newColumnData for the new record
    setNewColumnData(prev => [...prev, '']);
    
    setSuccess('Record added! Click Update to save changes.');
  };

  const handleRemoveRecord = (recordIndex) => {
    // Remove the record from edited data
    const updatedContacts = editedData.contacts.filter((_, index) => index !== recordIndex);
    setEditedData(prev => ({
      ...prev,
      contacts: updatedContacts
    }));
    
    // Remove corresponding entry from newColumnData
    setNewColumnData(prev => prev.filter((_, index) => index !== recordIndex));
    
    setSuccess('Record removed! Click Update to save changes.');
  };

  const handleRemoveColumn = (columnName) => {
    // Remove the column from all contacts
    const updatedContacts = editedData.contacts.map(contact => {
      const newContact = { ...contact };
      delete newContact[columnName];
      return newContact;
    });

    // Update editedData
    setEditedData(prev => ({
      ...prev,
      contacts: updatedContacts
    }));

    // Remove from newRecord as well
    const updatedNewRecord = { ...newRecord };
    delete updatedNewRecord[columnName];
    setNewRecord(updatedNewRecord);

    setSuccess('Column removed! Click Update to save changes.');
  };

  const handleAddColumn = () => {
    if (!newColumn || newColumn.trim() === '') {
      setError('Please enter a column name');
      return;
    }

    // Check if column already exists
    const existingColumns = editedData.contacts.length > 0 ? Object.keys(editedData.contacts[0]) : [];
    if (existingColumns.includes(newColumn.trim())) {
      setError('Column already exists');
      return;
    }

    // Add new column to all existing contacts with data from newColumnData
    const updatedContacts = editedData.contacts.map((contact, index) => ({
      ...contact,
      [newColumn.trim()]: newColumnData[index] || ''
    }));

    // If no existing contacts, just update the newRecord structure

    // Update editedData
    setEditedData(prev => ({
      ...prev,
      contacts: updatedContacts
    }));

    // Ensure newRecord has the new column field (keep existing value if any)
    setNewRecord(prev => ({
      ...prev,
      [newColumn.trim()]: prev[newColumn.trim()] || ''
    }));

    setNewColumn('');
    setNewColumnData([]);
    setSuccess('Column added! Click Update to save changes.');
  };

  const handleUpdateFile = async () => {
    if (!editedData || !editedData.contacts) {
      setError('No data to update');
      return;
    }

    setIsUpdating(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('No authentication token found');
        return;
      }

      // Get the file ID from preview data
      const fileId = previewData.file_id;

      const response = await fetch(`${API_ENDPOINTS.FILES}/${fileId}/update`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          contacts: editedData.contacts
        })
      });

      if (response.ok) {
        const updatedData = await response.json();
        setPreviewData(updatedData);
        setIsEditMode(false);
        setNewRecord({});
        setEditedData(null);
        setNewColumn(''); // Reset new column name
        setNewColumnData([]); // Reset new column data
        setSuccess('File updated successfully!');
        
        // Refresh the files list to show updated info
        fetchFiles();
      } else if (response.status === 401) {
        setError('Authentication failed. Please log in again.');
        navigate('/login');
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(formatErrorMessage(errorData));
      }
    } catch (error) {
      setError('Network error updating file');
    } finally {
      setIsUpdating(false);
    }
  };

  const getFileStatusColor = (processed) => {
    return processed ? 'green' : 'orange';
  };

  const getFileStatusText = (processed) => {
    return processed ? 'Processed' : 'Not Processed';
  };

  // File renaming handlers
  const handleStartRename = (file) => {
    setEditingFileId(file.id);
    setEditingFilename(file.filename || file.name || 'Untitled File');
  };

  const handleCancelRename = () => {
    setEditingFileId(null);
    setEditingFilename('');
  };

  const handleSaveRename = async () => {
    if (!editingFilename.trim()) {
      setError('Filename cannot be empty');
      return;
    }

    setIsRenamingFile(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('No authentication token found');
        return;
      }

      const response = await fetch(`${API_ENDPOINTS.FILES}/${editingFileId}/rename`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ filename: editingFilename.trim() })
      });

      if (response.ok) {
        setSuccess('File renamed successfully!');
        setEditingFileId(null);
        setEditingFilename('');
        // Refresh the files list
        fetchFiles();
      } else if (response.status === 401) {
        setError('Authentication failed. Please log in again.');
        navigate('/login');
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(formatErrorMessage(errorData));
      }
    } catch (error) {
      setError('Network error renaming file');
    } finally {
      setIsRenamingFile(false);
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
      {/* Folder Sidebar */}
      <div className="folder-sidebar">
        <div className="folder-header">
          <h3>📁 Folders</h3>
          <button
            onClick={() => setShowCreateFolder(true)}
            className="btn-create-folder"
            title="Create new folder"
          >
            +
          </button>
        </div>

        <div className="folder-list">
          {/* All Files Option */}
          <div
            className={`folder-item ${selectedFolder === null ? 'active' : ''} ${dragOverFolder === null && draggedFile ? 'drag-over' : ''}`}
            onClick={() => handleFolderSelect(null, 'All Files')}
            onDragOver={(e) => handleFolderDragOver(e, null)}
            onDragLeave={handleFolderDragLeave}
            onDrop={(e) => handleFolderDrop(e, null)}
          >
            <span className="folder-icon" style={{ color: '#6c757d' }}>📄</span>
            <span className="folder-name">All Files</span>
            <span className="file-count">{files.length}</span>
          </div>

          {/* Uncategorized Option */}
          <div
            className={`folder-item ${selectedFolder === 'uncategorized' ? 'active' : ''} ${dragOverFolder === 'uncategorized' ? 'drag-over' : ''}`}
            onClick={() => handleFolderSelect('uncategorized', 'Uncategorized')}
            onDragOver={(e) => handleFolderDragOver(e, 'uncategorized')}
            onDragLeave={handleFolderDragLeave}
            onDrop={(e) => handleFolderDrop(e, null)}
          >
            <span className="folder-icon" style={{ color: '#adb5bd' }}>📂</span>
            <span className="folder-name">Uncategorized</span>
          </div>

          {/* User Folders */}
          {folders.map((folder) => (
            <div
              key={folder.id}
              className={`folder-item ${selectedFolder === folder.id ? 'active' : ''} ${dragOverFolder === folder.id ? 'drag-over' : ''}`}
              onClick={() => handleFolderSelect(folder.id, folder.name)}
              onDragOver={(e) => handleFolderDragOver(e, folder.id)}
              onDragLeave={handleFolderDragLeave}
              onDrop={(e) => handleFolderDrop(e, folder.id)}
            >
              <span className="folder-icon" style={{ color: folder.color }}>📁</span>
              <span className="folder-name">{folder.name}</span>
              <span className="file-count">{folder.file_count}</span>
              <div className="folder-actions">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteFolder(folder.id);
                  }}
                  className="btn-delete-folder"
                  title="Delete folder"
                >
                  🗑️
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Breadcrumb Navigation */}
        {(selectedFolder || folderPath.length > 0) && (
          <div className="breadcrumb-container">
            <nav className="breadcrumb">
              <button 
                className={`breadcrumb-item ${!selectedFolder ? 'active' : ''}`}
                onClick={() => handleBreadcrumbClick(-1)}
              >
                📁 All Files
              </button>
              {folderPath.map((folder, index) => (
                <React.Fragment key={folder.id}>
                  <span className="breadcrumb-separator">›</span>
                  <button 
                    className={`breadcrumb-item ${index === folderPath.length - 1 ? 'active' : ''}`}
                    onClick={() => handleBreadcrumbClick(index)}
                  >
                    {folder.name}
                  </button>
                </React.Fragment>
              ))}
              {selectedFolder === 'uncategorized' && (
                <>
                  <span className="breadcrumb-separator">›</span>
                  <span className="breadcrumb-item active">Uncategorized</span>
                </>
              )}
            </nav>
          </div>
        )}

        {/* Search Bar */}
        <div className="search-container">
          <input
            type="text"
            placeholder="Search files..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          {searchTerm && (
            <button 
              onClick={() => setSearchTerm('')}
              className="clear-search"
            >
              ✕
            </button>
          )}
        </div>

      {/* Enhanced File Upload with Drag & Drop */}
      <div className="file-upload-section">
        <div 
          className={`upload-drop-zone ${isDragOver ? 'drag-over' : ''} ${uploading ? 'uploading' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <div className="upload-content">
            <div className="upload-icon">
              {uploading ? (
                <div className="upload-spinner">⏳</div>
              ) : (
                <div className="upload-cloud">☁️</div>
              )}
            </div>
            <h3>
              {uploading ? 'Uploading...' : 
               isDragOver ? 'Drop your file here' : 
               'Upload your file here'}
            </h3>
            <p className="upload-subtitle">
              {uploading ? 'Please wait while we process your file' :
               'or click below to browse'}
            </p>
            <input
              type="file"
              id="file-upload"
              accept=".xlsx,.xls,.csv"
              onChange={handleFileUpload}
              disabled={uploading}
              style={{ display: 'none' }}
            />
            <label 
              htmlFor="file-upload" 
              className={`upload-button ${uploading ? 'disabled' : ''}`}
            >
              {uploading ? 'Uploading...' : 'Choose File'}
            </label>
            <p className="upload-hint">
              Supported formats: Excel (.xlsx, .xls), CSV (.csv)
            </p>
          </div>
        </div>
      </div>

      {/* Files List */}
      <div className="files-list">
        <h2>Your Files</h2>
          {!Array.isArray(filteredFiles) || filteredFiles.length === 0 ? (
          <div className="no-files">
              <p>No files found. {searchTerm ? 'Try a different search term or' : ''} Upload your first file above.</p>
          </div>
        ) : (
          <div className="files-grid">
              {filteredFiles.map((file) => (
                <div 
                  key={file.id} 
                  className={`file-card ${draggedFile?.id === file.id ? 'dragging' : ''}`}
                  draggable
                  onDragStart={(e) => handleFileDragStart(e, file)}
                  onDragEnd={handleFileDragEnd}
                >
                  <div className="file-info">
                    <div className="filename-section">
                      {editingFileId === file.id ? (
                        <div className="filename-edit">
                          <input
                            type="text"
                            value={editingFilename}
                            onChange={(e) => setEditingFilename(e.target.value)}
                            className="filename-input"
                            placeholder="Enter filename"
                            onKeyPress={(e) => e.key === 'Enter' && handleSaveRename()}
                            autoFocus
                          />
                          <div className="filename-edit-actions">
                            <button
                              onClick={handleSaveRename}
                              className="btn-save-filename"
                              disabled={isRenamingFile}
                            >
                              {isRenamingFile ? '⏳' : '✓'}
                            </button>
                            <button
                              onClick={handleCancelRename}
                              className="btn-cancel-filename"
                              disabled={isRenamingFile}
                            >
                              ✕
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div className="filename-display">
                  <h3>{file.filename || file.name || 'Untitled File'}</h3>
                          <button
                            onClick={() => handleStartRename(file)}
                            className="btn-edit-filename"
                            title="Rename file"
                          >
                            ✏️
                          </button>
                        </div>
                      )}
                    </div>
                  <p className="file-uploaded">
                    Uploaded: {new Date(file.upload_date || file.created_at || file.uploaded_at).toLocaleDateString()}
                  </p>
                  <div className="file-status">
                    <span 
                      className={`status-badge status-${getFileStatusColor(file.processed)}`}
                    >
                      {getFileStatusText(file.processed)}
                    </span>
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
                    
                    {/* Folder Assignment */}
                    <div className="folder-assignment">
                      <label htmlFor={`folder-${file.id}`}>Move to:</label>
                      <select
                        id={`folder-${file.id}`}
                        value={file.folder_id || 'uncategorized'}
                        onChange={(e) => {
                          const newFolderId = e.target.value === 'uncategorized' ? null : e.target.value;
                          handleMoveFileToFolder(file.id, newFolderId);
                        }}
                        className="folder-select"
                      >
                        <option value="uncategorized">Uncategorized</option>
                        {folders.map((folder) => (
                          <option key={folder.id} value={folder.id}>
                            📁 {folder.name}
                          </option>
                        ))}
                      </select>
                    </div>

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

        {/* Error/Success Messages */}
        {error && (
          <div className="alert alert-error">
            <span>❌ {error}</span>
            <button onClick={() => setError('')} className="alert-close">×</button>
          </div>
        )}
        
        {success && (
          <div className="alert alert-success">
            <span>✅ {success}</span>
            <button onClick={() => setSuccess('')} className="alert-close">×</button>
          </div>
        )}

      {/* Preview Modal */}
      {showPreview && previewData && (
        <div className="preview-modal-overlay" onClick={closePreview}>
          <div className="preview-modal" onClick={(e) => e.stopPropagation()}>
            <div className="preview-modal-header">
              <h3>File Preview</h3>
                <div className="preview-modal-actions">
                  {!isEditMode ? (
                    <button onClick={handleEditMode} className="btn-primary">
                      Edit
                    </button>
                  ) : (
                    <div className="edit-actions">
                      <button 
                        onClick={handleUpdateFile} 
                        className="btn-primary"
                        disabled={isUpdating}
                      >
                        {isUpdating ? 'Updating...' : 'Update'}
                      </button>
                      <button onClick={handleCancelEdit} className="btn-secondary">
                        Cancel
                      </button>
                    </div>
                  )}
              <button onClick={closePreview} className="close-button">×</button>
                </div>
            </div>
            <div className="preview-modal-content">
              <div className="preview-table-container">
                  {(isEditMode ? editedData : previewData).contacts && (isEditMode ? editedData : previewData).contacts.length > 0 ? (
                  <div>
                      <table className={`preview-table ${isEditMode ? 'edit-mode' : ''}`}>
                      <thead>
                        <tr>
                            {isEditMode && <th className="plus-header"></th>}
                            {(isEditMode ? editedData : previewData).contacts.length > 0 && Object.keys((isEditMode ? editedData : previewData).contacts[0]).map((header) => (
                              <th key={header} className={isEditMode ? 'editable-header' : ''}>
                                <div className="header-content">
                                  <span>{header.charAt(0).toUpperCase() + header.slice(1)}</span>
                                  {isEditMode && (
                                    <button 
                                      onClick={() => handleRemoveColumn(header)}
                                      className="delete-column-btn"
                                      title="Delete this column"
                                    >
                                      ×
                                    </button>
                                  )}
                                </div>
                              </th>
                            ))}
                            {/* Add new column input in edit mode - ALWAYS visible */}
                            {isEditMode && (
                              <th className="new-column-header">
                                <div className="add-column-container">
                                  <input
                                    type="text"
                                    value={newColumn}
                                    onChange={(e) => {
                                      const columnName = e.target.value;
                                      setNewColumn(columnName);
                                      
                                      // Ensure newColumnData array is properly sized
                                      const contactsCount = editedData.contacts ? editedData.contacts.length : 0;
                                      if (newColumnData.length !== contactsCount) {
                                        setNewColumnData(new Array(contactsCount).fill(''));
                                      }
                                    }}
                                    placeholder="New column name"
                                    className="new-column-input"
                                    onKeyPress={(e) => e.key === 'Enter' && handleAddColumn()}
                                  />
                                  <button 
                                    onClick={handleAddColumn}
                                    className="add-column-btn"
                                    title="Add new column"
                                    disabled={!newColumn || newColumn.trim() === ''}
                                  >
                                    +
                                  </button>
                                </div>
                              </th>
                            )}
                        </tr>
                      </thead>
                      <tbody>
                          {/* Add input row for new records when in edit mode */}
                          {isEditMode && Object.keys(newRecord).length > 0 && (
                            <tr className="new-record-row">
                              <td className="plus-indicator">
                                <span className="plus-sign">+</span>
                              </td>
                              {Object.keys(newRecord).map((header) => (
                                <td key={header}>
                                  <input
                                    type="text"
                                    value={newRecord[header]}
                                    onChange={(e) => handleNewRecordChange(header, e.target.value)}
                                    placeholder={`Enter ${header.toLowerCase()}`}
                                    className="new-record-input"
                                  />
                                </td>
                              ))}
                              {/* Add new column input for new record */}
                              {isEditMode && newColumn && newColumn.trim() !== '' && (
                                <td>
                                  <input
                                    type="text"
                                    value={newRecord[newColumn.trim()] || ''}
                                    onChange={(e) => handleNewRecordChange(newColumn.trim(), e.target.value)}
                                    placeholder={`Enter ${newColumn.toLowerCase()}`}
                                    className="new-record-input"
                                  />
                                </td>
                              )}
                              <td>
                                <button 
                                  onClick={handleAddRecord}
                                  className="add-record-btn"
                                  title="Add this record"
                                >
                                  ✓
                                </button>
                              </td>
                            </tr>
                          )}

                          {/* Existing records in edit mode */}
                          {(isEditMode ? editedData : previewData).contacts.map((contact, index) => (
                            <tr key={index} className={isEditMode ? 'editable-row' : ''}>
                              {isEditMode && (
                                <td className="remove-indicator">
                                  <button 
                                    onClick={() => handleRemoveRecord(index)}
                                    className="remove-record-btn"
                                    title="Remove this record"
                                  >
                                    ✕
                                  </button>
                                </td>
                              )}
                              {Object.entries(contact).map(([key, value]) => (
                                <td key={key}>
                                  {isEditMode ? (
                                    <input
                                      type="text"
                                      value={value || ''}
                                      onChange={(e) => {
                                        const updatedContacts = [...editedData.contacts];
                                        updatedContacts[index] = {
                                          ...updatedContacts[index],
                                          [key]: e.target.value
                                        };
                                        setEditedData(prev => ({
                                          ...prev,
                                          contacts: updatedContacts
                                        }));
                                      }}
                                      className="edit-input"
                                    />
                                  ) : (
                                    <span>{value || ''}</span>
                                  )}
                                </td>
                            ))}
                              {/* Add new column input for existing records */}
                              {isEditMode && newColumn && newColumn.trim() !== '' && (
                                <td>
                                  <input
                                    type="text"
                                    value={newColumnData[index] || ''}
                                    onChange={(e) => handleNewColumnChange(index, e.target.value)}
                                    placeholder={`Enter ${newColumn.toLowerCase()}`}
                                    className="edit-input"
                                  />
                                </td>
                              )}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                      
                      {/* Add more controls for edit mode */}
                      {isEditMode && (
                        <div className="edit-controls">
                          <p className="edit-hint">
                            ✨ Add new records, remove existing ones, or add new columns. Click Update when done!
                    </p>
                        </div>
                      )}
                  </div>
                ) : (
                    <div className="no-contacts">
                      <p>No contact data available for this file.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

        {/* Folder Creation Modal */}
        {showCreateFolder && (
          <div className="modal-overlay" onClick={() => setShowCreateFolder(false)}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h3>Create New Folder</h3>
                <button 
                  onClick={() => setShowCreateFolder(false)}
                  className="modal-close"
                >
                  ×
                </button>
              </div>
              <div className="modal-content">
                <div className="form-group">
                  <label htmlFor="folder-name">Folder Name *</label>
                  <input
                    id="folder-name"
                    type="text"
                    value={newFolderData.name}
                    onChange={(e) => setNewFolderData(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="Enter folder name"
                    className="form-input"
                    autoFocus
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="folder-description">Description</label>
                  <textarea
                    id="folder-description"
                    value={newFolderData.description}
                    onChange={(e) => setNewFolderData(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Enter folder description (optional)"
                    className="form-textarea"
                    rows="3"
                  />
                </div>
                
                <div className="form-group">
                  <label>Folder Color</label>
                  <div className="color-picker">
                    {folderColors.map((color) => (
                      <button
                        key={color}
                        className={`color-option ${newFolderData.color === color ? 'selected' : ''}`}
                        style={{ backgroundColor: color }}
                        onClick={() => setNewFolderData(prev => ({ ...prev, color }))}
                        title={color}
                      />
                    ))}
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button 
                  onClick={() => setShowCreateFolder(false)}
                  className="btn-secondary"
                  disabled={isCreatingFolder}
                >
                  Cancel
                </button>
                <button 
                  onClick={handleCreateFolder}
                  className="btn-primary"
                  disabled={isCreatingFolder || !newFolderData.name.trim()}
                >
                  {isCreatingFolder ? 'Creating...' : 'Create Folder'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default FileManager; 