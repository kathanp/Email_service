import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

import './Landing.css';
import Navbar from '../Component/navbar';
import Footer from '../Component/footer';

function Landing() {
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

  const features = [
    {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      title: "AI-Powered Campaigns",
      description: "Create stunning campaigns with artificial intelligence that learns from your audience and optimizes performance automatically.",
      color: "cyan"
    },
    {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      title: "Real-time Analytics",
      description: "Track performance with advanced analytics, heat maps, and conversion tracking that updates in real-time.",
      color: "purple"
    },
    {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17v4a2 2 0 002 2h4M15 7l3 3" />
        </svg>
      ),
      title: "Dynamic Templates",
      description: "Professional templates that adapt to your brand with our intelligent design system and drag-drop editor.",
      color: "green"
    },
    {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
      ),
      title: "Lightning Automation",
      description: "Set up complex email sequences and behavioral triggers that respond to your customers instantly.",
      color: "orange"
    },
    {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
      ),
      title: "Enterprise Security",
      description: "Bank-level security with end-to-end encryption, GDPR compliance, and advanced threat protection.",
      color: "blue"
    },
    {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      title: "Global Delivery",
      description: "99.9% delivery rate with our worldwide infrastructure and intelligent routing algorithms.",
      color: "yellow"
    }
  ];

  const testimonials = [
    {
      quote: "MailsFlow transformed our email marketing completely. Our open rates increased by 300% in just 2 months!",
      author: "Sarah Johnson",
      position: "Marketing Director",
      company: "TechCorp",
      avatar: "S",
      rating: 5
    },
    {
      quote: "The automation features are incredible. We save 10+ hours per week and our campaigns perform better than ever.",
      author: "Michael Chen",
      position: "CEO",
      company: "StartupFlow",
      avatar: "M",
      rating: 5
    },
    {
      quote: "Best email platform we've used. The analytics insights helped us understand our customers like never before.",
      author: "Emily Rodriguez",
      position: "Growth Manager",
      company: "EcomPlus",
      avatar: "E",
      rating: 5
    }
  ];

  const stats = [
    { number: "99.9%", label: "Delivery Rate", color: "cyan" },
    { number: "2M+", label: "Emails Sent Daily", color: "purple" },
    { number: "10K+", label: "Happy Customers", color: "green" },
    { number: "24/7", label: "Expert Support", color: "orange" }
  ];

  const pricingPlans = [
    {
      name: "Free",
      price: "$0",
      period: "month",
      description: "Perfect for getting started",
      features: ["100/mo emails", "1 sender", "3 templates"],
      color: "slate",
      popular: false
    },
    {
      name: "Professional",
      price: "$14.99",
      period: "month",
      description: "Most popular for growing teams",
      features: ["10,000/mo emails", "10 senders", "50 templates", "API Access", "Priority Support"],
      color: "purple",
      popular: true
    },
    {
      name: "Enterprise",
      price: "$25.99",
      period: "month",
      description: "For large organizations",
      features: ["50,000/mo emails", "Unlimited senders", "White Label", "Custom Integrations"],
      color: "orange",
      popular: false
    }
  ];

  return (
    <div className="landing-container">
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

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <div className="hero-text animate-on-scroll" 
               style={{ opacity: isVisible[0] ? 1 : 0, transform: isVisible[0] ? 'translateY(0)' : 'translateY(40px)' }}>
            <h1>
              <span className="gradient-text">Transform</span>
              <br />
              <span className="white-text">Email Marketing</span>
              <br />
              <span className="accent-text">Forever</span>
            </h1>
            
            <p>
              Harness the power of AI-driven email marketing. Create, automate, and scale your campaigns with our next-generation platform that grows with your business.
            </p>
            
            <div className="hero-buttons">
              <Link to="/login" className="btn-primary">
                <span>Start Free Trial</span>
                <div className="btn-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </div>
              </Link>
              
              <Link to="/pricing" className="btn-secondary">
                <span>View Plans</span>
                <div className="btn-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </Link>
            </div>
          </div>

          <div className="hero-visual animate-on-scroll"
               style={{ opacity: isVisible[1] ? 1 : 0, transform: isVisible[1] ? 'translateX(0)' : 'translateX(40px)' }}>
            <div className="email-card">
              <div className="email-header">
                <div className="email-avatar">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <div className="email-info">
                  <div className="email-sender">MailsFlow Campaign</div>
                  <div className="email-subject">AI-Generated Newsletter</div>
                </div>
              </div>
              
              <div className="email-stats">
                <div className="stat-item">
                  <div className="stat-header">
                    <span className="stat-label">Open Rate</span>
                    <span className="stat-value">94.2%</span>
                  </div>
                  <div className="stat-bar">
                    <div className="stat-progress" style={{width: '94.2%'}}></div>
                  </div>
                </div>
                
                <div className="stat-item">
                  <div className="stat-header">
                    <span className="stat-label">Click Rate</span>
                    <span className="stat-value">67.8%</span>
                  </div>
                  <div className="stat-bar">
                    <div className="stat-progress stat-progress-alt" style={{width: '67.8%'}}></div>
                  </div>
                </div>
                
                <div className="email-preview">
                  "Transform your inbox experience with personalized content that converts..."
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats-section">
        <div className="stats-container animate-on-scroll"
             style={{ opacity: isVisible[2] ? 1 : 0, transform: isVisible[2] ? 'translateY(0)' : 'translateY(40px)' }}>
          {stats.map((stat, index) => (
            <div key={index} className={`stat-card ${stat.color}`}>
              <div className="stat-number">{stat.number}</div>
              <div className="stat-label">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="section-header animate-on-scroll"
             style={{ opacity: isVisible[3] ? 1 : 0, transform: isVisible[3] ? 'translateY(0)' : 'translateY(40px)' }}>
          <h2>
            <span className="gradient-text">Why Choose MailsFlow?</span>
          </h2>
          <p>
            Experience the future of email marketing with cutting-edge AI, real-time analytics, and seamless automation
          </p>
        </div>

        <div className="features-grid">
          {features.map((feature, index) => (
            <div 
              key={index}
              className={`feature-card ${feature.color} animate-on-scroll`}
              style={{ 
                opacity: isVisible[4 + index] ? 1 : 0, 
                transform: isVisible[4 + index] ? 'translateY(0)' : 'translateY(40px)',
                transitionDelay: `${index * 100}ms`
              }}
            >
              <div className="feature-icon">
                {feature.icon}
              </div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing Preview Section */}
      <section className="pricing-preview-section">
        <div className="section-header animate-on-scroll"
             style={{ opacity: isVisible[11] ? 1 : 0, transform: isVisible[11] ? 'translateY(0)' : 'translateY(40px)' }}>
          <h2>
            <span className="gradient-text">Simple Pricing</span>
            <br />
            <span className="white-text">For Every Business</span>
          </h2>
          <p>
            Choose the perfect plan for your email marketing needs. Start free and scale as you grow.
          </p>
        </div>

        <div className="pricing-cards-preview">
          {pricingPlans.map((plan, index) => (
            <div 
              key={index}
              className={`pricing-card-preview ${plan.color} ${plan.popular ? 'popular' : ''} animate-on-scroll`}
              style={{ 
                opacity: isVisible[12 + index] ? 1 : 0, 
                transform: isVisible[12 + index] ? 'translateY(0)' : 'translateY(40px)',
                transitionDelay: `${index * 150}ms`
              }}
            >
              {plan.popular && (
                <div className="popular-badge">Most Popular</div>
              )}
              
              <div className="plan-header">
                <h3>{plan.name}</h3>
                <p>{plan.description}</p>
              </div>
              
              <div className="plan-price">
                <span className="price-amount">{plan.price}</span>
                <span className="price-period">/{plan.period}</span>
              </div>
              
              <div className="plan-features">
                {plan.features.map((feature, featureIndex) => (
                  <div key={featureIndex} className="feature-item">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span>{feature}</span>
                  </div>
                ))}
              </div>
              
              <button className="plan-button">
                🚀 Choose {plan.name}
              </button>
            </div>
          ))}
        </div>

        <div className="pricing-cta animate-on-scroll"
             style={{ opacity: isVisible[15] ? 1 : 0, transform: isVisible[15] ? 'translateY(0)' : 'translateY(40px)' }}>
          <Link to="/pricing" className="view-all-pricing">
            <span>View All Pricing Plans</span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </Link>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="testimonials-section">
        <div className="section-header animate-on-scroll"
             style={{ opacity: isVisible[16] ? 1 : 0, transform: isVisible[16] ? 'translateY(0)' : 'translateY(40px)' }}>
          <h2>
            <span className="gradient-text">Loved by Thousands</span>
            <br />
            <span className="white-text">of Businesses</span>
          </h2>
          <p>
            See what our customers have to say about their experience with MailsFlow
          </p>
        </div>

        <div className="testimonials-grid">
          {testimonials.map((testimonial, index) => (
            <div 
              key={index}
              className="testimonial-card animate-on-scroll"
              style={{ 
                opacity: isVisible[17 + index] ? 1 : 0, 
                transform: isVisible[17 + index] ? 'translateY(0)' : 'translateY(40px)',
                transitionDelay: `${index * 150}ms`
              }}
            >
              <div className="testimonial-rating">
                {[...Array(testimonial.rating)].map((_, i) => (
                  <span key={i} className="star">⭐</span>
                ))}
              </div>
              
              <p className="testimonial-quote">"{testimonial.quote}"</p>
              
              <div className="testimonial-author">
                <div className="author-avatar">
                  <span>{testimonial.avatar}</span>
                </div>
                <div className="author-info">
                  <strong>{testimonial.author}</strong>
                  <span>{testimonial.position}, {testimonial.company}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-content animate-on-scroll"
             style={{ opacity: isVisible[20] ? 1 : 0, transform: isVisible[20] ? 'translateY(0)' : 'translateY(40px)' }}>
          <div className="cta-card">
            <h2>
              Ready to <span className="gradient-text">Transform</span> Your Email Marketing?
            </h2>
            <p>
              Join thousands of businesses using MailsFlow to grow their audience, increase engagement, and drive revenue through intelligent email marketing.
            </p>
            
            <div className="cta-buttons">
              <Link to="/login" className="btn-primary">
                <span>Get Started Free</span>
                <div className="btn-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </div>
              </Link>
              
              <Link to="/contact" className="btn-outline">
                <span>Contact Sales</span>
                <div className="btn-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-3.582 8-8 8a8.955 8.955 0 01-4.946-1.524A11.005 11.005 0 014.932 23 11.001 11.001 0 016 12c0-4.418 3.582-8 8-8s8 3.582 8 8z" />
                  </svg>
                </div>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer Component */}
      <Footer />
    </div>
  );
}

export default Landing;