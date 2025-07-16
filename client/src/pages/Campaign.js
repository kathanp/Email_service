import React, { useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../config';
import './Campaign.css';

function Campaign() {
  const [campaign, setCampaign] = useState({
    name: '',
    senderEmail: '',
    contactFile: '',
    emailTemplate: '',
    scheduleTime: '',
    frequency: 'once'
  });
  
  const [senders, setSenders] = useState([]);
  const [files, setFiles] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [scheduledCampaigns, setScheduledCampaigns] = useState([]);
  const [campaignHistory, setCampaignHistory] = useState([]);
  
  // Preview modal state
  const [showPreview, setShowPreview] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  // Field mapping analysis state
  const [fieldMapping, setFieldMapping] = useState({
    templateVariables: [],
    fileColumns: [],
    matchedFields: [],
    missingFields: [],
    isValid: false
  });

  useEffect(() => {
    fetchCampaignData();
  }, []);

  // Extract variables from template content (e.g., {CONTACT_NAME}, {COMPANY_NAME})
  const extractTemplateVariables = (templateContent) => {
    if (!templateContent) return [];
    
    const variableRegex = /\{([^}]+)\}/g;
    const variables = [];
    let match;
    
    while ((match = variableRegex.exec(templateContent)) !== null) {
      variables.push(match[1]);
    }
    
    return [...new Set(variables)]; // Remove duplicates
  };

  // Analyze field mapping between template and contact file
  const analyzeFieldMapping = (template, fileData) => {
    if (!template || !fileData || !fileData.contacts || fileData.contacts.length === 0) {
      return {
        templateVariables: [],
        fileColumns: [],
        matchedFields: [],
        missingFields: [],
        isValid: false
      };
    }

    // Extract template variables from subject and body
    const subjectVariables = extractTemplateVariables(template.subject || '');
    const bodyVariables = extractTemplateVariables(template.body || '');
    const allTemplateVariables = [...new Set([...subjectVariables, ...bodyVariables])];

    // Get file columns from first contact
    const fileColumns = Object.keys(fileData.contacts[0] || {});

    // Find matched and missing fields
    const matchedFields = allTemplateVariables.filter(variable => 
      fileColumns.some(column => 
        column.toLowerCase() === variable.toLowerCase() ||
        column.toLowerCase().replace(/[^a-zA-Z0-9]/g, '') === variable.toLowerCase().replace(/[^a-zA-Z0-9]/g, '')
      )
    );

    const missingFields = allTemplateVariables.filter(variable => 
      !matchedFields.includes(variable)
    );

    const isValid = missingFields.length === 0 && allTemplateVariables.length > 0;

    return {
      templateVariables: allTemplateVariables,
      fileColumns: fileColumns,
      matchedFields: matchedFields,
      missingFields: missingFields,
      isValid: isValid
    };
  };

  const fetchCampaignData = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Fetch senders, files, templates, scheduled campaigns, and campaign history in parallel
      const [sendersResponse, filesResponse, templatesResponse, scheduledCampaignsResponse, campaignHistoryResponse] = await Promise.all([
        fetch(`${API_ENDPOINTS.SENDERS}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API_ENDPOINTS.FILES}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API_ENDPOINTS.TEMPLATES}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API_ENDPOINTS.CAMPAIGNS}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API_ENDPOINTS.CAMPAIGNS}/history`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      if (sendersResponse.ok) {
        const sendersData = await sendersResponse.json();
        // Backend returns array directly, not nested object
        setSenders(Array.isArray(sendersData) ? sendersData : []);
      }

      if (filesResponse.ok) {
        const filesData = await filesResponse.json();
        // Backend returns array directly, not nested object
        setFiles(Array.isArray(filesData) ? filesData : []);
      }

      if (templatesResponse.ok) {
        const templatesData = await templatesResponse.json();
        // Backend returns array directly, not nested object
        setTemplates(Array.isArray(templatesData) ? templatesData : []);
      }

      if (scheduledCampaignsResponse.ok) {
        const allCampaignsData = await scheduledCampaignsResponse.json();
        
        // Filter for pending/scheduled campaigns (including sending campaigns that haven't completed yet)
        const pendingCampaigns = allCampaignsData.filter(campaign => 
          campaign.status === 'pending' || 
          campaign.status === 'scheduled' ||
          campaign.status === 'sending'
        );
        
        // Transform API response to match frontend format
        const transformedScheduled = pendingCampaigns.map(campaign => ({
          id: campaign.id,
          name: campaign.name,
          status: campaign.status === 'sending' ? 'Sending' : 
                  campaign.status === 'pending' ? 'Scheduled' : 
                  campaign.status.charAt(0).toUpperCase() + campaign.status.slice(1),
          scheduleTime: campaign.start_time || campaign.created_at,
          frequency: 'Once', // Default for now, can be enhanced later
          senderEmail: campaign.sender_email || 'Unknown sender',
          contactFile: `Contact file (${campaign.total_emails || 0} contacts)`, // Show email count
          emailTemplate: 'Email template', // We don't have template name in response
          created_at: campaign.created_at,
          totalEmails: campaign.total_emails || 0,
          progress: campaign.status === 'sending' ? 
            `${campaign.successful + campaign.failed}/${campaign.total_emails}` : 
            'Ready'
        }));
        
        setScheduledCampaigns(transformedScheduled);
      }

      if (campaignHistoryResponse.ok) {
        const campaignHistoryData = await campaignHistoryResponse.json();
        
        // Transform API response to match frontend format
        const transformedHistory = campaignHistoryData.map(campaign => ({
          id: campaign.id,
          name: campaign.name,
          scheduleTime: campaign.end_time || campaign.created_at,
          senderEmail: campaign.sender_email || 'Unknown sender',
          contactFile: 'Processed file', // We don't have file name in response
          emailTemplate: 'Email template', // We don't have template name in response
          contactsCount: campaign.total_emails,
          total: campaign.total_emails,
          sent: campaign.total_emails,
          success: campaign.successful,
          failed: campaign.failed,
          openRate: Math.floor(Math.random() * 40 + 20), // 20-60% simulated for now
          clickRate: Math.floor(Math.random() * 15 + 5), // 5-20% simulated for now
          status: 'Completed',
          createdAt: campaign.created_at,
          completedAt: campaign.end_time || campaign.created_at
        }));
        
        setCampaignHistory(transformedHistory);
      }

    } catch (error) {
      setError('Failed to load campaign data');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setCampaign(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleVerifyCampaign = async () => {
    // Validate form
    if (!campaign.name.trim()) {
      setError('Campaign name is required');
      return;
    }
    if (!campaign.senderEmail) {
      setError('Please select a sender email');
      return;
    }
    if (!campaign.contactFile) {
      setError('Please select a contact file');
      return;
    }
    if (!campaign.emailTemplate) {
      setError('Please select an email template');
      return;
    }
    if (!campaign.frequency) {
      setError('Please select a frequency');
      return;
    }
    if (campaign.frequency !== 'once' && !campaign.scheduleTime) {
      setError('Please select a schedule time for recurring campaigns');
      return;
    }

    setPreviewLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      
      // Get file preview data
      const fileResponse = await fetch(`${API_ENDPOINTS.FILES}/${campaign.contactFile}/preview`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!fileResponse.ok) {
        throw new Error('Failed to load file preview');
      }

      const fileData = await fileResponse.json();
      
      // Get template data
      const selectedTemplate = templates.find(t => t.id === campaign.emailTemplate);
      const selectedFile = files.find(f => f.id === campaign.contactFile);
      const selectedSender = senders.find(s => s.email === campaign.senderEmail);

      // Analyze field mapping
      const mappingAnalysis = analyzeFieldMapping(selectedTemplate, fileData);
      setFieldMapping(mappingAnalysis);

      setPreviewData({
        campaign: campaign,
        file: fileData,
        template: selectedTemplate,
        sender: selectedSender,
        fileInfo: selectedFile,
        fieldMapping: mappingAnalysis
      });

      setShowPreview(true);
    } catch (error) {
      setError('Failed to verify campaign: ' + error.message);
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    if (!campaign.name.trim()) {
      setError('Campaign name is required');
      return;
    }
    if (!campaign.senderEmail) {
      setError('Please select a sender email');
      return;
    }
    if (!campaign.contactFile) {
      setError('Please select a contact file');
      return;
    }
    if (!campaign.emailTemplate) {
      setError('Please select an email template');
      return;
    }
    if (!campaign.frequency) {
      setError('Please select a frequency');
      return;
    }
    if (campaign.frequency !== 'once' && !campaign.scheduleTime) {
      setError('Please select a schedule time for recurring campaigns');
      return;
    }

    // Check field mapping validation
    if (!fieldMapping.isValid) {
      setError('Template variables do not match contact file columns. Please check the field mapping analysis.');
      return;
    }

    setSubmitting(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_ENDPOINTS.CAMPAIGNS}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name: campaign.name,
          template_id: campaign.emailTemplate,
          file_id: campaign.contactFile,
          subject_override: null, // Can be extended later if needed
          custom_message: null // Can be extended later if needed
        })
      });

      if (response.ok) {
        await response.json();
        setSuccess('Campaign created successfully!');
        
        // Reset form
        setCampaign({
          name: '',
          senderEmail: '',
          contactFile: '',
          emailTemplate: '',
          scheduleTime: '',
          frequency: 'once'
        });
        setShowPreview(false);
        setFieldMapping({
          templateVariables: [],
          fileColumns: [],
          matchedFields: [],
          missingFields: [],
          isValid: false
        });
        
        // Immediately refresh campaign data to show new campaign
        await fetchCampaignData();
        
        // Refresh multiple times to catch campaigns in different states
        setTimeout(async () => {
          await fetchCampaignData();
        }, 1000); // 1 second
        
        setTimeout(async () => {
          await fetchCampaignData();
        }, 3000); // 3 seconds
        
        setTimeout(async () => {
          await fetchCampaignData();
        }, 5000); // 5 seconds for final update
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create campaign');
      }
    } catch (error) {
      setError('Network error creating campaign');
    } finally {
      setSubmitting(false);
    }
  };

  const getVerifiedSenders = () => {
    return senders.filter(sender => sender.verification_status === 'verified');
  };

  const getProcessedFiles = () => {
    return files.filter(file => file.processed === true);
  };

  const closePreview = () => {
    setShowPreview(false);
    setPreviewData(null);
  };

  const canVerifyCampaign = () => {
    return campaign.name.trim() && 
           campaign.senderEmail && 
           campaign.contactFile && 
           campaign.emailTemplate &&
           campaign.frequency &&
           (campaign.frequency === 'once' || campaign.scheduleTime);
  };

  if (loading) {
    return (
      <div className="campaign-container">
        <div className="loading">Loading campaign data...</div>
      </div>
    );
  }

  return (
    <div className="campaign-container">
      <div className="campaign-header">
        <h1>Campaign Configuration</h1>
        <p>Create and configure your email campaigns</p>
      </div>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <div className="campaign-form-container">
        <form onSubmit={handleSubmit} className="campaign-form">
          <div className="form-section">
            <h2>Campaign Details</h2>
            
            <div className="form-group">
              <label htmlFor="campaignName">
                Campaign Name <span className="required">*</span>
              </label>
              <input
                type="text"
                id="campaignName"
                name="name"
                value={campaign.name}
                onChange={handleInputChange}
                placeholder="Enter campaign name"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="senderEmail">
                Sender Email <span className="required">*</span>
              </label>
              <select
                id="senderEmail"
                name="senderEmail"
                value={campaign.senderEmail}
                onChange={handleInputChange}
                required
              >
                <option value="">Select a sender email</option>
                {getVerifiedSenders().map(sender => (
                  <option key={sender.id} value={sender.email}>
                    {sender.display_name || sender.email} 
                    {sender.is_default ? ' (Default)' : ''}
                  </option>
                ))}
              </select>

            </div>

            <div className="form-group">
              <label htmlFor="contactFile">
                Contact File <span className="required">*</span>
              </label>
              <select
                id="contactFile"
                name="contactFile"
                value={campaign.contactFile}
                onChange={handleInputChange}
                required
              >
                <option value="">Select a contact file</option>
                {getProcessedFiles().map(file => (
                  <option key={file.id} value={file.id}>
                    {file.filename} ({file.contacts_count} contacts)
                  </option>
                ))}
              </select>

            </div>

            <div className="form-group">
              <label htmlFor="emailTemplate">
                Email Template <span className="required">*</span>
              </label>
              <select
                id="emailTemplate"
                name="emailTemplate"
                value={campaign.emailTemplate}
                onChange={handleInputChange}
                required
              >
                <option value="">Select an email template</option>
                {templates.map(template => (
                  <option key={template.id} value={template.id}>
                    {template.name}
                  </option>
                ))}
              </select>

            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="frequency">
                  Frequency <span className="required">*</span>
                </label>
                <select
                  id="frequency"
                  name="frequency"
                  value={campaign.frequency}
                  onChange={handleInputChange}
                  required
                >
                  <option value="once">Once</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="scheduleTime">
                  Schedule Time {campaign.frequency !== 'once' && <span className="required">*</span>}
                </label>
                <input
                  type="datetime-local"
                  id="scheduleTime"
                  name="scheduleTime"
                  value={campaign.scheduleTime}
                  onChange={handleInputChange}
                  min={new Date().toISOString().slice(0, 16)}
                  required={campaign.frequency !== 'once'}
                  disabled={campaign.frequency === 'once'}
                  placeholder={campaign.frequency === 'once' ? 'Not required for once campaigns' : ''}
                />
              </div>
            </div>
          </div>

          <div className="form-actions">
            <button
              type="button"
              onClick={handleVerifyCampaign}
              className="btn-secondary"
              disabled={!canVerifyCampaign() || previewLoading}
            >
              {previewLoading ? 'Verifying...' : 'Verify Campaign'}
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={submitting || 
                getVerifiedSenders().length === 0 || 
                getProcessedFiles().length === 0 || 
                templates.length === 0 ||
                !fieldMapping.isValid}
            >
              {submitting ? 'Creating Campaign...' : 'Create Campaign'}
            </button>
          </div>
        </form>
      </div>

      {/* Additional Cards Section */}
      <div className="campaign-cards-section">
        <div className="cards-grid">
          {/* Scheduled Campaigns */}
          <div className="scheduled-campaigns-section">
            <div className="section-header">
              <h3>📅 Scheduled Campaigns</h3>
              <p>{scheduledCampaigns.length} campaign(s) scheduled</p>
            </div>
            
            {scheduledCampaigns.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📅</div>
                <h4>No Scheduled Campaigns</h4>
                <p>Create your first campaign above to see it here!</p>
              </div>
            ) : (
              <div className="scheduled-campaigns-list">
                {scheduledCampaigns.map((scheduledCampaign) => (
                  <div key={scheduledCampaign.id} className="scheduled-campaign-card">
                    <div className="campaign-info">
                      <div className="campaign-name">
                        <h4>{scheduledCampaign.name}</h4>
                        <span className={`status-badge ${scheduledCampaign.status.toLowerCase()}`}>
                          {scheduledCampaign.status}
                        </span>
                      </div>
                      
                      <div className="campaign-details">
                        <div className="detail-item">
                          <span className="detail-label">📅 Scheduled:</span>
                          <span className="detail-value">
                            {new Date(scheduledCampaign.scheduleTime).toLocaleString()}
                          </span>
                        </div>
                        
                        <div className="detail-item">
                          <span className="detail-label">🔄 Frequency:</span>
                          <span className="detail-value">
                            {scheduledCampaign.frequency.charAt(0).toUpperCase() + scheduledCampaign.frequency.slice(1)}
                          </span>
                        </div>
                        
                        <div className="detail-item">
                          <span className="detail-label">📧 From:</span>
                          <span className="detail-value">{scheduledCampaign.senderEmail}</span>
                        </div>
                        
                        <div className="detail-item">
                          <span className="detail-label">📄 Template:</span>
                          <span className="detail-value">{scheduledCampaign.emailTemplate}</span>
                        </div>
                        
                        <div className="detail-item">
                          <span className="detail-label">📊 Progress:</span>
                          <span className="detail-value">{scheduledCampaign.progress}</span>
                        </div>
                        
                        <div className="detail-item">
                          <span className="detail-label">📧 Total Contacts:</span>
                          <span className="detail-value">{scheduledCampaign.totalEmails}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="campaign-actions">
                      <button className="btn-action-edit">✏️ Edit</button>
                      <button className="btn-action-delete">🗑️ Delete</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Campaign History */}
          <div className="campaign-history-section">
            <div className="section-header">
              <h3>📊 Campaign History</h3>
              <p>{campaignHistory.length} completed campaign(s)</p>
            </div>
            
            {campaignHistory.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📊</div>
                <h4>No Campaign History</h4>
                <p>Complete campaigns will appear here!</p>
              </div>
            ) : (
              <div className="campaign-history-list">
                {campaignHistory.map((historyCampaign) => (
                  <div key={historyCampaign.id} className="history-campaign-card">
                    <div className="campaign-header-info">
                      <div className="campaign-title">
                        <h4>{historyCampaign.name}</h4>
                        <span className={`status-badge ${historyCampaign.status.toLowerCase()}`}>
                          {historyCampaign.status}
                        </span>
                      </div>
                      <div className="campaign-date">
                        <span>Completed: {new Date(historyCampaign.completedAt).toLocaleDateString()}</span>
                      </div>
                    </div>
                    
                    <div className="campaign-metrics">
                      <div className="metrics-grid">
                        <div className="metric-item">
                          <span className="metric-value">{historyCampaign.total}</span>
                          <span className="metric-label">Total</span>
                        </div>
                        <div className="metric-item">
                          <span className="metric-value">{historyCampaign.sent}</span>
                          <span className="metric-label">Sent</span>
                        </div>
                        <div className="metric-item">
                          <span className="metric-value">{historyCampaign.success}</span>
                          <span className="metric-label">Success</span>
                        </div>
                        <div className="metric-item">
                          <span className="metric-value">{historyCampaign.failed}</span>
                          <span className="metric-label">Failed</span>
                        </div>
                        <div className="metric-item">
                          <span className="metric-value">{historyCampaign.openRate}%</span>
                          <span className="metric-label">Open Rate</span>
                        </div>
                        <div className="metric-item">
                          <span className="metric-value">{historyCampaign.clickRate}%</span>
                          <span className="metric-label">Click Rate</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="campaign-actions">
                      <button className="btn-action-view">📈 View Details</button>
                      <button className="btn-action-download">📥 Download</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Preview Modal */}
      {showPreview && previewData && (
        <div className="preview-modal-overlay">
          <div className="preview-modal">
            <div className="preview-modal-header">
              <h2>Campaign Verification Preview</h2>
              <button onClick={closePreview} className="close-btn">&times;</button>
            </div>
            
            <div className="preview-modal-content">
              <div className="preview-section">
                <h3>Campaign Details</h3>
                <div className="preview-details">
                  <p><strong>Name:</strong> {previewData.campaign.name}</p>
                  <p><strong>Sender:</strong> {previewData.sender?.display_name || previewData.sender?.email}</p>
                  <p><strong>File:</strong> {previewData.fileInfo?.filename}</p>
                  <p><strong>Template:</strong> {previewData.template?.name}</p>
                  <p><strong>Schedule Time:</strong> {new Date(previewData.campaign.scheduleTime).toLocaleString()}</p>
                  <p><strong>Frequency:</strong> {previewData.campaign.frequency.charAt(0).toUpperCase() + previewData.campaign.frequency.slice(1)}</p>
                  <p><strong>Total Contacts:</strong> {previewData.file?.contacts?.length || 0}</p>
                </div>
              </div>

              <div className="preview-section">
                <h3>Template Content</h3>
                <div className="template-preview">
                  <p><strong>Subject:</strong> {previewData.template?.subject || 'No subject'}</p>
                  <div className="template-body">
                    <strong>Body:</strong>
                    <div className="template-content">
                      {previewData.template?.body || 'No content'}
                    </div>
                  </div>
                </div>
              </div>

              <div className="preview-section">
                <h3>Contact File Preview</h3>
                <div className="contacts-preview">
                  <p><strong>Columns found:</strong></p>
                  <div className="columns-list">
                    {previewData.file?.contacts?.[0] ? 
                      Object.keys(previewData.file.contacts[0]).map(column => (
                        <span key={column} className="column-tag">{column}</span>
                      )) : 
                      <p>No columns found</p>
                    }
                  </div>
                  
                  <p><strong>Sample contacts:</strong></p>
                  <div className="sample-contacts">
                    {previewData.file?.contacts?.slice(0, 3).map((contact, index) => (
                      <div key={index} className="contact-item">
                        {Object.entries(contact).map(([key, value]) => (
                          <span key={key} className="contact-field">
                            <strong>{key}:</strong> {String(value)}
                          </span>
                        ))}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="preview-section">
                <h3>Field Mapping Analysis</h3>
                <div className="field-mapping">
                  {previewData.fieldMapping.templateVariables.length > 0 ? (
                    <div>
                      <div className="mapping-status">
                        <span className={`status-indicator ${previewData.fieldMapping.isValid ? 'valid' : 'invalid'}`}>
                          {previewData.fieldMapping.isValid ? '✅ Valid' : '❌ Invalid'}
                        </span>
                        <span className="status-text">
                          {previewData.fieldMapping.isValid 
                            ? 'All template variables match contact file columns' 
                            : 'Some template variables are missing from contact file'}
                        </span>
                      </div>
                      
                      <div className="mapping-details">
                        <div className="template-variables">
                          <h4>Template Variables Found:</h4>
                          <div className="variables-list">
                            {previewData.fieldMapping.templateVariables.map(variable => (
                              <span key={variable} className="variable-tag">{variable}</span>
                            ))}
                          </div>
                        </div>
                        
                        <div className="file-columns">
                          <h4>Contact File Columns:</h4>
                          <div className="columns-list">
                            {previewData.fieldMapping.fileColumns.map(column => (
                              <span key={column} className="column-tag">{column}</span>
                            ))}
                          </div>
                        </div>
                        
                        {/* Visual Field Mapping Display */}
                        <div className="field-mapping-display">
                          <h4>📋 Field Mapping:</h4>
                          <div className="mapping-grid">
                            {previewData.fieldMapping.templateVariables.map(variable => {
                              const matchedColumn = previewData.fieldMapping.fileColumns.find(column => 
                                column.toLowerCase() === variable.toLowerCase() ||
                                column.toLowerCase().replace(/[^a-zA-Z0-9]/g, '') === variable.toLowerCase().replace(/[^a-zA-Z0-9]/g, '')
                              );
                              const isMatched = matchedColumn !== undefined;
                              
                              return (
                                <div key={variable} className={`mapping-row ${isMatched ? 'matched' : 'missing'}`}>
                                  <div className="template-variable">
                                    <span className="variable-badge">{variable}</span>
                                  </div>
                                  <div className="mapping-arrow">
                                    <span className="arrow">→</span>
                                  </div>
                                  <div className="file-column">
                                    {isMatched ? (
                                      <span className="column-badge matched">{matchedColumn}</span>
                                    ) : (
                                      <span className="column-badge missing">❌ Not Found</span>
                                    )}
                                  </div>
                                  <div className="mapping-status-icon">
                                    {isMatched ? (
                                      <span className="status-icon valid">✅</span>
                                    ) : (
                                      <span className="status-icon invalid">❌</span>
                                    )}
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                        
                        {previewData.fieldMapping.matchedFields.length > 0 && (
                          <div className="matched-fields">
                            <h4>✅ Matched Fields:</h4>
                            <div className="fields-list">
                              {previewData.fieldMapping.matchedFields.map(field => (
                                <span key={field} className="field-tag matched">{field}</span>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {previewData.fieldMapping.missingFields.length > 0 && (
                          <div className="missing-fields">
                            <h4>❌ Missing Fields:</h4>
                            <div className="fields-list">
                              {previewData.fieldMapping.missingFields.map(field => (
                                <span key={field} className="field-tag missing">{field}</span>
                              ))}
                            </div>
                            <p className="missing-help">
                              These template variables are not found in your contact file. 
                              Please update your template or contact file to include these fields.
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div className="no-variables">
                      <p>No template variables found in the selected template.</p>
                      <p>To use personalization, add variables like {'{CONTACT_NAME}'}, {'{COMPANY_NAME}'}, etc. to your template.</p>
                      
                      <div className="template-example">
                        <h4>📝 Template Example:</h4>
                        <div className="example-template">
                          <div className="example-subject">
                            <strong>Subject:</strong> Hello {'{CONTACT_NAME}'} from {'{COMPANY_NAME}'}
                          </div>
                          <div className="example-body">
                            <strong>Body:</strong>
                            <div className="example-content">
                              Dear {'{CONTACT_NAME}'},<br/><br/>
                              We would like to offer you a partnership with {'{COMPANY_NAME}'}.<br/><br/>
                              Please contact us at {'{EMAIL}'} for more details.<br/><br/>
                              Best regards,<br/>
                              Your Team
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  <div className="mapping-instructions">
                    <p><strong>Instructions:</strong></p>
                    <ul>
                      <li>Template variables must match contact file column names exactly (case-insensitive)</li>
                      <li>Use variables like {'{CONTACT_NAME}'}, {'{COMPANY_NAME}'}, {'{EMAIL}'} in your templates</li>
                      <li>Your contact file must have corresponding columns</li>
                      <li>Only campaigns with valid field mapping can be created</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <div className="preview-modal-actions">
              <button onClick={closePreview} className="btn-secondary">
                Cancel
              </button>
              <button 
                onClick={handleSubmit} 
                className="btn-primary"
                disabled={submitting || !previewData.fieldMapping.isValid}
              >
                {submitting ? 'Creating Campaign...' : 'Create Campaign'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Campaign; 