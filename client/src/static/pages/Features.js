import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

import Navbar from '../Component/navbar';
import Footer from '../Component/footer';
import './Features.css';


function Features() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
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

  const heroFeatures = [
    {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      ),
      title: "AI-Powered Intelligence",
      description: "Machine learning algorithms that optimize your campaigns automatically",
      color: "cyan"
    },
    {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      title: "Lightning Fast Delivery",
      description: "99.9% delivery rate with our global infrastructure network",
      color: "purple"
    },
    {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
      ),
      title: "Enterprise Security",
      description: "Bank-level encryption with GDPR compliance and data protection",
      color: "orange"
    }
  ];

  const mainFeatures = [
    {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      ),
      title: "Campaign Management",
      description: "Create, schedule, and manage professional email campaigns with advanced automation and personalization features.",
      features: ["Drag & Drop Builder", "Advanced Scheduling", "A/B Testing", "Personalization"],
      color: "cyan"
    },
    {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      title: "Advanced Analytics",
      description: "Track performance with detailed analytics, open rates, click-through rates, and conversion tracking in real-time.",
      features: ["Real-time Reports", "Heat Maps", "Conversion Tracking", "ROI Analysis"],
      color: "purple"
    },
    {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
      title: "Smart Templates",
      description: "Professional email templates that adapt to your brand with our intelligent design system and responsive layouts.",
      features: ["50+ Templates", "Mobile Responsive", "Brand Customization", "Dynamic Content"],
      color: "green"
    },
    {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      ),
      title: "Contact Management",
      description: "Organize and segment your contact lists for targeted campaigns with advanced filtering and tagging systems.",
      features: ["Smart Segmentation", "Import/Export", "Custom Fields", "Tag Management"],
      color: "blue"
    },
    {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      title: "Marketing Automation",
      description: "Set up automated email sequences and drip campaigns to nurture your audience with behavioral triggers.",
      features: ["Drip Campaigns", "Behavioral Triggers", "Lead Scoring", "Workflow Builder"],
      color: "yellow"
    },
    {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
      ),
      title: "API & Integrations",
      description: "Connect with your favorite tools and platforms through our robust API and pre-built integrations.",
      features: ["REST API", "Webhooks", "CRM Integration", "E-commerce Sync"],
      color: "red"
    }
  ];

  const stats = [
    { number: "99.9%", label: "Delivery Rate", color: "cyan" },
    { number: "2M+", label: "Emails Sent Daily", color: "purple" },
    { number: "10K+", label: "Happy Customers", color: "green" },
    { number: "24/7", label: "Expert Support", color: "orange" }
  ];

  const integrations = [
    { name: 'Shopify', icon: 'S', color: 'from-green-500 to-green-600' },
    { name: 'WordPress', icon: 'W', color: 'from-blue-500 to-blue-600' },
    { name: 'Salesforce', icon: 'SF', color: 'from-blue-400 to-cyan-500' },
    { name: 'HubSpot', icon: 'H', color: 'from-orange-500 to-red-500' },
    { name: 'Zapier', icon: 'Z', color: 'from-purple-500 to-pink-500' },
    { name: 'Slack', icon: 'SL', color: 'from-green-400 to-cyan-400' }
  ];

  return (
    <div className="features-container">
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

      {/* Navigation */}
      <Navbar />

      {/* Hero Section */}
      <section className="features-hero">
        <div className="hero-content animate-on-scroll"
             style={{ opacity: isVisible[0] ? 1 : 0, transform: isVisible[0] ? 'translateY(0)' : 'translateY(40px)' }}>
          <h1>
            <span className="gradient-text">Powerful Features</span>
            <br />
            <span className="white-text">for Modern Email Marketing</span>
          </h1>
          
          <p>
            Discover the comprehensive suite of tools designed to help you create, manage, and optimize your email campaigns like never before.
          </p>
          
          <div className="hero-features-grid">
            {heroFeatures.map((feature, index) => (
              <div key={index} className={`hero-feature-card ${feature.color}`}>
                <div className="feature-icon">
                  {feature.icon}
                </div>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats-section">
        <div className="stats-container animate-on-scroll"
             style={{ opacity: isVisible[1] ? 1 : 0, transform: isVisible[1] ? 'translateY(0)' : 'translateY(40px)' }}>
          {stats.map((stat, index) => (
            <div key={index} className={`stat-item ${stat.color}`}>
              <div className="stat-number">{stat.number}</div>
              <div className="stat-label">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Main Features Section */}
      <section className="main-features-section">
        <div className="section-header animate-on-scroll"
             style={{ opacity: isVisible[2] ? 1 : 0, transform: isVisible[2] ? 'translateY(0)' : 'translateY(40px)' }}>
          <h2>
            <span className="gradient-text">Everything You Need</span>
            <br />
            <span className="white-text">to Succeed</span>
          </h2>
          <p>
            Our comprehensive platform provides all the tools and features you need to create engaging email campaigns that convert.
          </p>
        </div>

        <div className="features-grid">
          {mainFeatures.map((feature, index) => (
            <div 
              key={index}
              className={`main-feature-card ${feature.color} animate-on-scroll`}
              style={{ 
                opacity: isVisible[3 + index] ? 1 : 0, 
                transform: isVisible[3 + index] ? 'translateY(0)' : 'translateY(40px)',
                transitionDelay: `${index * 150}ms`
              }}
            >
              <div className="feature-header">
                <div className="feature-icon">
                  {feature.icon}
                </div>
                <div className="feature-title">
                  <h3>{feature.title}</h3>
                  <p>{feature.description}</p>
                </div>
              </div>
              
              <div className="feature-list">
                {feature.features.map((item, itemIndex) => (
                  <div key={itemIndex} className="feature-list-item">
                    <div className="list-icon">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <span>{item}</span>
                  </div>
                ))}
              </div>
              
              <div className="feature-action">
                <button className="learn-more-btn">
                  <span>Learn More</span>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Integration Section */}
      <section className="integration-section">
        <div className="integration-content animate-on-scroll"
             style={{ opacity: isVisible[9] ? 1 : 0, transform: isVisible[9] ? 'translateY(0)' : 'translateY(40px)' }}>
          <div className="integration-header">
            <h2>
              <span className="gradient-text">Seamless Integrations</span>
            </h2>
            <p>
              Connect MailsFlow with your favorite tools and platforms for a unified workflow experience.
            </p>
          </div>
          
          <div className="integration-grid">
            {integrations.map((integration, index) => (
              <div key={index} className="integration-card">
                <div className={`integration-logo bg-gradient-to-br ${integration.color}`}>
                  {integration.icon}
                </div>
                <span>{integration.name}</span>
              </div>
            ))}
          </div>
          
          <div className="integration-cta">
            <p>And 50+ more integrations available</p>
            <Link to="/integrations" className="view-all-btn">
              <span>View All Integrations</span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Link>
          </div>
        </div>
      </section>

      {/* Testimonial Section */}
      <section className="testimonial-section">
        <div className="testimonial-content animate-on-scroll"
             style={{ opacity: isVisible[10] ? 1 : 0, transform: isVisible[10] ? 'translateY(0)' : 'translateY(40px)' }}>
          <div className="testimonial-header">
            <h2>
              <span className="gradient-text">Loved by Thousands</span>
              <br />
              <span className="white-text">of Businesses</span>
            </h2>
          </div>
          
          <div className="testimonials-grid">
            <div className="testimonial-card">
              <div className="testimonial-rating">
                {[...Array(5)].map((_, i) => (
                  <span key={i} className="star">⭐</span>
                ))}
              </div>
              <p>
                "MailsFlow transformed our email marketing. The AI optimization increased our open rates by 300% in just 2 months!"
              </p>
              <div className="testimonial-author">
                <div className="author-avatar">
                  <span>S</span>
                </div>
                <div className="author-info">
                  <strong>Sarah Johnson</strong>
                  <span>Marketing Director, TechCorp</span>
                </div>
              </div>
            </div>
            
            <div className="testimonial-card">
              <div className="testimonial-rating">
                {[...Array(5)].map((_, i) => (
                  <span key={i} className="star">⭐</span>
                ))}
              </div>
              <p>
                "The automation features saved us hours every week. Our drip campaigns now run perfectly without any manual intervention."
              </p>
              <div className="testimonial-author">
                <div className="author-avatar">
                  <span>M</span>
                </div>
                <div className="author-info">
                  <strong>Michael Chen</strong>
                  <span>CEO, StartupFlow</span>
                </div>
              </div>
            </div>
            
            <div className="testimonial-card">
              <div className="testimonial-rating">
                {[...Array(5)].map((_, i) => (
                  <span key={i} className="star">⭐</span>
                ))}
              </div>
              <p>
                "Best email platform we've ever used. The analytics insights helped us understand our customers like never before."
              </p>
              <div className="testimonial-author">
                <div className="author-avatar">
                  <span>E</span>
                </div>
                <div className="author-info">
                  <strong>Emily Rodriguez</strong>
                  <span>Growth Manager, EcomPlus</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="features-cta">
        <div className="cta-content animate-on-scroll"
             style={{ opacity: isVisible[11] ? 1 : 0, transform: isVisible[11] ? 'translateY(0)' : 'translateY(40px)' }}>
          <div className="cta-card">
            <h2>
              Ready to <span className="gradient-text">Experience</span> These Features?
            </h2>
            <p>
              Start your free trial today and discover how MailsFlow can transform your email marketing strategy.
            </p>
            
            <div className="cta-buttons">
              <Link to="/login" className="cta-primary">
                <span>Start Free Trial</span>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </Link>
              
              <Link to="/pricing" className="cta-secondary">
                <span>View Pricing</span>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <Footer />
    </div>
  );
}

export default Features;