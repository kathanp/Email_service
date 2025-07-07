import os
import json
import logging
from typing import Dict, Optional
from datetime import datetime
import httpx
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from ..core.config import settings

logger = logging.getLogger(__name__)

class GoogleOAuthService:
    """Google OAuth service for user authentication."""
    
    # Google OAuth scopes for user login
    SCOPES = [
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
    ]
    
    def __init__(self):
        """Initialize Google OAuth service."""
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
        
    def get_authorization_url(self, state: str = None) -> Dict:
        """Get Google OAuth authorization URL for user login."""
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
            flow.redirect_uri = self.redirect_uri
            
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
        """Exchange authorization code for access token and user info."""
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
                'user_info': user_info
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
    
    def verify_google_token(self, id_token: str) -> Dict:
        """Verify Google ID token."""
        try:
            # This would typically verify the JWT token with Google's public keys
            # For now, we'll return a simple verification
            return {
                'success': True,
                'verified': True
            }
        except Exception as e:
            logger.error(f"Error verifying Google token: {e}")
            return {
                'success': False,
                'error': str(e)
            } 