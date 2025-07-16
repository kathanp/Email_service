# Render.com Deployment Guide

## Overview

This guide will help you deploy your Email Bot application to Render.com. The application consists of:

- **Backend**: FastAPI Python service
- **Frontend**: React static site

## Prerequisites

- GitHub account linked to Render.com ✓ (already done)
- MongoDB Atlas database (for production)
- Environment variables configured

## Deployment Steps

### 1. Prepare Environment Variables

Create these environment variables in Render.com for your **backend service**:

#### Required Environment Variables:

```
# Database
MONGODB_URL=mongodb+srv://your-connection-string

# Security
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# Email Services
GMAIL_CLIENT_ID=your-gmail-client-id
GMAIL_CLIENT_SECRET=your-gmail-client-secret

# AWS SES (if using)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_DEFAULT_REGION=us-east-1

# Stripe
STRIPE_SECRET_KEY=sk_live_or_test_key
STRIPE_PUBLISHABLE_KEY=pk_live_or_test_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=https://email-bot-backend.onrender.com/api/v1/google-auth/callback

# CORS
FRONTEND_URL=https://email-bot-frontend.onrender.com
```

### 2. Deploy Backend Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `email-bot-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python3 -m uvicorn server.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free/Starter
5. Add all environment variables from above
6. Deploy

### 3. Deploy Frontend Service

1. In Render Dashboard, click "New" → "Static Site"
2. Connect your GitHub repository
3. Configure the static site:
   - **Name**: `email-bot-frontend`
   - **Build Command**: `cd client && npm ci && npm run build`
   - **Publish Directory**: `client/build`
   - **Plan**: Free
4. Add environment variable:
   - `REACT_APP_API_URL`: `https://email-bot-backend.onrender.com`
5. Deploy

### 4. Alternative: Using render.yaml (Infrastructure as Code)

If you prefer to use the `render.yaml` file:

1. Push the `render.yaml` file to your repository
2. In Render Dashboard, click "New" → "Blueprint"
3. Connect your repository and select the `render.yaml` file
4. Add environment variables through the Render dashboard
5. Deploy both services

### 5. Post-Deployment Configuration

#### Update CORS Settings

Ensure your backend CORS settings include your frontend URL:

```python
# In your FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://email-bot-frontend.onrender.com",
        "http://localhost:3000"  # for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Update OAuth Redirect URIs

Update your Google OAuth app settings:

- Add `https://email-bot-backend.onrender.com/api/v1/google-auth/callback` to authorized redirect URIs

#### Update Stripe Webhooks

Update your Stripe webhook endpoint:

- Point to `https://email-bot-backend.onrender.com/api/webhooks/stripe`

## Important Notes

### Free Tier Limitations

- **Backend**: May spin down after 15 minutes of inactivity (cold starts)
- **Frontend**: No limitations on static sites
- **Database**: Use MongoDB Atlas free tier (512MB limit)

### Custom Domains (Optional)

1. Purchase a domain
2. In Render Dashboard → Service Settings → Custom Domains
3. Add your domain and follow DNS configuration

### SSL Certificates

Render automatically provides SSL certificates for all deployments.

### Monitoring

- Use Render's built-in logs and metrics
- Set up health check endpoint (`/health`) for monitoring

## Troubleshooting

### Common Issues:

1. **Build Failures**:

   - Check build logs in Render dashboard
   - Ensure all dependencies are in requirements.txt/package.json

2. **Environment Variables**:

   - Double-check all required env vars are set
   - Use Render's environment variable editor

3. **CORS Errors**:

   - Update CORS origins in your FastAPI app
   - Ensure frontend URL matches exactly

4. **Database Connection**:
   - Verify MongoDB Atlas connection string
   - Check IP whitelist (0.0.0.0/0 for Render)

### Support

- Render Documentation: https://render.com/docs
- GitHub Issues: Create issues in your repository
- Render Community: https://community.render.com

## Scaling

For production workloads, consider upgrading to:

- Starter ($7/month) or Standard ($25/month) plans for backend
- Pro static site plans for advanced features
