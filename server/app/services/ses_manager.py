try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
import logging
from typing import List, Dict, Optional
from datetime import datetime
from botocore.exceptions import ClientError, BotoCoreError
from ..core.config import settings

logger = logging.getLogger(__name__)

class SESManager:
    """Dynamic AWS SES Manager for the Email Bot application."""
    
    def __init__(self):
        """Initialize the SES manager."""
        try:
            self.ses_client = boto3.client(
                'ses',
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            logger.info("SES Manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SES Manager: {e}")
            raise

    async def send_email(self, to_email: str, subject: str, body: str, 
                        sender_email: str, html_body: Optional[str] = None, 
                        user_id: str = None) -> Dict:
        """Send a single email using dynamic sender with improved headers."""
        try:
            # Prepare email content with better headers
            email_content = {
                'Source': sender_email,
                'Destination': {
                    'ToAddresses': [to_email]
                },
                'Message': {
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': body,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            }

            # Add HTML body if provided
            if html_body:
                email_content['Message']['Body']['Html'] = {
                    'Data': html_body,
                    'Charset': 'UTF-8'
                }

            # Send email
            response = self.ses_client.send_email(**email_content)
            
            logger.info(f"Email sent successfully to {to_email} from {sender_email}. Message ID: {response['MessageId']}")
            
            return {
                'success': True,
                'message_id': response['MessageId'],
                'to_email': to_email,
                'sender_email': sender_email,
                'user_id': user_id,
                'timestamp': datetime.utcnow()
            }

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"SES ClientError for {to_email} from {sender_email}: {error_code} - {error_message}")
            
            return {
                'success': False,
                'error_code': error_code,
                'error_message': error_message,
                'to_email': to_email,
                'sender_email': sender_email,
                'user_id': user_id,
                'timestamp': datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Unexpected error sending email to {to_email} from {sender_email}: {e}")
            return {
                'success': False,
                'error_code': 'UNKNOWN_ERROR',
                'error_message': str(e),
                'to_email': to_email,
                'sender_email': sender_email,
                'user_id': user_id,
                'timestamp': datetime.utcnow()
            }

    async def send_bulk_emails(self, emails: List[Dict], sender_email: str, user_id: str = None) -> Dict:
        """Send bulk emails with rate limiting and user tracking."""
        results = {
            'total': len(emails),
            'successful': 0,
            'failed': 0,
            'errors': [],
            'sender_email': sender_email,
            'user_id': user_id,
            'start_time': datetime.utcnow(),
            'end_time': None
        }

        logger.info(f"Starting bulk email campaign for user {user_id} from {sender_email}: {len(emails)} recipients")

        # Process emails with rate limiting
        import asyncio
        semaphore = asyncio.Semaphore(10)  # Limit concurrent requests
        
        async def send_with_rate_limit(email_data):
            async with semaphore:
                result = await self.send_email(
                    to_email=email_data['email'],
                    subject=email_data['subject'],
                    body=email_data['body'],
                    sender_email=sender_email,
                    html_body=email_data.get('html_body'),
                    user_id=user_id
                )
                
                if result['success']:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(result)
                
                # Rate limiting: wait 0.1 seconds between emails
                await asyncio.sleep(0.1)
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

    async def get_sending_statistics(self, user_id: str = None) -> Dict:
        """Get SES sending statistics."""
        try:
            response = self.ses_client.get_send_statistics()
            return {
                'success': True,
                'statistics': response['SendDataPoints'],
                'user_id': user_id
            }
        except Exception as e:
            logger.error(f"Failed to get sending statistics: {e}")
            return {
                'success': False,
                'error': str(e),
                'user_id': user_id
            }

    async def get_send_quota(self) -> Dict:
        """Get SES sending quota information."""
        try:
            response = self.ses_client.get_send_quota()
            return {
                'success': True,
                'quota': {
                    'max_24_hour_send': response['Max24HourSend'],
                    'sent_last_24_hours': response['SentLast24Hours'],
                    'max_send_rate': response['MaxSendRate']
                }
            }
        except Exception as e:
            logger.error(f"Failed to get send quota: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def verify_email_identity(self, email: str) -> Dict:
        """Verify an email address with SES."""
        try:
            response = self.ses_client.verify_email_identity(EmailAddress=email)
            logger.info(f"Verification email sent to {email}")
            return {
                'success': True,
                'message': f"Verification email sent to {email}"
            }
        except Exception as e:
            logger.error(f"Failed to verify email {email}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def create_html_email(self, template_content: str, variables: Dict) -> str:
        """Create HTML email from template with variable substitution."""
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Email Campaign</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 20px;
                    border-radius: 0 0 8px 8px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Email Campaign</h1>
            </div>
            <div class="content">
                {template_content}
            </div>
            <div class="footer">
                <p>This email was sent via Email Bot</p>
                <p>Sent on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
            </div>
        </body>
        </html>
        """
        
        # Replace variables in template
        for key, value in variables.items():
            html_template = html_template.replace(f'{{{key}}}', str(value))
        
        return html_template

    async def check_health(self) -> Dict:
        """Check SES service health."""
        try:
            # Test connection by getting quota
            quota = await self.get_send_quota()
            if quota['success']:
                return {
                    'status': 'healthy',
                    'service': 'AWS SES',
                    'sender_email': 'N/A (Dynamic)', # Indicate dynamic sender
                    'quota': quota['quota']
                }
            else:
                return {
                    'status': 'unhealthy',
                    'service': 'AWS SES',
                    'error': quota['error']
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'service': 'AWS SES',
                'error': str(e)
            } 