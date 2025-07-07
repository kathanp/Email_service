from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from ..deps import get_current_user
from ...models.user import UserResponse
from ...models.campaign import CampaignCreate, CampaignResponse
from ...services.ses_manager import SESManager
from ...services.template_service import TemplateService
from ...services.sender_service import SenderService
from ...services.subscription_service import SubscriptionService
from ...db.mongodb import MongoDB
import pandas as pd
import io
import logging
from bson import ObjectId

logger = logging.getLogger(__name__)
router = APIRouter()
ses_manager = SESManager()

class CampaignRequest(BaseModel):
    template_id: str
    subject_override: Optional[str] = None
    custom_message: Optional[str] = None

# CampaignResponse is imported from app.models.campaign

class TemplateValidationRequest(BaseModel):
    template_id: str
    file_id: str

class TemplateValidationResponse(BaseModel):
    is_valid: bool
    template_variables: List[str]
    available_columns: List[str]
    missing_variables: List[str]
    available_variables: List[str]
    missing_count: int
    available_count: int
    validation_message: str

@router.post("/validate-template", response_model=TemplateValidationResponse)
async def validate_template_variables(
    validation_request: TemplateValidationRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Validate template variables against contact file columns."""
    try:
        # Initialize services
        template_service = TemplateService()
        db = MongoDB.get_database()
        
        # Get template
        template = await template_service.get_template_by_id(
            validation_request.template_id, 
            current_user.id
        )
        
        # Get file
        file_collection = MongoDB.get_collection("files")
        file_doc = await file_collection.find_one({
            "_id": ObjectId(validation_request.file_id),
            "user_id": current_user.id
        })
        
        if not file_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact file not found"
            )
        
        # Read file data from database
        file_data = file_doc.get('file_data')
        if not file_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File data not found"
            )
        
        try:
            if file_doc['file_type'] == 'excel':
                df = pd.read_excel(io.BytesIO(file_data))
            else:
                df = pd.read_csv(io.BytesIO(file_data))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error reading file: {str(e)}"
            )
        
        # Get available columns
        available_columns = [col.strip() for col in df.columns.tolist()]
        
        # Validate template variables
        validation_result = template_service.validate_template_variables(
            template.body, 
            available_columns
        )
        
        # Create validation message
        if validation_result["is_valid"]:
            validation_message = f"✅ Template validation successful! All {validation_result['available_count']} template variables are available in your contact file."
        else:
            missing_vars = ", ".join(validation_result["missing_variables"])
            validation_message = f"❌ Template validation failed! Missing variables: {missing_vars}. Please upload a contact file with these columns or update your template."
        
        return TemplateValidationResponse(
            is_valid=validation_result["is_valid"],
            template_variables=validation_result["template_variables"],
            available_columns=validation_result["available_columns"],
            missing_variables=validation_result["missing_variables"],
            available_variables=validation_result["available_variables"],
            missing_count=validation_result["missing_count"],
            available_count=validation_result["available_count"],
            validation_message=validation_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )

@router.post("/", response_model=CampaignResponse)
async def create_and_send_campaign(
    campaign_data: CampaignCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create and send a campaign using existing processed file and template."""
    try:
        # Initialize services
        subscription_service = SubscriptionService()
        sender_service = SenderService()
        template_service = TemplateService()
        
        # Get user's default sender email
        default_sender = await sender_service.get_default_sender(str(current_user.id))
        
        if not default_sender:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No verified sender email found. Please add and verify a sender email first."
            )
        
        sender_email = default_sender['email']
        
        # Get template
        template = await template_service.get_template_by_id(
            campaign_data.template_id, 
            current_user.id
        )
        
        # Get file
        file_collection = MongoDB.get_collection("files")
        file_doc = await file_collection.find_one({
            "_id": ObjectId(campaign_data.file_id),
            "user_id": current_user.id
        })
        
        if not file_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact file not found"
            )
        
        if not file_doc.get('processed'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be processed before sending campaigns"
            )
        
        # Read file data from database
        file_data = file_doc.get('file_data')
        if not file_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File data not found"
            )
        
        # Convert file data to DataFrame - fix the DataFrame constructor issue
        if file_doc.get('file_type') == 'excel':
            df = pd.read_excel(io.BytesIO(file_data))
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only Excel files are supported for campaigns"
            )
        
        # Get available columns
        available_columns = [col.strip() for col in df.columns.tolist()]
        
        # Validate template variables against contact file columns
        validation_result = template_service.validate_template_variables(
            template.body, 
            available_columns
        )
        
        if not validation_result["is_valid"]:
            missing_vars = ", ".join(validation_result["missing_variables"])
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Template validation failed! Missing variables in contact file: {missing_vars}. Please upload a contact file with these columns or update your template."
            )
        
        # Validate required columns
        required_columns = ['email']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {missing_columns}"
            )
        
        # Prepare emails
        emails = []
        for _, row in df.iterrows():
            email = row['email'].strip()
            
            if not email or '@' not in email:
                continue
            
            # Create email content with variable substitution
            subject = campaign_data.subject_override or template.subject
            body = template.body
            
            # Replace all template variables with values from the row
            for column in available_columns:
                column_upper = column.upper()
                if f'{{{column_upper}}}' in body:
                    value = str(row.get(column, '')).strip()
                    body = body.replace(f'{{{column_upper}}}', value)
            
            # Add custom message if provided
            if campaign_data.custom_message:
                body += f"\n\n{campaign_data.custom_message}"
            
            emails.append({
                'email': email,
                'subject': subject,
                'body': body
            })
        
        if not emails:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid email addresses found in file"
            )
        
        # Check subscription limits before sending
        limit_check = await subscription_service.check_email_limit(str(current_user.id), len(emails))
        if not limit_check["allowed"]:
            upgrade_message = await subscription_service.get_upgrade_message(str(current_user.id), "emails")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{limit_check['reason']}. {upgrade_message}"
            )
        
        # Create campaign record
        campaign_collection = MongoDB.get_collection("campaigns")
        campaign_dict = {
            "name": campaign_data.name,
            "user_id": current_user.id,
            "template_id": campaign_data.template_id,
            "file_id": campaign_data.file_id,
            "subject_override": campaign_data.subject_override,
            "custom_message": campaign_data.custom_message,
            "sender_email": sender_email,
            "status": "sending",
            "total_emails": 0,
            "successful": 0,
            "failed": 0,
            "start_time": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        campaign_result = await campaign_collection.insert_one(campaign_dict)
        campaign_id = str(campaign_result.inserted_id)
        
        # Update campaign with total emails count
        await campaign_collection.update_one(
            {"_id": campaign_result.inserted_id},
            {"$set": {"total_emails": len(emails)}}
        )
        
        # Send bulk emails using AWS SES with user's verified sender email
        logger.info(f"Starting mass email campaign for {len(emails)} recipients from {sender_email}")
        
        results = await ses_manager.send_bulk_emails(emails, sender_email, user_id=current_user.id)
        
        # Calculate duration
        end_time = datetime.utcnow()
        duration = (end_time - campaign_dict["start_time"]).total_seconds()
        
        # Update campaign with results
        await campaign_collection.update_one(
            {"_id": campaign_result.inserted_id},
            {
                "$set": {
                    "status": "completed",
                    "successful": results['successful'],
                    "failed": results['failed'],
                    "end_time": end_time,
                    "duration": duration,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Get updated campaign
        updated_campaign = await campaign_collection.find_one({"_id": campaign_result.inserted_id})
        
        return CampaignResponse(
            campaign_id=campaign_id,
            total_emails=updated_campaign["total_emails"],
            successful=updated_campaign["successful"],
            failed=updated_campaign["failed"],
            duration=updated_campaign["duration"],
            status=updated_campaign["status"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Campaign failed: {str(e)}"
        )

@router.post("/send-mass-email", response_model=CampaignResponse)
async def send_mass_email(
    campaign_request: CampaignRequest,
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """Send mass emails using uploaded contact file and selected template."""
    
    try:
        # Check if user has a sender email configured
        db = MongoDB.get_database()
        user = db.users.find_one({"_id": current_user.id})
        
        if not user or not user.get('sender_email'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No sender email configured. Please connect your Google account or set a sender email."
            )
        
        # Initialize template service
        template_service = TemplateService()
        
        # Get template
        template = await template_service.get_template_by_id(
            campaign_request.template_id, 
            current_user.id
        )
        
        # Read and validate file
        if not file.filename.endswith(('.xlsx', '.csv')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be Excel (.xlsx) or CSV (.csv) format"
            )
        
        # Read file content
        content = await file.read()
        
        if file.filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(content))
        else:
            df = pd.read_csv(io.BytesIO(content))
        
        # Get available columns
        available_columns = [col.strip() for col in df.columns.tolist()]
        
        # Validate template variables against contact file columns
        validation_result = template_service.validate_template_variables(
            template.body, 
            available_columns
        )
        
        if not validation_result["is_valid"]:
            missing_vars = ", ".join(validation_result["missing_variables"])
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Template validation failed! Missing variables in contact file: {missing_vars}. Please upload a contact file with these columns or update your template."
            )
        
        # Validate required columns
        required_columns = ['email']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {missing_columns}"
            )
        
        # Prepare emails
        emails = []
        for _, row in df.iterrows():
            email = row['email'].strip()
            
            if not email or '@' not in email:
                continue
            
            # Create email content with variable substitution
            subject = campaign_request.subject_override or template.subject
            body = template.body
            
            # Replace all template variables with values from the row
            for column in available_columns:
                column_upper = column.upper()
                if f'{{{column_upper}}}' in body:
                    value = str(row.get(column, '')).strip()
                    body = body.replace(f'{{{column_upper}}}', value)
            
            # Add custom message if provided
            if campaign_request.custom_message:
                body += f"\n\n{campaign_request.custom_message}"
            
            emails.append({
                'email': email,
                'subject': subject,
                'body': body
            })
        
        if not emails:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid email addresses found in file"
            )
        
        # Send bulk emails using AWS SES with user's email as sender
        logger.info(f"Starting mass email campaign for {len(emails)} recipients")
        
        # Override the sender email for this campaign
        ses_manager.sender_email = user['sender_email']
        
        results = await ses_manager.send_bulk_emails(emails, user_id=current_user.id)
        
        # Calculate duration
        duration = (results['end_time'] - results['start_time']).total_seconds()
        
        return CampaignResponse(
            campaign_id=f"campaign_{current_user.id}_{results['start_time'].timestamp()}",
            total_emails=results['total'],
            successful=results['successful'],
            failed=results['failed'],
            duration=duration,
            status="completed"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in mass email campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Campaign failed: {str(e)}"
        )

@router.get("/sender-status")
async def get_sender_status(current_user: UserResponse = Depends(get_current_user)):
    """Get sender email status for current user."""
    try:
        db = MongoDB.get_database()
        user = db.users.find_one({"_id": current_user.id})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        has_sender_email = bool(user.get('sender_email'))
        
        return {
            "has_sender_email": has_sender_email,
            "sender_email": user.get('sender_email'),
            "is_google_user": bool(user.get('google_id')),
            "google_email": user.get('google_email')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sender status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sender status: {str(e)}"
        )

@router.post("/send-test-email")
async def send_test_email(
    to_email: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Send a test email using AWS SES."""
    try:
        db = MongoDB.get_database()
        user = db.users.find_one({"_id": current_user.id})
        
        if not user or not user.get('sender_email'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No sender email configured. Please connect your Google account or set a sender email."
            )
        
        # Get user's sender email if available, otherwise use AWS SES default
        if user and user.get('sender_email'):
            ses_manager.sender_email = user['sender_email']
        else:
            # Use AWS SES default sender email
            from ...core.config import settings
            ses_manager.sender_email = settings.AWS_SES_SENDER_EMAIL
        
        # Send test email
        result = await ses_manager.send_email(
            to_email=to_email,
            subject="Test Email from Email Bot",
            body="This is a test email sent from your Email Bot application using AWS SES.",
            user_id=current_user.id
        )
        
        if result['success']:
            return {
                "success": True,
                "message": "Test email sent successfully",
                "message_id": result['message_id'],
                "sender_email": ses_manager.sender_email
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to send email: {result['error_message']}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test email: {str(e)}"
        )

@router.get("/quota")
async def get_send_quota(current_user: UserResponse = Depends(get_current_user)):
    """Get SES sending quota information."""
    try:
        quota_info = await ses_manager.get_send_quota()
        
        if not quota_info['success']:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=quota_info['error']
            )
        
        return quota_info['quota']
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting send quota: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get quota: {str(e)}"
        )

@router.get("/statistics")
async def get_sending_statistics(current_user: UserResponse = Depends(get_current_user)):
    """Get SES sending statistics."""
    try:
        stats = await ses_manager.get_sending_statistics(user_id=current_user.id)
        
        if not stats['success']:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=stats['error']
            )
        
        return {"statistics": stats['statistics']}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sending statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        ) 
@router.get("/{campaign_id}/status")
async def get_campaign_status(
    campaign_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get live status of a campaign."""
    try:
        campaign_collection = MongoDB.get_collection("campaigns")
        campaign = await campaign_collection.find_one({
            "_id": ObjectId(campaign_id),
            "user_id": current_user.id
        })
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        return {
            "id": str(campaign["_id"]),
            "name": campaign["name"],
            "status": campaign["status"],
            "total_emails": campaign["total_emails"],
            "successful": campaign["successful"],
            "failed": campaign["failed"],
            "start_time": campaign["start_time"],
            "end_time": campaign.get("end_time"),
            "duration": campaign.get("duration"),
            "progress_percentage": (
                ((campaign["successful"] + campaign["failed"]) / campaign["total_emails"] * 100)
                if campaign["total_emails"] > 0 else 0
            )
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campaign status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign status: {str(e)}"
        )
