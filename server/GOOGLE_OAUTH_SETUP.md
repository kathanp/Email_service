# Google OAuth Setup Guide for Email Bot

This guide will help you set up Google OAuth for user authentication in your Email Bot application.

## 🎯 What We're Setting Up

- **Google OAuth for User Login**: Users can sign in with their Google accounts
- **AWS SES for Email Sending**: Emails are sent via AWS SES using the user's Google email as sender
- **MongoDB Atlas**: Database for storing user data, templates, and campaigns

## 📋 Prerequisites

1. Google Cloud Console account
2. MongoDB Atlas account
3. AWS account with SES configured

## 🔧 Step-by-Step Setup

### 1. Google OAuth Setup

#### 1.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your Project ID

#### 1.2 Enable Required APIs

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for and enable these APIs:
   - **Google+ API** (for user profile information)
   - **Google OAuth2 API** (should be enabled automatically)

#### 1.3 Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Web application" as the application type
4. Set the following:
   - **Name**: Email Bot OAuth Client
   - **Authorized redirect URIs**: `http://localhost:8000/api/v1/google-auth/callback`
5. Click "Create"
6. **Save your Client ID and Client Secret** - you'll need these for the .env file

### 2. MongoDB Atlas Setup

#### 2.1 Create MongoDB Atlas Cluster

1. Go to [MongoDB Atlas](https://cloud.mongodb.com/)
2. Create a new cluster (free tier is fine)
3. Create a database user with read/write permissions
4. Get your connection string

#### 2.2 Update MongoDB Connection

Replace the MongoDB URL in your `.env` file:

```
MONGODB_URL=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/email_bot?retryWrites=true&w=majority
```

### 3. AWS SES Setup

#### 3.1 Configure AWS SES

1. Go to [AWS SES Console](https://console.aws.amazon.com/ses/)
2. Verify your sender email address or domain
3. Create IAM user with SES permissions
4. Get your AWS Access Key ID and Secret Access Key

#### 3.2 Update AWS Credentials

Replace the AWS credentials in your `.env` file:

```
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=us-east-1
DEFAULT_SENDER_EMAIL=your-verified-sender-email@domain.com
```

### 4. Update Environment Variables

Edit the `server/.env` file and replace the placeholder values:

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-actual-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/google-auth/callback

# MongoDB Configuration
MONGODB_URL=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/email_bot?retryWrites=true&w=majority
DATABASE_NAME=email_bot

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS SES Configuration
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
DEFAULT_SENDER_EMAIL=your-verified-email@domain.com

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

### 5. Restart the Application

After updating the `.env` file:

```bash
# Kill existing servers
pkill -f uvicorn
pkill -f "npm start"

# Start backend server
cd server
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, start frontend
cd client
npm start
```

## 🧪 Testing the Setup

### 1. Test Backend Health

```bash
curl http://localhost:8000/health
```

Should return: `{"status":"healthy","database":"connected"}`

### 2. Test Google OAuth

1. Open http://localhost:3000 in your browser
2. Click "Sign in with Google"
3. You should be redirected to Google's OAuth consent screen
4. After authorization, you should be logged in

### 3. Test Email Sending

1. Create an email template
2. Upload a contacts file
3. Send a test campaign
4. Check your email for the test message

## 🔒 Security Notes

1. **Never commit your .env file** to version control
2. **Use strong, unique secrets** for JWT and other sensitive data
3. **Verify sender emails** in AWS SES before sending
4. **Use HTTPS in production** and update redirect URIs accordingly

## 🚀 Production Deployment

For production deployment:

1. **Update redirect URIs** in Google Cloud Console to your production domain
2. **Use environment variables** instead of .env file
3. **Enable HTTPS** and update CORS origins
4. **Use a proper domain** for your application
5. **Set up proper logging** and monitoring

## 🆘 Troubleshooting

### Common Issues

1. **"Invalid redirect URI" error**

   - Make sure the redirect URI in Google Cloud Console matches exactly
   - Check for trailing slashes or typos

2. **"Database connection failed"**

   - Verify MongoDB connection string
   - Check if your IP is whitelisted in MongoDB Atlas

3. **"Email sending failed"**

   - Verify AWS SES credentials
   - Make sure sender email is verified in SES
   - Check SES sending limits

4. **"CORS error"**
   - Verify CORS_ORIGINS in .env file
   - Make sure frontend and backend URLs match

### Getting Help

If you encounter issues:

1. Check the browser console for errors
2. Check the backend logs for detailed error messages
3. Verify all environment variables are set correctly
4. Test each service individually (Google OAuth, MongoDB, AWS SES)

## 📚 Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [AWS SES Documentation](https://docs.aws.amazon.com/ses/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

🎉 **You're all set!** Your Email Bot is now configured with Google OAuth for user authentication and AWS SES for reliable email sending.
