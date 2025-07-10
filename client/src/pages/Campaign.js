import React, { useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../config';
import './Campaign.css';

function Campaign() {
  const [campaign, setCampaign] = useState({
    name: '',
    senderEmail: '',
    contactFile: '',
    emailTemplate: ''
  });
  
  const [senders, setSenders] = useState([]);
  const [files, setFiles] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Preview modal state
  const [showPreview, setShowPreview] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  useEffect(() => {
    fetchCampaignData();
  }, []);

  const fetchCampaignData = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Fetch senders, files, and templates in parallel
      const [sendersResponse, filesResponse, templatesResponse] = await Promise.all([
        fetch(`${API_ENDPOINTS.SENDERS}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API_ENDPOINTS.FILES}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API_ENDPOINTS.TEMPLATES}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      if (sendersResponse.ok) {
        const sendersData = await sendersResponse.json();
        setSenders(sendersData.senders || []);
      }

      if (filesResponse.ok) {
        const filesData = await filesResponse.json();
        setFiles(filesData.files || []);
      }

      if (templatesResponse.ok) {
        const templatesData = await templatesResponse.json();
        setTemplates(templatesData.templates || []);
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

      setPreviewData({
        campaign: campaign,
        file: fileData,
        template: selectedTemplate,
        sender: selectedSender,
        fileInfo: selectedFile
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
        body: JSON.stringify(campaign)
      });

      if (response.ok) {
        await response.json();
        setSuccess('Campaign created successfully!');
        setCampaign({
          name: '',
          senderEmail: '',
          contactFile: '',
          emailTemplate: ''
        });
        setShowPreview(false);
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
           campaign.emailTemplate;
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
              {getVerifiedSenders().length === 0 && (
                <div className="form-help">
                  No verified sender emails found. Please add and verify a sender email first.
                </div>
              )}
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
              {getProcessedFiles().length === 0 && (
                <div className="form-help">
                  No processed files found. Please upload and process a contact file first.
                </div>
              )}
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
              {templates.length === 0 && (
                <div className="form-help">
                  No templates found. Please create an email template first.
                </div>
              )}
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
                templates.length === 0}
            >
              {submitting ? 'Creating Campaign...' : 'Create Campaign'}
            </button>
          </div>
        </form>
      </div>

      {/* Campaign Summary */}
      {campaign.name && (
        <div className="campaign-summary">
          <h3>Campaign Summary</h3>
          <div className="summary-grid">
            <div className="summary-item">
              <label>Campaign Name:</label>
              <span>{campaign.name}</span>
            </div>
            <div className="summary-item">
              <label>Sender Email:</label>
              <span>{campaign.senderEmail || 'Not selected'}</span>
            </div>
            <div className="summary-item">
              <label>Contact File:</label>
              <span>
                {campaign.contactFile ? 
                  files.find(f => f.id === campaign.contactFile)?.filename || 'Unknown file' : 
                  'Not selected'
                }
              </span>
            </div>
            <div className="summary-item">
              <label>Email Template:</label>
              <span>
                {campaign.emailTemplate ? 
                  templates.find(t => t.id === campaign.emailTemplate)?.name || 'Unknown template' : 
                  'Not selected'
                }
              </span>
            </div>
          </div>
        </div>
      )}

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
                  <p>This preview shows how your contact file data will be used in the campaign.</p>
                  <p>If you see the data you expect, you can proceed to create the campaign.</p>
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
                disabled={submitting}
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