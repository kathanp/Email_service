import React, { useState, useEffect } from 'react';
import { useAppContext } from '../context/AppContext';
import './EmailTemplates.css';

function EmailTemplates() {
  const [newTemplate, setNewTemplate] = useState({
    name: '',
    subject: '',
    body: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const { 
    templates, 
    isLoading, 
    createTemplate, 
    deleteTemplate, 
    setTemplateAsDefault 
  } = useAppContext();

  // Pre-filled generic cold email template
  const genericColdEmailTemplate = {
    name: 'Generic Cold Email - Corporate Partnership',
    subject: 'Exclusive Corporate Partnership Opportunity - {COMPANY_NAME}',
    body: `Dear Sir/Madam,

I trust this letter finds you well. I am writing to introduce the exclusive corporate rates available at {BUSINESS_NAME}, designed specifically for {COMPANY_NAME}'s contractors and workforce.

We understand that business travelers have unique requirements, and we are committed to providing exceptional accommodations at competitive rates. Our partnership with {PARTNER_NAME} enables us to offer particularly attractive pricing for both short-term and extended stays.

Our Corporate Rate Structure:
{BUSINESS_NAME}
- Weekly Rates: {WEEKLY_RATE_SINGLE} (Single Bed) / {WEEKLY_RATE_DOUBLE} (Double Bed) including tax
- Monthly Rates: {MONTHLY_RATE_SINGLE} (Single Bed) / {MONTHLY_RATE_DOUBLE} (Double Bed) per night including tax, for stays of one month or longer

Distinguished Amenities:
- {AMENITY_1}
- {AMENITY_2}
- {AMENITY_3}
- {AMENITY_4}
- {AMENITY_5}
- {AMENITY_6}
- {AMENITY_7}
- {AMENITY_8}

For companies with specific room requirements and employee headcounts, we are happy to discuss custom rate negotiations to better accommodate your needs. Our flexible pricing structure allows us to provide even more competitive rates for larger groups or longer-term commitments.

As a {PARTNER_NAME} partner, we are positioned to provide superior accommodations at highly competitive rates. We welcome the opportunity to discuss how we can tailor our services to meet your specific requirements.

For reservations or inquiries, please contact:
{CONTACT_NAME}
{CONTACT_TITLE}
Tel: {CONTACT_PHONE}
Email: {CONTACT_EMAIL}

We look forward to establishing a lasting partnership with {COMPANY_NAME} and serving as your preferred accommodation provider.

Best regards,
{CONTACT_NAME}
{CONTACT_TITLE}
{BUSINESS_NAME}

Template Variables to Replace:
- {COMPANY_NAME}: Target company name
- {BUSINESS_NAME}: Your business name
- {PARTNER_NAME}: Partner organization name
- {WEEKLY_RATE_SINGLE}: Weekly rate for single bed
- {WEEKLY_RATE_DOUBLE}: Weekly rate for double bed
- {MONTHLY_RATE_SINGLE}: Monthly rate per night for single bed
- {MONTHLY_RATE_DOUBLE}: Monthly rate per night for double bed
- {AMENITY_1-8}: List of amenities
- {CONTACT_NAME}: Your name
- {CONTACT_TITLE}: Your title
- {CONTACT_PHONE}: Your phone number
- {CONTACT_EMAIL}: Your email address`
  };

  // Red Roof Inn specific template
  const redRoofInnTemplate = {
    name: 'Red Roof Inn - Corporate Partnership (Kathan)',
    subject: 'Corporate Accommodation Partnership - Red Roof Inn Moss Point',
    body: `Dear {CONTACT_NAME},

I hope this message finds you well. I'm reaching out regarding corporate accommodation opportunities for {COMPANY_NAME} at Red Roof Inn, Moss Point.

We specialize in providing quality accommodations for business travelers and contractors, with competitive rates designed for corporate partnerships.

**Our Corporate Rate Structure:**
Red Roof Inn, Moss Point
• Weekly Rates: $370 (Single Bed) / $420 (Double Bed) including tax
• Monthly Rates: $50 (Single Bed) / $57 (Double Bed) per night including tax, for stays of one month or longer

**Property Features:**
• Complimentary hot breakfast
• Newly renovated rooms with modern furniture
• Complimentary Tesla and EV charging stations
• High-speed Wi-Fi
• 24/7 coffee service in the lobby
• Strategic location in Moss Point
• Business-friendly facilities
• Corporate rewards program

We offer flexible pricing for larger groups and extended stays. Our partnership with CLC Lodging enables us to provide competitive rates for corporate clients.

Contact Information:
Kathan Patel
General Manager
Tel: +1(228) 460-0615
Email: Redroofinn1101@gmail.com

I'd welcome the opportunity to discuss how we can meet {COMPANY_NAME}'s accommodation needs. Please let me know if you'd like to schedule a brief call to explore this partnership further.

Best regards,
Kathan Patel
General Manager
Red Roof Inn, Moss Point

---
This email is sent in accordance with applicable email regulations. To unsubscribe, please reply with "Unsubscribe" in the subject line.

Template Variables to Replace:
- {CONTACT_NAME}: Contact person's name
- {COMPANY_NAME}: Target company name (e.g., Ksy group)`
  };

  const loadDefaultTemplate = () => {
    // Find the default template from the user's saved templates
    const defaultTemplate = templates.find(template => template.is_default);
    
    if (defaultTemplate) {
      setNewTemplate({
        name: defaultTemplate.name,
        subject: defaultTemplate.subject,
        body: defaultTemplate.body
      });
      setSuccess(`Loaded default template: ${defaultTemplate.name}`);
    } else {
      // If no default template is set, load the generic template
      setNewTemplate(genericColdEmailTemplate);
      setSuccess('No default template found. Loaded generic template.');
    }
  };

  const loadRedRoofTemplate = () => {
    setNewTemplate(redRoofInnTemplate);
  };

  const handleSetTemplateAsDefault = async (template) => {
    try {
      const result = await setTemplateAsDefault(template);
      
      if (result.success) {
        // Clear the form when setting a new default template
        setNewTemplate({ name: '', subject: '', body: '' });
        setSuccess(`${template.name} set as default template! Form cleared for new template creation.`);
      } else {
        setError(result.error || 'Failed to set template as default');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!newTemplate.name.trim() || !newTemplate.subject.trim() || !newTemplate.body.trim()) {
      setError('Please fill in all fields');
      return;
    }

    setIsSubmitting(true);
    setError('');
    setSuccess('');

    try {
      const result = await createTemplate({
        name: newTemplate.name,
        subject: newTemplate.subject,
        body: newTemplate.body
      });

      if (result.success) {
        setNewTemplate({ name: '', subject: '', body: '' });
        setSuccess('Template created successfully!');
      } else {
        setError(result.error || 'Failed to create template');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (templateId) => {
    if (!window.confirm('Are you sure you want to delete this template?')) {
      return;
    }

    try {
      const result = await deleteTemplate(templateId);
      
      if (result.success) {
        setSuccess('Template deleted successfully!');
      } else {
        setError(result.error || 'Failed to delete template');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
  };

  useEffect(() => {
    // Start with empty template form
    setNewTemplate({ name: '', subject: '', body: '' });
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
      <div className="email-templates">
        <div className="loading">Loading templates...</div>
      </div>
    );
  }

  return (
    <div className="email-templates-wrapper">
      <div className="email-templates">
        <div className="templates-header">
          <h2>Email Templates</h2>
          <p>Create and manage your email templates for campaigns</p>
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        <div className="template-form-container">
          <h3>Create New Template</h3>
          <div className="template-actions">
            <button 
              type="button" 
              onClick={loadDefaultTemplate} 
              className={`load-template-button ${templates.find(t => t.is_default) ? 'has-default' : ''}`}
            >
              Load Default Email Template
              {templates.find(t => t.is_default) && <span className="default-indicator">●</span>}
            </button>
            <button 
              type="button" 
              onClick={loadRedRoofTemplate} 
              className="load-template-button red-roof"
            >
              Load Red Roof Inn Template
            </button>
          </div>
          <form onSubmit={handleSubmit} className="template-form">
            <div className="form-group">
              <label htmlFor="templateName">Template Name *</label>
              <input
                id="templateName"
                type="text"
                placeholder="Enter template name"
                value={newTemplate.name}
                onChange={(e) => setNewTemplate({...newTemplate, name: e.target.value})}
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="emailSubject">Email Subject *</label>
              <input
                id="emailSubject"
                type="text"
                placeholder="Enter email subject"
                value={newTemplate.subject}
                onChange={(e) => setNewTemplate({...newTemplate, subject: e.target.value})}
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="emailBody">Email Body *</label>
              <textarea
                id="emailBody"
                placeholder="Enter email body content"
                value={newTemplate.body}
                onChange={(e) => setNewTemplate({...newTemplate, body: e.target.value})}
                rows="6"
                required
              />
            </div>
            
            <button type="submit" disabled={isSubmitting} className="save-button">
              {isSubmitting ? 'Saving...' : 'Save Template'}
            </button>
          </form>
        </div>

        <div className="templates-list-container">
          <h3>Your Templates ({templates.length})</h3>
          {templates.length === 0 ? (
            <div className="no-templates">
              <p>No templates created yet. Create your first template above!</p>
            </div>
          ) : (
            <div className="templates-grid">
              {templates.map((template) => (
                <div key={template.id} className={`template-card ${template.is_default ? 'default-template' : ''}`}>
                  <div className="template-header">
                    <h4>
                      {template.name}
                      {template.is_default && <span className="default-badge">Default</span>}
                    </h4>
                    <div className="template-actions-buttons">
                      <button
                        onClick={() => handleSetTemplateAsDefault(template)}
                        className={`set-default-button ${template.is_default ? 'is-default' : ''}`}
                        title={template.is_default ? 'Current default template' : 'Set as default'}
                      >
                        {template.is_default ? '⭐' : '☆'}
                      </button>
                      <button
                        onClick={() => handleDelete(template.id)}
                        className="delete-button"
                        title="Delete template"
                      >
                        ×
                      </button>
                    </div>
                  </div>
                  <div className="template-content">
                    <p className="template-subject">
                      <strong>Subject:</strong> {template.subject}
                    </p>
                    <p className="template-body">
                      <strong>Body:</strong> {template.body.length > 100 
                        ? `${template.body.substring(0, 100)}...` 
                        : template.body}
                    </p>
                    <p className="template-date">
                      Created: {formatDate(template.created_at)}
                    </p>
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

export default EmailTemplates; 