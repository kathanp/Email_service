import React from 'react';
import { Link } from 'react-router-dom';
import './staticPricing.css';
import Footer from '../Component/footer';
import Navbar from '../Component/navbar';

function StaticPricing() {
  const plans = [
    {
      name: "Free",
      price: "$0",
      period: "month",
      description: "Perfect for getting started",
      features: [
        { icon: "email", text: "100/mo emails" },
        { icon: "user", text: "1 sender" },
        { icon: "template", text: "3 templates" },
        { icon: "analytics", text: "Basic analytics" },
        { icon: "support", text: "Email support" }
      ],
      buttonText: "🚀 CHOOSE FREE",
      buttonClass: "btn-free",
      popular: false,
      colorScheme: "slate"
    },
    {
      name: "Starter",
      price: "$4.99",
      period: "month",
      description: "Great for small businesses",
      features: [
        { icon: "email", text: "1,000/mo emails" },
        { icon: "users", text: "3 senders" },
        { icon: "template", text: "10 templates" },
        { icon: "analytics", text: "Advanced analytics" },
        { icon: "test", text: "A/B testing" },
        { icon: "automation", text: "Basic automation" }
      ],
      buttonText: "🚀 CHOOSE STARTER",
      buttonClass: "btn-starter",
      popular: false,
      colorScheme: "cyan"
    },
    {
      name: "Professional",
      price: "$14.99",
      period: "month",
      description: "Most popular for growing teams",
      features: [
        { icon: "email", text: "10,000/mo emails" },
        { icon: "users", text: "10 senders" },
        { icon: "template", text: "50 templates" },
        { icon: "api", text: "API Access" },
        { icon: "priority", text: "Priority Support" },
        { icon: "segment", text: "Advanced segmentation" },
        { icon: "reports", text: "Custom reports" },
        { icon: "ai", text: "AI optimization" }
      ],
      buttonText: "🚀 CHOOSE PROFESSIONAL",
      buttonClass: "btn-professional",
      popular: true,
      colorScheme: "purple"
    },
    {
      name: "Enterprise",
      price: "$25.99",
      period: "month",
      description: "For large organizations",
      features: [
        { icon: "email", text: "50,000/mo emails" },
        { icon: "unlimited", text: "Unlimited senders" },
        { icon: "template", text: "Unlimited templates" },
        { icon: "api", text: "API Access" },
        { icon: "priority", text: "Priority Support" },
        { icon: "whitelabel", text: "White Label" },
        { icon: "integrations", text: "Custom Integrations" },
        { icon: "security", text: "Enterprise security" },
        { icon: "manager", text: "Dedicated manager" }
      ],
      buttonText: "🚀 CHOOSE ENTERPRISE",
      buttonClass: "btn-enterprise",
      popular: false,
      colorScheme: "orange"
    }
  ];

  const getIcon = (iconName) => {
    const icons = {
      email: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      ),
      user: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      ),
      users: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      ),
      template: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
      analytics: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      support: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-3.582 8-8 8a8.955 8.955 0 01-4.946-1.524A11.005 11.005 0 014.932 23 11.001 11.001 0 016 12c0-4.418 3.582-8 8-8s8 3.582 8 8z" />
        </svg>
      ),
      test: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
        </svg>
      ),
      automation: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      api: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
      ),
      priority: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
        </svg>
      ),
      segment: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
        </svg>
      ),
      reports: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
      ai: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      ),
      unlimited: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
      ),
      whitelabel: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
        </svg>
      ),
      integrations: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
        </svg>
      ),
      security: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
      ),
      manager: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )
    };
    return icons[iconName] || icons.email;
  };

  return (
    <div className="pricing-container navbar-offset">
      {/* Navigation */}
      <Navbar />

      {/* Header Section */}
      <section className="pricing-header">
        <div className="header-content">
          <h1>
            <span className="gradient-text">Simple Pricing</span>
            <br />
            <span className="white-text">For Every Business</span>
          </h1>
          
          <p>
            Choose the perfect plan for your email marketing needs. Start free and scale as you grow.
          </p>

          {/* Billing Toggle - Static Monthly */}
          <div className="billing-toggle">
            <span className="toggle-label active">
              Monthly
            </span>
            <div className="toggle-switch">
              <div className="toggle-slider"></div>
            </div>
            <span className="toggle-label">
              Yearly
              <span className="save-badge">Save 20%</span>
            </span>
          </div>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="pricing-cards">
        <div className="cards-container">
          {plans.map((plan, index) => (
            <div
              key={index}
              className={`pricing-card ${plan.colorScheme} ${plan.popular ? 'popular' : ''}`}
            >
              {/* Popular Badge */}
              {plan.popular && (
                <div className="popular-badge">
                  Most Popular
                </div>
              )}

              {/* Card Content */}
              <div className="card-content">
                {/* Plan Header */}
                <div className="plan-header">
                  <h3>{plan.name}</h3>
                  <p>{plan.description}</p>
                </div>

                {/* Price */}
                <div className="plan-price">
                  <span className="price-amount">{plan.price}</span>
                  <span className="price-period">/{plan.period}</span>
                </div>

                {/* Features */}
                <div className="plan-features">
                  {plan.features.map((feature, featureIndex) => (
                    <div key={featureIndex} className="feature-item">
                      <div className="feature-icon">
                        {getIcon(feature.icon)}
                      </div>
                      <span className="feature-text">{feature.text}</span>
                    </div>
                  ))}
                </div>

                {/* CTA Button */}
                <button className={`plan-button ${plan.buttonClass}`}>
                  {plan.buttonText}
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Features Comparison */}
      <section className="features-comparison">
        <div className="comparison-content">
          <div className="comparison-header">
            <h2>
              <span className="gradient-text">Compare All Features</span>
            </h2>
            <p>See what's included in each plan</p>
          </div>

          <div className="comparison-table">
            <div className="table-header">
              <div className="feature-col">Features</div>
              <div className="plan-col slate">Free</div>
              <div className="plan-col cyan">Starter</div>
              <div className="plan-col purple">Professional</div>
              <div className="plan-col orange">Enterprise</div>
            </div>

            {[
              { feature: "Monthly Emails", free: "100", starter: "1K", pro: "10K", enterprise: "50K" },
              { feature: "Senders", free: "1", starter: "3", pro: "10", enterprise: "Unlimited" },
              { feature: "Templates", free: "3", starter: "10", pro: "50", enterprise: "Unlimited" },
              { feature: "API Access", free: "❌", starter: "❌", pro: "✅", enterprise: "✅" },
              { feature: "Priority Support", free: "❌", starter: "❌", pro: "✅", enterprise: "✅" },
              { feature: "White Label", free: "❌", starter: "❌", pro: "❌", enterprise: "✅" },
              { feature: "Custom Integrations", free: "❌", starter: "❌", pro: "❌", enterprise: "✅" }
            ].map((row, index) => (
              <div key={index} className="table-row">
                <div className="feature-col">{row.feature}</div>
                <div className="plan-col slate">{row.free}</div>
                <div className="plan-col cyan">{row.starter}</div>
                <div className="plan-col purple">{row.pro}</div>
                <div className="plan-col orange">{row.enterprise}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="faq-section">
        <div className="faq-content">
          <div className="faq-header">
            <h2>
              <span className="gradient-text">Frequently Asked Questions</span>
            </h2>
          </div>

          <div className="faq-grid">
            {[
              {
                question: "Can I change my plan anytime?",
                answer: "Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately."
              },
              {
                question: "What happens if I exceed my email limit?",
                answer: "We'll notify you when you're approaching your limit. You can upgrade or purchase additional emails."
              },
              {
                question: "Do you offer refunds?",
                answer: "Yes, we offer a 30-day money-back guarantee for all paid plans. No questions asked."
              },
              {
                question: "Is there a setup fee?",
                answer: "No setup fees ever. What you see is what you pay. Simple and transparent pricing."
              }
            ].map((faq, index) => (
              <div key={index} className="faq-item">
                <h3>{faq.question}</h3>
                <p>{faq.answer}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="pricing-cta">
        <div className="cta-content">
          <div className="cta-card">
            <h2>
              Ready to <span className="gradient-text">Get Started?</span>
            </h2>
            <p>
              Start your free trial today. No credit card required.
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

      {/* Footer */}
      <Footer />
    </div>
  );
}

export default StaticPricing;