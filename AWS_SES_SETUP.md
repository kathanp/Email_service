# AWS SES Setup Guide for Sender Email Verification

## Overview

This guide will help you set up AWS SES (Simple Email Service) to verify sender emails for your mass email service.

## Step 1: Create AWS Account

1. Go to [AWS Console](https://aws.amazon.com/)
2. Create a new account or sign in to existing account
3. Complete the registration process

## Step 2: Access AWS SES

1. Go to AWS Console
2. Search for "SES" or "Simple Email Service"
3. Click on "Simple Email Service"

## Step 3: Verify Your Domain (Recommended)

1. In SES Console, go to "Verified identities"
2. Click "Create identity"
3. Choose "Domain"
4. Enter your domain (e.g., `yourdomain.com`)
5. Follow the DNS verification steps
6. Add the provided DNS records to your domain

## Step 4: Verify Individual Email Addresses (Alternative)

If you don't have a domain, you can verify individual email addresses:

1. In SES Console, go to "Verified identities"
2. Click "Create identity"
3. Choose "Email address"
4. Enter the email address you want to verify
5. Check the email inbox and click the verification link

## Step 5: Create IAM User for API Access

1. Go to AWS Console → IAM
2. Click "Users" → "Create user"
3. Enter username: `ses-email-bot`
4. Select "Programmatic access"
5. Click "Next: Permissions"
6. Click "Attach existing policies directly"
7. Search for "SES" and select "AmazonSESFullAccess"
8. Click "Next: Tags" → "Next: Review" → "Create user"
9. **IMPORTANT**: Save the Access Key ID and Secret Access Key

## Step 6: Configure Environment Variables

Create a `.env` file in your project root with:

```env
# AWS SES Configuration
AWS_ACCESS_KEY_ID=your_access_key_id_here
AWS_SECRET_ACCESS_KEY=your_secret_access_key_here
AWS_REGION=us-east-1
DEFAULT_SENDER_EMAIL=your_verified_email@yourdomain.com

# Other existing variables...
MONGODB_URL=your_mongodb_url
SECRET_KEY=your_secret_key
# ... rest of your existing config
```

## Step 7: Test the Setup

1. Restart your backend server
2. Go to Sender Management in your app
3. Add a new sender email
4. Check the email inbox for verification email
5. Click the verification link

## Important Notes:

- **Sandbox Mode**: New SES accounts start in sandbox mode
  - You can only send to verified email addresses
  - To send to any email, request production access
- **Verification**: All sender emails must be verified before sending
- **Rate Limits**: SES has sending rate limits (check AWS console)
- **Costs**: SES charges per email sent (very low cost)

## Troubleshooting:

1. **"Invalid security token"**: Check AWS credentials
2. **"Email not verified"**: Verify the email in SES console
3. **"Rate exceeded"**: Check SES sending limits
4. **"Sandbox mode"**: Request production access if needed

## Production Access Request:

To send to any email address (not just verified ones):

1. Go to SES Console → Account dashboard
2. Click "Request production access"
3. Fill out the form explaining your use case
4. Wait for AWS approval (usually 24-48 hours)

## Security Best Practices:

1. Never commit `.env` file to git
2. Use IAM roles instead of access keys in production
3. Regularly rotate access keys
4. Monitor SES usage and costs
