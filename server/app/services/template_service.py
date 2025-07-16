import re
from datetime import datetime
from typing import List, Optional, Set
from bson import ObjectId
import logging
from fastapi import HTTPException, status
from ..db.mongodb import MongoDB
from ..models.template import TemplateCreate, TemplateUpdate, TemplateInDB, TemplateResponse
from ..services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)

class TemplateService:
    def __init__(self):
        self.subscription_service = SubscriptionService()

    def _get_templates_collection(self):
        """Get the templates collection from MongoDB."""
        try:
            return MongoDB.get_collection("templates")
        except Exception as e:
            logger.warning(f"Database not available: {e}")
            return None

    def extract_template_variables(self, template_body: str) -> Set[str]:
        """Extract all template variables from template body using regex."""
        # Pattern to match {VARIABLE_NAME} format
        pattern = r'\{([A-Z_][A-Z0-9_]*)\}'
        variables = re.findall(pattern, template_body)
        return set(variables)

    def validate_template_variables(self, template_body: str, available_columns: List[str]) -> dict:
        """
        Validate template variables against available contact file columns.
        Returns validation result with missing and available variables.
        """
        template_variables = self.extract_template_variables(template_body)
        # Convert available columns to uppercase for comparison
        available_columns_upper = [col.upper() for col in available_columns]
        available_columns_set = set(available_columns_upper)
        
        missing_variables = template_variables - available_columns_set
        available_variables = template_variables & available_columns_set
        
        return {
            "template_variables": list(template_variables),
            "available_columns": available_columns,
            "missing_variables": list(missing_variables),
            "available_variables": list(available_variables),
            "is_valid": len(missing_variables) == 0,
            "missing_count": len(missing_variables),
            "available_count": len(available_variables)
        }

    async def create_template(self, template_data: TemplateCreate) -> TemplateResponse:
        """Create a new email template."""
        try:
            logger.info(f"📝 Creating template for user {template_data.user_id}: {template_data.name}")
            # Get user info for subscription check
            users_collection = MongoDB.get_collection("users")
            user_doc = await users_collection.find_one({"_id": ObjectId(template_data.user_id)})
            if not user_doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
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
            limit_check = await self.subscription_service.check_template_limit(user)
            if not limit_check["can_create"]:
                plan_limits = self.subscription_service.get_user_plan_limits(user)
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"You have reached the maximum number of templates ({plan_limits['templates']}) for your {user.usersubscription} plan. Please upgrade to create more templates."
                )
            
            templates_collection = self._get_templates_collection()
            
            # Check if template with same name already exists for this user
            existing_template = await templates_collection.find_one({
                "name": template_data.name,
                "user_id": template_data.user_id,
                "is_active": True
            })
            
            if existing_template:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A template with this name already exists"
                )

            # Create template document
            template_dict = template_data.dict()
            template_dict["created_at"] = datetime.utcnow()
            template_dict["updated_at"] = datetime.utcnow()
            template_dict["is_active"] = True
            template_dict["is_default"] = template_dict.get("is_default", False)

            logger.info(f"📝 Template data to save: {template_dict}")

            # If this template is being set as default, unset other defaults for this user
            if template_dict["is_default"]:
                await templates_collection.update_many(
                    {"user_id": template_data.user_id, "is_active": True},
                    {"$set": {"is_default": False, "updated_at": datetime.utcnow()}}
                )

            # Insert template into database
            result = await templates_collection.insert_one(template_dict)
            logger.info(f"✅ Template created with ID: {result.inserted_id}")
            
            # Get the created template
            created_template = await templates_collection.find_one({"_id": result.inserted_id})
            logger.info(f"📝 Retrieved created template: {created_template}")
            
            return TemplateResponse(
                id=str(created_template["_id"]),
                name=created_template["name"],
                subject=created_template["subject"],
                content=created_template.get("content", ""),  # Use get to avoid KeyError
                body=created_template.get("content", ""),  # Add body field for frontend compatibility
                user_id=created_template["user_id"],
                created_at=created_template.get("created_at", datetime.utcnow()),
                updated_at=created_template.get("updated_at", datetime.utcnow()),
                is_active=created_template.get("is_active", True),
                is_default=created_template.get("is_default", False)
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error creating template: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Template creation failed: {str(e)}"
            )

    async def get_user_templates(self, user_id: str) -> List[TemplateResponse]:
        """Get all templates created by a user."""
        try:
            logger.info(f"🔍 Fetching templates for user {user_id}")
            templates_collection = self._get_templates_collection()
            cursor = templates_collection.find({
                "user_id": user_id,
                "is_active": True
            }).sort("created_at", -1)  # Sort by newest first
            
            templates = await cursor.to_list(length=None)
            logger.info(f"📝 Found {len(templates)} templates for user {user_id}")
            
            for template in templates:
                logger.info(f"  - {template.get('name', 'Unknown')} (ID: {template['_id']})")
            
            return [
                TemplateResponse(
                    id=str(template["_id"]),
                    name=template["name"],
                    subject=template["subject"],
                    content=template.get("content", ""),  # Use get to avoid KeyError
                    body=template.get("content", ""),  # Add body field for frontend compatibility
                    user_id=template["user_id"],
                    created_at=template.get("created_at", datetime.utcnow()),
                    updated_at=template.get("updated_at", datetime.utcnow()),
                    is_active=template.get("is_active", True),
                    is_default=template.get("is_default", False)
                )
                for template in templates
            ]
        except Exception as e:
            logger.error(f"❌ Error getting user templates: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving templates: {str(e)}"
            )

    async def get_template_by_id(self, template_id: str, user_id: str) -> TemplateResponse:
        """Get a specific template by ID (user can only access their own templates)."""
        try:
            templates_collection = self._get_templates_collection()
            
            # Validate ObjectId format
            if not ObjectId.is_valid(template_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid template ID format"
                )
            
            template = await templates_collection.find_one({
                "_id": ObjectId(template_id),
                "user_id": user_id,
                "is_active": True
            })
            
            if not template:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Template not found"
                )
            
            return TemplateResponse(
                id=str(template["_id"]),
                name=template["name"],
                subject=template["subject"],
                content=template.get("content", ""),  # Use get to avoid KeyError
                body=template.get("content", ""),  # Add body field for frontend compatibility
                user_id=template["user_id"],
                created_at=template.get("created_at", datetime.utcnow()),
                updated_at=template.get("updated_at", datetime.utcnow()),
                is_active=template.get("is_active", True),
                is_default=template.get("is_default", False)
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting template by ID: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving template: {str(e)}"
            )

    async def update_template(self, template_id: str, user_id: str, template_data: TemplateUpdate) -> TemplateResponse:
        """Update a template."""
        try:
            templates_collection = self._get_templates_collection()
            
            # Validate ObjectId format
            if not ObjectId.is_valid(template_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid template ID format"
                )
            
            # Check if template exists and belongs to user
            existing_template = await templates_collection.find_one({
                "_id": ObjectId(template_id),
                "user_id": user_id,
                "is_active": True
            })
            
            if not existing_template:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Template not found"
                )
            
            # Check if name is being changed and if it conflicts with existing template
            if template_data.name and template_data.name != existing_template["name"]:
                name_conflict = await templates_collection.find_one({
                    "name": template_data.name,
                    "user_id": user_id,
                    "is_active": True,
                    "_id": {"$ne": ObjectId(template_id)}
                })
                
                if name_conflict:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="A template with this name already exists"
                    )
            
            # Prepare update data
            update_data = template_data.dict(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow()
            
            # If setting as default, unset other defaults
            if template_data.is_default:
                await templates_collection.update_many(
                    {"user_id": user_id, "is_active": True, "_id": {"$ne": ObjectId(template_id)}},
                    {"$set": {"is_default": False, "updated_at": datetime.utcnow()}}
                )
            
            # Update the template
            result = await templates_collection.update_one(
                {"_id": ObjectId(template_id), "user_id": user_id},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update template"
                )
            
            # Get the updated template
            updated_template = await templates_collection.find_one({"_id": ObjectId(template_id)})
            
            return TemplateResponse(
                id=str(updated_template["_id"]),
                name=updated_template["name"],
                subject=updated_template["subject"],
                content=updated_template.get("content", ""),  # Use get to avoid KeyError
                body=updated_template.get("content", ""),  # Add body field for frontend compatibility
                user_id=updated_template["user_id"],
                created_at=updated_template.get("created_at", datetime.utcnow()),
                updated_at=updated_template.get("updated_at", datetime.utcnow()),
                is_active=updated_template.get("is_active", True),
                is_default=updated_template.get("is_default", False)
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating template: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Template update failed: {str(e)}"
            )

    async def delete_template(self, template_id: str, user_id: str) -> dict:
        """Delete a template (soft delete by setting is_active to False)."""
        try:
            templates_collection = self._get_templates_collection()
            
            # Validate ObjectId format
            if not ObjectId.is_valid(template_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid template ID format"
                )
            
            # Check if template exists and belongs to user
            existing_template = await templates_collection.find_one({
                "_id": ObjectId(template_id),
                "user_id": user_id,
                "is_active": True
            })
            
            if not existing_template:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Template not found"
                )
            
            # Soft delete by setting is_active to False
            result = await templates_collection.update_one(
                {"_id": ObjectId(template_id), "user_id": user_id},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete template"
                )
            
            return {"message": "Template deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting template: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Template deletion failed: {str(e)}"
            )

    async def set_template_as_default(self, template_id: str, user_id: str) -> TemplateResponse:
        """Set a template as the default template for the user."""
        try:
            templates_collection = self._get_templates_collection()
            
            # Validate ObjectId format
            if not ObjectId.is_valid(template_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid template ID format"
                )
            
            # Check if template exists and belongs to user
            existing_template = await templates_collection.find_one({
                "_id": ObjectId(template_id),
                "user_id": user_id,
                "is_active": True
            })
            
            if not existing_template:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Template not found"
                )
            
            # Unset all other defaults for this user
            await templates_collection.update_many(
                {"user_id": user_id, "is_active": True},
                {"$set": {"is_default": False, "updated_at": datetime.utcnow()}}
            )
            
            # Set this template as default
            result = await templates_collection.update_one(
                {"_id": ObjectId(template_id), "user_id": user_id},
                {"$set": {"is_default": True, "updated_at": datetime.utcnow()}}
            )
            
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to set template as default"
                )
            
            # Get the updated template
            updated_template = await templates_collection.find_one({"_id": ObjectId(template_id)})
            
            return TemplateResponse(
                id=str(updated_template["_id"]),
                name=updated_template["name"],
                subject=updated_template["subject"],
                content=updated_template.get("content", ""),  # Use get to avoid KeyError
                user_id=updated_template["user_id"],
                created_at=updated_template["created_at"],
                updated_at=updated_template["updated_at"],
                is_active=updated_template["is_active"],
                is_default=updated_template.get("is_default", False)
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error setting template as default: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to set template as default: {str(e)}"
            )