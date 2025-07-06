# 🚀 Email Bot Deployment Checklist

## ✅ Pre-Deployment Checklist

### 1. Environment Variables Setup

- [ ] Generate environment variables using `python3 generate_env_vars.py`
- [ ] Copy `.env.template` to `.env` for local development
- [ ] Fill in your actual credentials in the local `.env` file

### 2. Google OAuth Configuration

- [ ] Go to [Google Cloud Console](https://console.cloud.google.com/)
- [ ] Select your project
- [ ] Go to "APIs & Services" > "Credentials"
- [ ] Edit your OAuth 2.0 Client ID
- [ ] Add your production domain to "Authorized redirect URIs":
  - For Vercel: `https://your-app.vercel.app/api/v1/google-auth/callback`
  - For Railway: `https://your-app.railway.app/api/v1/google-auth/callback`
  - For Heroku: `https://your-app.herokuapp.com/api/v1/google-auth/callback`

### 3. MongoDB Setup

- [ ] Ensure your MongoDB Atlas cluster is running
- [ ] Check that your cluster allows connections from your deployment platform
- [ ] Verify your connection string is correct

### 4. AWS SES Setup

- [ ] Verify your sender email address in AWS SES
- [ ] Check that your AWS credentials have SES permissions
- [ ] Test email sending locally

### 5. Stripe Setup

- [ ] Get your Stripe API keys from the dashboard
- [ ] Set up webhook endpoints (if needed)
- [ ] Test payment flow with test cards

## 🚀 Deployment Steps

### For Vercel:

1. [ ] Go to [vercel.com](https://vercel.com)
2. [ ] Create a new project
3. [ ] Connect your GitHub repository
4. [ ] Go to Settings > Environment Variables
5. [ ] Add all environment variables from your generated list
6. [ ] Update `GOOGLE_REDIRECT_URI` to your Vercel domain
7. [ ] Deploy!

### For Railway:

1. [ ] Go to [railway.app](https://railway.app)
2. [ ] Create a new project
3. [ ] Connect your GitHub repository
4. [ ] Go to Variables tab
5. [ ] Add all environment variables from your generated list
6. [ ] Update `GOOGLE_REDIRECT_URI` to your Railway domain
7. [ ] Deploy!

### For Heroku:

1. [ ] Install Heroku CLI
2. [ ] Create app: `heroku create your-app-name`
3. [ ] Add environment variables using the generated commands
4. [ ] Update `GOOGLE_REDIRECT_URI` to your Heroku domain
5. [ ] Deploy: `git push heroku main`

## 🧪 Post-Deployment Testing

### 1. Basic Functionality

- [ ] Test the homepage loads correctly
- [ ] Test Google OAuth login
- [ ] Test user registration/login
- [ ] Test dashboard access

### 2. Email Functionality

- [ ] Test email template creation
- [ ] Test contact upload
- [ ] Test email campaign sending
- [ ] Verify emails are received

### 3. Payment Functionality

- [ ] Test subscription creation
- [ ] Test payment processing
- [ ] Test webhook handling (if applicable)

### 4. Error Handling

- [ ] Check application logs for errors
- [ ] Test error pages
- [ ] Verify proper error messages

## 🔧 Troubleshooting

### Common Issues:

1. **"Invalid redirect URI" error**

   - Solution: Update Google OAuth redirect URI in Google Cloud Console

2. **"Database connection failed"**

   - Solution: Check MongoDB connection string and network access

3. **"Email sending failed"**

   - Solution: Verify AWS SES credentials and sender email verification

4. **"CORS error"**

   - Solution: Update CORS_ORIGINS with your production domain

5. **"Environment variable not found"**
   - Solution: Check that all environment variables are set in your hosting platform

## 📞 Support

If you encounter issues:

1. Check the deployment platform logs
2. Verify all environment variables are set correctly
3. Test each service individually
4. Check the browser console for frontend errors

## 🎉 Success!

Once everything is working:

- [ ] Set up monitoring (optional)
- [ ] Configure custom domain (optional)
- [ ] Set up SSL certificate (usually automatic)
- [ ] Test thoroughly with real users
- [ ] Monitor performance and errors

---

**Remember:** Never commit your `.env` file to version control. Always use environment variables in production!
