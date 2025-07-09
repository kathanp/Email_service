import React, { useState, useEffect, useCallback } from 'react';
import { API_ENDPOINTS } from '../config';
import './CustomerManager.css';
import { useNavigate } from 'react-router-dom';

function AutonomousCampaign() {
  const [files, setFiles] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [senders, setSenders] = useState([]);
  const [selectedFile, setSelectedFile] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [selectedSender, setSelectedSender] = useState('');
  const [campaignName, setCampaignName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [previewData, setPreviewData] = useState(null);
  const [validationData, setValidationData] = useState(null);
  const [showValidationModal, setShowValidationModal] = useState(false);
  const [campaignStatus, setCampaignStatus] = useState(null);
  const [showLiveStatus, setShowLiveStatus] = useState(false);
  const statusIntervalRef = useRef(null);
  const [recentCampaigns, setRecentCampaigns] = useState([]);
  const [campaignsLoading, setCampaignsLoading] = useState(true);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'tile'
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
        setFiles(data || []);
      } else if (response.status === 401) {
        setError('Authentication failed. Please log in again.');
        navigate('/login');
      } else {
        setError('Failed to load files');
      }
    } catch (error) {
      setError('Network error loading files');
    }
  }, [navigate]);

  useEffect(() => {
    fetchFiles();
    fetchTemplates();
    fetchSenders();
    fetchRecentCampaigns();
    
    // Cleanup function to stop polling when component unmounts
    return () => {
      if (statusIntervalRef.current) {
        clearInterval(statusIntervalRef.current);
      }
    };
  }, []); // Empty dependency array to run only once on mount

  useEffect(() => {
    fetchFiles();
  }, [fetchFiles]);

  const fetchTemplates = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.TEMPLATES}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setTemplates(data || []); // Backend returns templates array directly
      } else {
        setError('Failed to load templates');
      }
    } catch (err) {
      setError('Network error loading templates');
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
        setSenders(data || []); // Backend returns senders array directly
        
        // Auto-select default sender if available
        const defaultSender = data && data.find(sender => sender.is_default && sender.verification_status === 'verified');
        if (defaultSender) {
          setSelectedSender(defaultSender.id);
        }
      } else {
        setError('Failed to load sender emails');
      }
    } catch (err) {
      setError('Network error loading sender emails');
    }
  };

  const validateTemplate = async () => {
    if (!selectedFile || !selectedTemplate) {
      setError('Please select both a file and template for validation');
      return;
    }

    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.CAMPAIGNS}/validate-template`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          file_id: selectedFile,
          template_id: selectedTemplate
        })
      });

      if (response.ok) {
        const data = await response.json();
        setValidationData(data);
        setShowValidationModal(true);
        
        if (data.is_valid) {
          setSuccess('Template validation successful! You can now send your campaign.');
        } else {
          setError('Template validation failed! Please check the details below.');
        }
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to validate template');
      }
    } catch (err) {
      setError('Network error validating template');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePreview = async () => {
    if (!selectedFile || !selectedTemplate) {
      setError('Please select both a file and template');
      return;
    }

    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.CAMPAIGNS}/preview`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          file_id: selectedFile,
          template_id: selectedTemplate
        })
      });

      if (response.ok) {
        const data = await response.json();
        setPreviewData(data);
        setSuccess('Preview generated successfully!');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to generate preview');
      }
    } catch (err) {
      setError('Network error generating preview');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendCampaign = async () => {
    if (!selectedFile || !selectedTemplate || !campaignName || !selectedSender) {
      setError('Please fill in all required fields');
      return;
    }

    // Check if template has been validated
    if (!validationData || !validationData.is_valid) {
      setError('Please validate your template first before sending the campaign');
      return;
    }

    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.CAMPAIGNS}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name: campaignName,
          file_id: selectedFile,
          template_id: selectedTemplate,
          sender_id: selectedSender
        })
      });

      if (response.ok) {
        const data = await response.json();
        setSuccess(`Campaign "${campaignName}" started successfully!`);
        
        // Start polling for status updates
        if (data.id) {
        startLiveStatusPolling(data.id);
        }
        
        // Reset form
        setCampaignName('');
        setSelectedFile('');
        setSelectedTemplate('');
        setValidationData(null);
        
        // Refresh campaigns list
        fetchRecentCampaigns();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to start campaign');
      }
    } catch (err) {
      setError('Network error starting campaign');
    } finally {
      setIsLoading(false);
    }
  };

  const closeValidationModal = () => {
    setShowValidationModal(false);
    // Don't clear validationData - keep it so the user can send the campaign
  };

  const startLiveStatusPolling = (campaignId) => {
    setShowLiveStatus(true);
    setCampaignStatus({
      status: 'sending',
      total_emails: 0,
      successful: 0,
      failed: 0,
      progress_percentage: 0
    });

    const interval = setInterval(async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_ENDPOINTS.CAMPAIGNS}/${campaignId}/status`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          const status = await response.json();
          setCampaignStatus(status);
          
          // Stop polling if campaign is completed
          if (status.status === 'completed' || status.status === 'failed') {
            clearInterval(interval);
            statusIntervalRef.current = null;
          }
        }
      } catch (error) {
        // console.error('Error fetching campaign status:', error); // Removed as per edit hint
      }
    }, 2000); // Poll every 2 seconds

    statusIntervalRef.current = interval;
  };

  const stopLiveStatusPolling = () => {
    if (statusIntervalRef.current) {
      clearInterval(statusIntervalRef.current);
      statusIntervalRef.current = null;
    }
    setShowLiveStatus(false);
    setCampaignStatus(null);
  };

  const fetchRecentCampaigns = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.STATS}/campaigns`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setRecentCampaigns(data.campaigns || []); // Extract campaigns array from response
      } else {
        setError('Failed to load recent campaigns');
      }
    } catch (error) {
      setError('Network error loading recent campaigns');
    } finally {
      setCampaignsLoading(false);
    }
  };

  const getCampaignStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return '✅';
      case 'sending':
        return '📤';
      case 'failed':
        return '❌';
      case 'pending':
        return '⏳';
      default:
        return '📧';
    }
  };

  const getCampaignStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return '#10b981';
      case 'sending':
        return '#3b82f6';
      case 'failed':
        return '#ef4444';
      case 'pending':
        return '#f59e0b';
      default:
        return '#6b7280';
    }
  };

  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return `${minutes}m ${remainingSeconds}s`;
  };

  return (
    <div className="customer-manager-wrapper">
    <div className="customer-manager">
        <div className="campaign-header">
          <h2>Autonomous Email Campaign</h2>
          <p>Select your contact file and email template to send mass emails</p>
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        <div className="campaign-form">
          <div className="form-section">
            <h3>Campaign Configuration</h3>
            
            <div className="form-group">
              <label htmlFor="campaignName">Campaign Name *</label>
        <input
                id="campaignName"
          type="text"
                placeholder="Enter campaign name"
                value={campaignName}
                onChange={(e) => setCampaignName(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="senderSelect">Sender Email *</label>
              <select
                id="senderSelect"
                value={selectedSender}
                onChange={(e) => setSelectedSender(e.target.value)}
                required
              >
                <option value="">Select a sender email</option>
                {Array.isArray(senders) && senders.map((sender) => (
                  <option key={sender.id} value={sender.id}>
                    {sender.display_name || sender.email} 
                    {sender.verification_status === 'verified' ? ' ✅' : 
                     sender.verification_status === 'pending' ? ' ⏳' : ' ❌'}
                    {sender.is_default ? ' (Default)' : ''}
                  </option>
                ))}
              </select>
              {(!senders || senders.length === 0) && (
                <div className="sender-info">
                  <p>No sender emails found. <a href="/sender-management">Add a sender email</a> first.</p>
                </div>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="fileSelect">Contact File *</label>
              <select
                id="fileSelect"
                value={selectedFile}
                onChange={(e) => setSelectedFile(e.target.value)}
                required
              >
                <option value="">Select a contact file</option>
                {Array.isArray(files) && files.map((file) => (
                  <option key={file.id} value={file.id}>
                    {file.filename} ({file.contacts_count || 0} contacts)
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="templateSelect">Email Template *</label>
              <select
                id="templateSelect"
                value={selectedTemplate}
                onChange={(e) => setSelectedTemplate(e.target.value)}
                required
              >
                <option value="">Select an email template</option>
                {Array.isArray(templates) && templates.map((template) => (
                  <option key={template.id} value={template.id}>
                    {template.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-actions">
            <button
              type="button"
              onClick={validateTemplate}
              disabled={isLoading || !selectedFile || !selectedTemplate}
              className={`preview-button ${validationData && validationData.is_valid ? 'validated' : ''}`}
            >
              {isLoading ? 'Validating Template...' : 
               validationData && validationData.is_valid ? '✅ Template Validated' : 'Validate Template'}
            </button>
            
            <button
              type="button"
              onClick={handlePreview}
              disabled={isLoading || !selectedFile || !selectedTemplate}
              className="preview-button"
            >
              {isLoading ? 'Generating Preview...' : 'Preview Campaign'}
            </button>
            
            <button
              type="button"
              onClick={handleSendCampaign}
              disabled={isLoading || !selectedFile || !selectedTemplate || !campaignName || !selectedSender || !validationData || !validationData.is_valid}
              className={`send-button ${validationData && validationData.is_valid && campaignName && selectedSender ? 'ready' : ''}`}
            >
              {isLoading ? 'Sending Campaign...' : 
               !validationData || !validationData.is_valid ? 'Validate Template First' :
               !campaignName ? 'Enter Campaign Name' :
               !selectedSender ? 'Select Sender Email' : '🚀 Send Campaign'}
            </button>
          </div>
        </div>

        {previewData && (
          <div className="preview-section">
            <h3>Campaign Preview</h3>
            <div className="preview-content">
              <div className="preview-info">
                <p><strong>Recipients:</strong> {previewData.recipients_count}</p>
                <p><strong>Template:</strong> {previewData.template_name}</p>
                <p><strong>Subject:</strong> {previewData.subject}</p>
              </div>
              <div className="preview-email">
                <h4>Email Preview:</h4>
                <div className="email-preview" dangerouslySetInnerHTML={{ __html: previewData.body }} />
              </div>
            </div>
          </div>
        )}

        {showLiveStatus && campaignStatus && (
          <div className="live-status-modal">
            <div className="modal-content">
              <h3>Campaign Progress</h3>
              
              <div className="campaign-status">
                <div className="status-header">
                  <span className={`status-badge ${campaignStatus.status}`}>
                    {campaignStatus.status === 'sending' ? '📤 Sending...' : 
                     campaignStatus.status === 'completed' ? '✅ Completed' : 
                     campaignStatus.status === 'failed' ? '❌ Failed' : '⏳ Pending'}
                  </span>
                </div>
                
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${campaignStatus.progress_percentage}%` }}
                  ></div>
                </div>
                
                <div className="status-stats">
                  <div className="stat-item">
                    <span className="stat-label">Total Emails:</span>
                    <span className="stat-value">{campaignStatus.total_emails}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Successful:</span>
                    <span className="stat-value success">{campaignStatus.successful}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Failed:</span>
                    <span className="stat-value failed">{campaignStatus.failed}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Progress:</span>
                    <span className="stat-value">{Math.round(campaignStatus.progress_percentage)}%</span>
                  </div>
                </div>
                
                {campaignStatus.duration && (
                  <div className="duration-info">
                    <p>Duration: {Math.round(campaignStatus.duration)} seconds</p>
                  </div>
                )}
              </div>
              
              <div className="modal-actions">
                <button onClick={stopLiveStatusPolling} className="close-button">
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {showValidationModal && validationData && (
          <div className="validation-modal">
            <div className="modal-content">
              <h3>Template Validation Results</h3>
              
              <div className="validation-status">
                <p className={`status ${validationData.is_valid ? 'valid' : 'invalid'}`}>
                  <strong>Status:</strong> {validationData.is_valid ? '✅ Valid' : '❌ Invalid'}
                </p>
                <p className="validation-message">{validationData.validation_message}</p>
              </div>

              <div className="validation-details">
                <div className="detail-section">
                  <h4>Template Variables Found:</h4>
                  <div className="variables-list">
                    {validationData.template_variables && validationData.template_variables.length > 0 ? (
                      validationData.template_variables.map((variable, index) => (
                        <span key={index} className="variable-tag">{variable}</span>
                      ))
                    ) : (
                      <p>No template variables found</p>
                    )}
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Available Columns in Contact File:</h4>
                  <div className="columns-list">
                    {validationData.available_columns && validationData.available_columns.map((column, index) => (
                      <span key={index} className="column-tag">{column}</span>
                    ))}
                  </div>
                </div>

                {validationData.missing_variables && validationData.missing_variables.length > 0 && (
                  <div className="detail-section error">
                    <h4>Missing Variables:</h4>
                    <div className="missing-variables">
                      {validationData.missing_variables.map((variable, index) => (
                        <span key={index} className="variable-tag missing">{variable}</span>
                      ))}
                    </div>
                    <p className="error-message">
                      These variables are used in your template but not found in your contact file. 
                      Please either:
                    </p>
                    <ul className="error-suggestions">
                      <li>Add these columns to your contact file</li>
                      <li>Update your template to use available variables</li>
                      <li>Remove these variables from your template</li>
                    </ul>
                  </div>
                )}

                {validationData.available_variables && validationData.available_variables.length > 0 && (
                  <div className="detail-section success">
                    <h4>Matching Variables:</h4>
                    <div className="matching-variables">
                      {validationData.available_variables.map((variable, index) => (
                        <span key={index} className="variable-tag matching">{variable}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="modal-actions">
                <button onClick={closeValidationModal} className="close-button">
                  Close
                </button>
                {!validationData.is_valid && (
                  <button onClick={() => {
                    closeValidationModal();
                    setError('Please fix the template variables before sending the campaign');
                  }} className="fix-template-button">
                    Fix Template Issues
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Recent Campaigns Section */}
        <div className="campaigns-card">
          <div className="campaigns-header-row">
            <h3>Recent Campaigns</h3>
            <div className="view-toggle">
              <button
                className={`toggle-btn${viewMode === 'grid' ? ' active' : ''}`}
                onClick={() => setViewMode('grid')}
                title="Grid View"
              >
                {/* <FaThLarge /> */}
              </button>
              <button
                className={`toggle-btn${viewMode === 'tile' ? ' active' : ''}`}
                onClick={() => setViewMode('tile')}
                title="Tile View"
              >
                {/* <FaList /> */}
              </button>
            </div>
          </div>
          {campaignsLoading ? (
            <div className="no-campaigns"><p>Loading campaigns...</p></div>
          ) : recentCampaigns.length === 0 ? (
            <div className="no-campaigns">
              <p>No campaigns found. Start your first campaign!</p>
            </div>
          ) : (
            <div className={viewMode === 'grid' ? 'campaigns-grid' : 'campaigns-tile'}>
              {Array.isArray(recentCampaigns) && recentCampaigns.map((campaign) => (
                <div key={campaign.id} className={viewMode === 'grid' ? 'campaign-item' : 'campaign-tile-item'}>
                  <div className="campaign-header">
                    <div className="campaign-status">
                      <span 
                        className="status-icon"
                        style={{ backgroundColor: getCampaignStatusColor(campaign.status) }}
                      >
                        {getCampaignStatusIcon(campaign.status)}
                      </span>
                      <span className="campaign-name">{campaign.name}</span>
                    </div>
                    <span className="campaign-date">
                      {new Date(campaign.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="campaign-stats">
                    <div className="stat-row">
                      <span className="stat-label">Total Emails:</span>
                      <span className="stat-value">{campaign.total_emails}</span>
                    </div>
                    <div className="stat-row">
                      <span className="stat-label">Successful:</span>
                      <span className="stat-value success">{campaign.successful}</span>
                    </div>
                    <div className="stat-row">
                      <span className="stat-label">Failed:</span>
                      <span className="stat-value failed">{campaign.failed}</span>
                    </div>
                    <div className="stat-row">
                      <span className="stat-label">Duration:</span>
                      <span className="stat-value">{formatDuration(campaign.duration)}</span>
                    </div>
                  </div>
                  <div className="campaign-progress">
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ 
                          width: `${campaign.total_emails > 0 ? (campaign.successful / campaign.total_emails) * 100 : 0}%`,
                          backgroundColor: getCampaignStatusColor(campaign.status)
                        }}
                      ></div>
                    </div>
                    <span className="progress-text">
                      {campaign.total_emails > 0 ? Math.round((campaign.successful / campaign.total_emails) * 100) : 0}% Success Rate
                    </span>
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

export default AutonomousCampaign; 