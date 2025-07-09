import boto3
import logging
from typing import List, Dict, Optional
from datetime import datetime
from botocore.exceptions import ClientError
from bson import ObjectId
from ..core.config import settings
from ..db.mongodb import MongoDB
from ..models.sender import SenderCreate, SenderInDB, Sender
from ..services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)

class SenderService:
    def __init__(self):
        """Initialize the sender service with AWS SES client."""
        try:
            self.collection = MongoDB.get_collection("senders")
            self.subscription_service = SubscriptionService()
            
            # Initialize AWS SES client
            self.ses_client = boto3.client(
                'ses',
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            logger.info("Sender Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Sender Service: {e}")
            raise

    async def add_sender(self, user_id: str, sender_data: SenderCreate) -> Dict:
        """Add a new sender email for a user and initiate verification."""
        try:
            # Get user info for subscription check
            users_collection = MongoDB.get_collection("users")
            user_doc = await users_collection.find_one({"_id": ObjectId(user_id)})
            if not user_doc:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            # Create UserResponse object for subscription service
            from ..models.user import UserResponse
            user = UserResponse(
                id=str(user_doc["_id"]),
                email=user_doc["email"],
                username=user_doc.get("username"),
                full_name=user_doc.get("full_name"),
                role=user_doc["role"],
                created_at=user_doc["created_at"],
                last_login=user_doc.get("last_login"),
                is_active=user_doc["is_active"],
                usersubscription=user_doc.get("usersubscription", "free"),
                google_id=user_doc.get("google_id"),
                google_name=user_doc.get("google_name"),
                sender_email=user_doc.get("sender_email")
            )
            
            # Check subscription limits
            limit_check = await self.subscription_service.check_sender_email_limit(user)
            if not limit_check["can_add"]:
                plan_limits = self.subscription_service.get_user_plan_limits(user)
                return {
                    "success": False,
                    "error": f"You have reached the maximum number of sender emails ({plan_limits['sender_emails']}) for your {user.usersubscription} plan. Please upgrade to add more sender emails."
                }
            
            # Check if sender already exists for this user
            existing_sender = await self.collection.find_one({
                "user_id": user_id,
                "email": sender_data.email
            })
            
            if existing_sender:
                return {
                    "success": False,
                    "error": "Sender email already exists for this user"
                }

            # Create sender document
            sender_doc = {
                "user_id": user_id,
                "email": sender_data.email,
                "display_name": sender_data.display_name or sender_data.email,
                "is_default": sender_data.is_default,
                "verification_status": "pending",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            # If this is the first sender or marked as default, set as default
            if sender_data.is_default:
                await self.collection.update_many(
                    {"user_id": user_id},
                    {"$set": {"is_default": False}}
                )

            # Insert sender document
            result = await self.collection.insert_one(sender_doc)
            sender_doc["_id"] = result.inserted_id

            # Initiate AWS SES verification
            verification_result = await self._verify_sender_email(sender_data.email)
            
            if verification_result["success"]:
                # Update verification status
                await self.collection.update_one(
                    {"_id": result.inserted_id},
                    {"$set": {"verification_status": "pending"}}
                )
                
                return {
                    "success": True,
                    "message": f"Verification email sent to {sender_data.email}",
                    "sender_id": str(result.inserted_id),
                    "verification_status": "pending"
                }
            else:
                # Delete the sender if verification failed
                await self.collection.delete_one({"_id": result.inserted_id})
                return verification_result

        except Exception as e:
            logger.error(f"Error adding sender: {e}")
            return {
                "success": False,
                "error": f"Failed to add sender: {str(e)}"
            }

    async def get_user_senders(self, user_id: str) -> List[Dict]:
        """Get all sender emails for a user."""
        try:
            senders = []
            cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1)
            
            async for sender in cursor:
                # Check current verification status with AWS SES
                verification_status = await self._check_verification_status(sender["email"])
                
                # Update status if changed
                if verification_status != sender["verification_status"]:
                    await self.collection.update_one(
                        {"_id": sender["_id"]},
                        {"$set": {"verification_status": verification_status}}
                    )
                    sender["verification_status"] = verification_status
                
                senders.append({
                    "id": str(sender["_id"]),
                    "email": sender["email"],
                    "display_name": sender["display_name"],
                    "is_default": sender["is_default"],
                    "verification_status": sender["verification_status"],
                    "created_at": sender["created_at"],
                    "updated_at": sender["updated_at"]
                })
            
            return senders

        except Exception as e:
            logger.error(f"Error getting user senders: {e}")
            return []

    async def delete_sender(self, user_id: str, sender_id: str) -> Dict:
        """Delete a sender email for a user."""
        try:
            # Check if sender belongs to user
            sender = await self.collection.find_one({
                "_id": ObjectId(sender_id),
                "user_id": user_id
            })
            
            if not sender:
                return {
                    "success": False,
                    "error": "Sender not found or access denied"
                }

            # Delete from database
            result = await self.collection.delete_one({"_id": ObjectId(sender_id)})
            
            if result.deleted_count > 0:
                return {
                    "success": True,
                    "message": "Sender deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to delete sender"
                }

        except Exception as e:
            logger.error(f"Error deleting sender: {e}")
            return {
                "success": False,
                "error": f"Failed to delete sender: {str(e)}"
            }

    async def set_default_sender(self, user_id: str, sender_id: str) -> Dict:
        """Set a sender as default for a user."""
        try:
            # Check if sender belongs to user
            sender = await self.collection.find_one({
                "_id": ObjectId(sender_id),
                "user_id": user_id
            })
            
            if not sender:
                return {
                    "success": False,
                    "error": "Sender not found or access denied"
                }

            # Check if sender is verified
            if sender["verification_status"] != "verified":
                return {
                    "success": False,
                    "error": "Only verified senders can be set as default"
                }

            # Update all user's senders to not default
            await self.collection.update_many(
                {"user_id": user_id},
                {"$set": {"is_default": False}}
            )

            # Set the selected sender as default
            await self.collection.update_one(
                {"_id": ObjectId(sender_id)},
                {"$set": {"is_default": True}}
            )

            return {
                "success": True,
                "message": f"{sender['email']} set as default sender"
            }

        except Exception as e:
            logger.error(f"Error setting default sender: {e}")
            return {
                "success": False,
                "error": f"Failed to set default sender: {str(e)}"
            }

    async def get_default_sender(self, user_id: str) -> Optional[Dict]:
        """Get the default sender for a user."""
        try:
            sender = await self.collection.find_one({
                "user_id": user_id,
                "is_default": True,
                "verification_status": "verified"
            })
            
            if sender:
                return {
                    "id": str(sender["_id"]),
                    "email": sender["email"],
                    "display_name": sender["display_name"],
                    "is_default": sender["is_default"],
                    "verification_status": sender["verification_status"]
                }
            
            return None

        except Exception as e:
            logger.error(f"Error getting default sender: {e}")
            return None

    async def _verify_sender_email(self, email: str) -> Dict:
        """Initiate AWS SES verification for a sender email."""
        try:
            response = self.ses_client.verify_email_identity(EmailAddress=email)
            logger.info(f"Verification email sent to {email}")
            return {
                "success": True,
                "message": f"Verification email sent to {email}"
            }
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'AlreadyExists':
                return {
                    "success": True,
                    "message": f"Verification already in progress for {email}"
                }
            else:
                logger.error(f"AWS SES error for {email}: {error_code} - {error_message}")
                return {
                    "success": False,
                    "error": f"AWS SES error: {error_message}"
                }
        except Exception as e:
            logger.error(f"Error verifying sender email {email}: {e}")
            return {
                "success": False,
                "error": f"Failed to verify email: {str(e)}"
            }

    async def _check_verification_status(self, email: str) -> str:
        """Check the verification status of a sender email with AWS SES."""
        try:
            response = self.ses_client.get_identity_verification_attributes(
                Identities=[email]
            )
            
            if email in response['VerificationAttributes']:
                status = response['VerificationAttributes'][email]['VerificationStatus']
                if status == 'Success':
                    return 'verified'
                elif status == 'Pending':
                    return 'pending'
                else:
                    return 'failed'
            else:
                return 'not_found'
                
        except Exception as e:
            logger.error(f"Error checking verification status for {email}: {e}")
            return 'unknown'

    async def resend_verification(self, user_id: str, sender_id: str) -> Dict:
        """Resend verification email for a sender."""
        try:
            # Check if sender belongs to user
            sender = await self.collection.find_one({
                "_id": ObjectId(sender_id),
                "user_id": user_id
            })
            
            if not sender:
                return {
                    "success": False,
                    "error": "Sender not found or access denied"
                }

            # Resend verification
            verification_result = await self._verify_sender_email(sender["email"])
            
            if verification_result["success"]:
                # Update verification status
                await self.collection.update_one(
                    {"_id": ObjectId(sender_id)},
                    {"$set": {"verification_status": "pending"}}
                )
                
                return {
                    "success": True,
                    "message": f"Verification email resent to {sender['email']}"
                }
            else:
                return verification_result

        except Exception as e:
            logger.error(f"Error resending verification: {e}")
            return {
                "success": False,
                "error": f"Failed to resend verification: {str(e)}"
            } 