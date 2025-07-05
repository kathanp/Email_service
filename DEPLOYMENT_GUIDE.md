# Email Bot Deployment Guide

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
