import os
import json
import base64
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import httpx
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from ..core.config import settings

logger = logging.getLogger(__name__)

class GmailOAuthService:
    """Gmail OAuth service for user authentication and email sending."""
    
    # Gmail API scopes
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
    ]
    
    def __init__(self):
        """Initialize Gmail OAuth service."""
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
        
    def get_authorization_url(self, state: str = None) -> Dict:
        """Get Gmail OAuth authorization URL."""
        try:
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "redirect_uris": [self.redirect_uri],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                },
                scopes=self.SCOPES
            )
            
            authorization_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=state
            )
            
            return {
                'success': True,
                'authorization_url': authorization_url
            }
            
        except Exception as e:
            logger.error(f"Error generating authorization URL: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def exchange_code_for_tokens(self, authorization_code: str) -> Dict:
        """Exchange authorization code for access and refresh tokens."""
        try:
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': authorization_code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(token_url, data=data)
                response.raise_for_status()
                token_data = response.json()
            
            # Get user info
            user_info = await self.get_user_info(token_data['access_token'])
            
            return {
                'success': True,
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token'),
                'expires_in': token_data['expires_in'],
                'token_type': token_data['token_type'],
                'user_email': user_info.get('email'),
                'user_name': user_info.get('name')
            }
            
        except Exception as e:
            logger.error(f"Error exchanging code for tokens: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_user_info(self, access_token: str) -> Dict:
        """Get user information from Google."""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    'https://www.googleapis.com/oauth2/v2/userinfo',
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return {}
    
    def refresh_access_token(self, refresh_token: str) -> Dict:
        """Refresh access token using refresh token."""
        try:
            credentials = Credentials(
                None,  # No access token initially
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            
            credentials.refresh(Request())
            
            return {
                'success': True,
                'access_token': credentials.token,
                'expires_in': credentials.expiry.timestamp() if credentials.expiry else None
            }
            
        except Exception as e:
            logger.error(f"Error refreshing access token: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def send_email(self, access_token: str, to_email: str, subject: str, 
                        body: str, html_body: Optional[str] = None, user_id: str = None) -> Dict:
        """Send email using Gmail API."""
        try:
            # Create Gmail service
            credentials = Credentials(access_token)
            service = build('gmail', 'v1', credentials=credentials)
            
            # Create message
            message = MIMEMultipart('alternative')
            message['to'] = to_email
            message['subject'] = subject
            
            # Add text part
            text_part = MIMEText(body, 'plain')
            message.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                message.attach(html_part)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send email
            sent_message = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f"Email sent successfully to {to_email}. Message ID: {sent_message['id']}")
            
            return {
                'success': True,
                'message_id': sent_message['id'],
                'to_email': to_email,
                'user_id': user_id,
                'timestamp': datetime.utcnow()
            }
            
        except HttpError as e:
            error_details = json.loads(e.content.decode())
            logger.error(f"Gmail API error for {to_email}: {error_details}")
            
            return {
                'success': False,
                'error_code': 'GMAIL_API_ERROR',
                'error_message': error_details.get('error', {}).get('message', str(e)),
                'to_email': to_email,
                'user_id': user_id,
                'timestamp': datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Unexpected error sending email to {to_email}: {e}")
            return {
                'success': False,
                'error_code': 'UNKNOWN_ERROR',
                'error_message': str(e),
                'to_email': to_email,
                'user_id': user_id,
                'timestamp': datetime.utcnow()
            }
    
    async def send_bulk_emails(self, access_token: str, emails: list, user_id: str = None) -> Dict:
        """Send bulk emails with rate limiting."""
        results = {
            'total': len(emails),
            'successful': 0,
            'failed': 0,
            'errors': [],
            'user_id': user_id,
            'start_time': datetime.utcnow(),
            'end_time': None
        }
        
        logger.info(f"Starting bulk email campaign for user {user_id}: {len(emails)} recipients")
        
        # Process emails with rate limiting
        import asyncio
        semaphore = asyncio.Semaphore(5)  # Gmail has stricter rate limits
        
        async def send_with_rate_limit(email_data):
            async with semaphore:
                result = await self.send_email(
                    access_token=access_token,
                    to_email=email_data['email'],
                    subject=email_data['subject'],
                    body=email_data['body'],
                    html_body=email_data.get('html_body'),
                    user_id=user_id
                )
                
                if result['success']:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(result)
                
                # Rate limiting: wait 0.2 seconds between emails for Gmail
                await asyncio.sleep(0.2)
                return result
        
        # Create tasks for all emails
        tasks = [send_with_rate_limit(email) for email in emails]
        
        # Execute all tasks
        await asyncio.gather(*tasks, return_exceptions=True)
        
        results['end_time'] = datetime.utcnow()
        duration = (results['end_time'] - results['start_time']).total_seconds()
        
        logger.info(f"Bulk email campaign completed for user {user_id} in {duration:.2f} seconds")
        logger.info(f"Results: {results['successful']} successful, {results['failed']} failed")
        
        return results
    
    def is_token_expired(self, expires_at: datetime) -> bool:
        """Check if access token is expired."""
        if not expires_at:
            return True
        return datetime.utcnow() >= expires_at 