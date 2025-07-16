import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Contact.css';
import Navbar from '../Component/navbar';
import Footer from '../Component/footer';
import { API_ENDPOINTS } from '../../config';

function Contact() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    subject: '',
    message: ''
  });
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isVisible, setIsVisible] = useState({});

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    const handleScroll = () => {
      const elements = document.querySelectorAll('.animate-on-scroll');
      elements.forEach((element, index) => {
        const rect = element.getBoundingClientRect();
        const isElementVisible = rect.top < window.innerHeight && rect.bottom > 0;
        setIsVisible(prev => ({ ...prev, [index]: isElementVisible }));
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('scroll', handleScroll);
    handleScroll();

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      const response = await fetch(`${API_ENDPOINTS.CONTACTS}/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit contact form');
      }

      // Success - show success message
      alert('Thank you for your message! We will get back to you soon.');
      
      // Reset form
      setFormData({
        name: '',
        email: '',
        company: '',
        subject: '',
        message: ''
      });
      
    } catch (error) {
      alert('Sorry, there was an error submitting your message. Please try again later.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // const contactInfo = [
  //   {
  //     icon: (
  //       <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
  //         <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
  //         <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
  //       </svg>
  //     ),
  //     title: "Address",
  //     details: ["123 Business Street", "Suite 100", "New York, NY 10001"],
  //     color: "cyan"
  //   },
  //   {
  //     icon: (
  //       <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
  //         <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
  //       </svg>
  //     ),
  //     title: "Email",
  //     details: ["hello@mailsflow.com", "support@mailsflow.com"],
  //     color: "purple"
  //   },
  //   {
  //     icon: (
  //       <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
  //         <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
  //       </svg>
  //     ),
  //     title: "Phone",
  //     details: ["+1 (555) 123-4567", "Mon-Fri 9AM-6PM EST"],
  //     color: "orange"
  //   }
  // ];

  const faqs = [
    {
      question: "How do I get started with MailsFlow?",
      answer: "Simply sign up for a free account and you can start creating your first email campaign in minutes. Our platform is designed to be intuitive and user-friendly with guided onboarding."
    },
    {
      question: "What email limits do you have?",
      answer: "Email limits vary by plan. Our Free plan includes 100 emails per month, Starter includes 1,000, Professional includes 10,000, and Enterprise offers up to 50,000 emails monthly."
    },
    {
      question: "Do you offer customer support?",
      answer: "Yes! We offer email support for all plans, priority support for Professional and Enterprise plans, and dedicated account management for Enterprise customers."
    },
    {
      question: "Can I cancel my subscription anytime?",
      answer: "Absolutely. You can cancel your subscription at any time with no penalties. Your account will remain active until the end of your current billing period."
    },
    {
      question: "Do you provide email templates?",
      answer: "Yes! We offer a variety of professionally designed templates that you can customize to match your brand. The number of templates varies by plan."
    },
    {
      question: "Is my data secure with MailsFlow?",
      answer: "Security is our top priority. We use enterprise-grade encryption, regular security audits, and comply with GDPR and other privacy regulations to protect your data."
    }
  ];

  return (
    <div className="contact-container">
      {/* Animated Background */}
      <div className="animated-bg">
        <div 
          className="bg-blob bg-blob-1"
          style={{
            left: mousePosition.x / 10,
            top: mousePosition.y / 10,
            transform: 'translate(-50%, -50%)'
          }}
        />
        <div 
          className="bg-blob bg-blob-2"
          style={{
            right: mousePosition.x / 15,
            bottom: mousePosition.y / 15,
            transform: 'translate(50%, 50%)'
          }}
        />
      </div>

      {/* Navigation Component */}
      <Navbar />

      {/* Header Section */}
      <section className="contact-header">
        <div className="header-content animate-on-scroll"
             style={{ opacity: isVisible[0] ? 1 : 0, transform: isVisible[0] ? 'translateY(0)' : 'translateY(40px)' }}>
          <h1>
            <span className="gradient-text">Get in Touch</span>
          </h1>
          <p>
            Have questions about MailsFlow? We're here to help you succeed with your email marketing goals.
          </p>
        </div>
      </section>

      {/* Contact Content */}
      <section className="contact-content">
        <div className="contact-grid">
          
          {/* Contact Form */}
          <div className="contact-form-section animate-on-scroll"
               style={{ opacity: isVisible[1] ? 1 : 0, transform: isVisible[1] ? 'translateX(0)' : 'translateX(-40px)' }}>
            <div className="form-card">
              <h2>
                <span className="gradient-text">Send us a Message</span>
              </h2>
              
              <form onSubmit={handleSubmit} className="contact-form">
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="name">Full Name *</label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      required
                      placeholder="Your full name"
                    />
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="email">Email Address *</label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      required
                      placeholder="your.email@company.com"
                    />
                  </div>
                </div>
                
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="company">Company</label>
                    <input
                      type="text"
                      id="company"
                      name="company"
                      value={formData.company}
                      onChange={handleInputChange}
                      placeholder="Your company name"
                    />
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="subject">Subject *</label>
                    <input
                      type="text"
                      id="subject"
                      name="subject"
                      value={formData.subject}
                      onChange={handleInputChange}
                      required
                      placeholder="What can we help you with?"
                    />
                  </div>
                </div>
                
                <div className="form-group">
                  <label htmlFor="message">Message *</label>
                  <textarea
                    id="message"
                    name="message"
                    value={formData.message}
                    onChange={handleInputChange}
                    required
                    rows="6"
                    placeholder="Tell us more about your inquiry..."
                  ></textarea>
                </div>
                
                <button 
                  type="submit" 
                  disabled={isSubmitting}
                  className="submit-btn"
                >
                  {isSubmitting ? (
                    <>
                      <div className="loading-spinner"></div>
                      <span>Sending...</span>
                    </>
                  ) : (
                    <>
                      <span>Send Message</span>
                      <div className="btn-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                        </svg>
                      </div>
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>

          {/* Contact Information */}
          <div className="contact-info-section">
            
            {/* Contact Info Cards */}
            {/* <div className="contact-info-card animate-on-scroll"
                 style={{ opacity: isVisible[2] ? 1 : 0, transform: isVisible[2] ? 'translateX(0)' : 'translateX(40px)' }}>
              <h2>
                <span className="gradient-text">Contact Information</span>
              </h2>
              
              <div className="contact-info-grid">
                {contactInfo.map((info, index) => (
                  <div key={index} className={`info-card ${info.color}`}>
                    <div className="info-icon">
                      {info.icon}
                    </div>
                    <div className="info-content">
                      <h3>{info.title}</h3>
                      {info.details.map((detail, detailIndex) => (
                        <p key={detailIndex}>{detail}</p>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div> */}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="faq-section">
        <div className="faq-content">
          <div className="faq-header animate-on-scroll"
               style={{ opacity: isVisible[4] ? 1 : 0, transform: isVisible[4] ? 'translateY(0)' : 'translateY(40px)' }}>
            <h2>
              <span className="gradient-text">Frequently Asked Questions</span>
            </h2>
            <p>Quick answers to common questions</p>
          </div>

          <div className="faq-grid">
            {faqs.map((faq, index) => (
              <div 
                key={index}
                className="faq-item animate-on-scroll"
                style={{ 
                  opacity: isVisible[5 + index] ? 1 : 0, 
                  transform: isVisible[5 + index] ? 'translateY(0)' : 'translateY(40px)',
                  transitionDelay: `${index * 100}ms`
                }}
              >
                <h3>{faq.question}</h3>
                <p>{faq.answer}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="contact-cta">
        <div className="cta-content animate-on-scroll"
             style={{ opacity: isVisible[11] ? 1 : 0, transform: isVisible[11] ? 'translateY(0)' : 'translateY(40px)' }}>
          <div className="cta-card">
            <h2>
              Ready to <span className="gradient-text">Transform</span> Your Email Marketing?
            </h2>
            <p>
              Don't wait! Start your free trial today and see the difference MailsFlow can make.
            </p>
            
            <Link to="/login" className="cta-button">
              <span>Start Free Trial</span>
              <div className="btn-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </div>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer Component */}
      <Footer />
    </div>
  );
}

export default Contact;