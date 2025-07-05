#!/usr/bin/env python3
"""
Deployment Setup Script
This script helps set up the email bot for production deployment.
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def check_requirements():
    """Check if all requirements are met for deployment."""
    print("🔍 Checking deployment requirements...")
    
    requirements = {
        "backend": {
            "python": "3.8+",
            "dependencies": ["fastapi", "uvicorn", "stripe", "pymongo", "python-jose"]
        },
        "frontend": {
            "node": "16+",
            "dependencies": ["react", "react-router-dom"]
        }
    }
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print(f"❌ Python version {python_version.major}.{python_version.minor} is too old. Need 3.8+")
        return False
    else:
        print(f"✅ Python version {python_version.major}.{python_version.minor} is compatible")
    
    # Check Node.js version
    try:
        node_version = subprocess.check_output(["node", "--version"], text=True).strip()
        print(f"✅ Node.js version {node_version} found")
    except:
        print("❌ Node.js not found. Please install Node.js 16+")
        return False
    
    return True

def create_env_template():
    """Create environment template file."""
    print("\n📝 Creating environment template...")
    
    env_template = """# Email Bot Environment Configuration
# Copy this file to .env and fill in your actual values

# MongoDB Configuration
MONGODB_URL=mongodb+srv://your_username:your_password@your_cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=email_bot

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS Configuration (for SES)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
DEFAULT_SENDER_EMAIL=your_default_sender@example.com

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=https://yourdomain.com/api/v1/google-auth/callback

# Stripe Configuration
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# CORS Configuration
CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]
"""
    
    with open(".env.template", "w") as f:
        f.write(env_template)
    
    print("✅ Created .env.template file")

def create_production_config():
    """Create production configuration files."""
    print("\n⚙️  Creating production configuration...")
    
    # Production requirements
    prod_requirements = """fastapi==0.104.1
uvicorn[standard]==0.24.0
stripe==12.3.0
pymongo==4.6.0
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
boto3==1.34.0
google-auth==2.23.4
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.1.1
"""
    
    with open("server/requirements.txt", "w") as f:
        f.write(prod_requirements)
    
    # Docker configuration
    dockerfile = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server/ .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile)
    
    # Docker Compose
    docker_compose = """version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=${MONGODB_URL}
      - SECRET_KEY=${SECRET_KEY}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    volumes:
      - ./server:/app
    restart: unless-stopped

  frontend:
    build: ./client
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped
"""
    
    with open("docker-compose.yml", "w") as f:
        f.write(docker_compose)
    
    print("✅ Created production configuration files")

def create_deployment_guide():
    """Create deployment guide."""
    print("\n📚 Creating deployment guide...")
    
    guide = """# Email Bot Deployment Guide

## 🚀 Quick Deploy Options

### Option 1: Railway (Recommended for beginners)
1. Fork this repository to your GitHub
2. Go to [railway.app](https://railway.app)
3. Connect your GitHub repository
4. Add environment variables from .env.template
5. Deploy!

### Option 2: Heroku
1. Install Heroku CLI
2. Create Heroku app: `heroku create your-app-name`
3. Add environment variables: `heroku config:set KEY=value`
4. Deploy: `git push heroku main`

### Option 3: DigitalOcean App Platform
1. Go to [digitalocean.com](https://digitalocean.com)
2. Create new app from GitHub repository
3. Configure environment variables
4. Deploy!

### Option 4: AWS/GCP/Azure
1. Use Docker containers
2. Deploy to ECS/GKE/AKS
3. Set up load balancer
4. Configure domain and SSL

## 🔧 Environment Setup

### Required Environment Variables:
- MONGODB_URL: Your MongoDB connection string
- SECRET_KEY: JWT secret key (generate with: `openssl rand -hex 32`)
- STRIPE_SECRET_KEY: Your Stripe secret key
- AWS_ACCESS_KEY_ID: AWS SES access key
- AWS_SECRET_ACCESS_KEY: AWS SES secret key
- GOOGLE_CLIENT_ID: Google OAuth client ID
- GOOGLE_CLIENT_SECRET: Google OAuth client secret

### Optional:
- CORS_ORIGINS: Allowed origins for CORS
- DATABASE_NAME: MongoDB database name

## 🌐 Domain Setup

1. Purchase domain (recommended: emailcampaignpro.com)
2. Point DNS to your hosting provider
3. Set up SSL certificate (automatic on most platforms)
4. Update CORS_ORIGINS with your domain

## 📊 Monitoring

### Recommended Tools:
- Sentry for error tracking
- Google Analytics for user tracking
- Stripe Dashboard for payment monitoring
- MongoDB Atlas for database monitoring

## 🔒 Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use HTTPS in production
- [ ] Set up proper CORS origins
- [ ] Enable Stripe webhooks
- [ ] Set up rate limiting
- [ ] Configure proper logging
- [ ] Set up backup strategy

## 💰 Monetization Setup

1. Complete Stripe account verification
2. Set up webhook endpoints
3. Test payment flow with test cards
4. Monitor subscription metrics
5. Set up email notifications for payments

## 🚨 Important Notes

- Always use environment variables for secrets
- Never commit .env files to version control
- Set up proper logging and monitoring
- Test thoroughly before going live
- Have a backup and recovery plan

## 📞 Support

For deployment issues:
1. Check the logs in your hosting platform
2. Verify all environment variables are set
3. Test the API endpoints manually
4. Check database connectivity
"""
    
    with open("DEPLOYMENT_GUIDE.md", "w") as f:
        f.write(guide)
    
    print("✅ Created DEPLOYMENT_GUIDE.md")

def main():
    """Main deployment setup function."""
    print("🚀 Email Bot Deployment Setup")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements not met. Please fix the issues above.")
        return
    
    # Create configuration files
    create_env_template()
    create_production_config()
    create_deployment_guide()
    
    print("\n🎉 Deployment setup complete!")
    print("\n📋 Next steps:")
    print("1. Copy .env.template to .env and fill in your values")
    print("2. Run: python server/setup_stripe_products.py")
    print("3. Choose your deployment platform")
    print("4. Follow the DEPLOYMENT_GUIDE.md")
    print("\n💡 Recommended: Start with Railway for easy deployment!")

if __name__ == "__main__":
    main() 