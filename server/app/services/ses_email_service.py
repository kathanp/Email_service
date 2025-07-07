try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime
from botocore.exceptions import ClientError, BotoCoreError
from ..core.config import settings

logger = logging.getLogger(__name__)

class SESEmailService:
    def __init__(self):
        """Initialize Amazon SES client with centralized credentials."""
        if not BOTO3_AVAILABLE:
            logger.warning("boto3 not available - SES functionality disabled")
            self.ses_client = None
            return
            
        try:
            self.ses_client = boto3.client(
                'ses',
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            self.sender_email = settings.SENDER_EMAIL
            logger.info("SES Email Service initialized with centralized credentials")
        except Exception as e:
            logger.error(f"Failed to initialize SES client: {e}")
            self.ses_client = None

    async def send_single_email(self, to_email: str, subject: str, body: str, 
                               html_body: Optional[str] = None) -> Dict:
        """Send a single email using Amazon SES."""
        if not self.ses_client:
            return {
                'success': False,
                'error_code': 'SERVICE_UNAVAILABLE',
                'error_message': 'SES service not available',
                'to_email': to_email,
                'timestamp': datetime.utcnow()
            }
            
        try:
            # Prepare email content
            email_content = {
                'Source': self.sender_email,
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
            
            logger.info(f"Email sent successfully to {to_email}. Message ID: {response['MessageId']}")
            
            return {
                'success': True,
                'message_id': response['MessageId'],
                'to_email': to_email,
                'timestamp': datetime.utcnow()
            }

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"SES ClientError for {to_email}: {error_code} - {error_message}")
            
            return {
                'success': False,
                'error_code': error_code,
                'error_message': error_message,
                'to_email': to_email,
                'timestamp': datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Unexpected error sending email to {to_email}: {e}")
            return {
                'success': False,
                'error_code': 'UNKNOWN_ERROR',
                'error_message': str(e),
                'to_email': to_email,
                'timestamp': datetime.utcnow()
            }

    async def send_bulk_emails(self, emails: List[Dict], template_id: Optional[str] = None) -> Dict:
        """Send bulk emails with rate limiting and error handling."""
        results = {
            'total': len(emails),
            'successful': 0,
            'failed': 0,
            'errors': [],
            'start_time': datetime.utcnow(),
            'end_time': None
        }

        logger.info(f"Starting bulk email campaign for {len(emails)} recipients")

        # Process emails with rate limiting (SES allows 14 emails per second)
        semaphore = asyncio.Semaphore(10)  # Limit concurrent requests
        
        async def send_with_rate_limit(email_data):
            async with semaphore:
                result = await self.send_single_email(
                    to_email=email_data['email'],
                    subject=email_data['subject'],
                    body=email_data['body'],
                    html_body=email_data.get('html_body')
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
        
        logger.info(f"Bulk email campaign completed in {duration:.2f} seconds")
        logger.info(f"Results: {results['successful']} successful, {results['failed']} failed")
        
        return results

    async def get_sending_statistics(self) -> Dict:
        """Get SES sending statistics."""
        if not self.ses_client:
            return {
                'success': False,
                'error': 'SES service not available'
            }
        try:
            response = self.ses_client.get_send_statistics()
            return {
                'success': True,
                'statistics': response['SendDataPoints']
            }
        except Exception as e:
            logger.error(f"Failed to get sending statistics: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def verify_email_identity(self, email: str) -> Dict:
        """Verify an email address with SES."""
        if not self.ses_client:
            return {
                'success': False,
                'error': 'SES service not available'
            }
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

    async def get_send_quota(self) -> Dict:
        """Get SES sending quota information."""
        if not self.ses_client:
            return {
                'success': False,
                'error': 'SES service not available'
            }
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

    def create_html_email(self, template_content: str, variables: Dict) -> str:
        """Create HTML email from template with variable substitution."""
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Email Template</title>
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
                <p>This email was sent via Amazon SES</p>
                <p>Sent on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
            </div>
        </body>
        </html>
        """
        
        # Replace variables in template
        for key, value in variables.items():
            html_template = html_template.replace(f'{{{key}}}', str(value))
        
        return html_template 