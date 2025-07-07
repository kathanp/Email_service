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
        """Get templates collection."""
        try:
            return MongoDB.get_collection("templates")
        except Exception as e:
            logger.warning(f"Database not available: {e}")
            return None

    def _is_development_mode(self):
        """Check if we're in development mode without database."""
        try:
            collection = self._get_templates_collection()
            return collection is None
        except:
            return True

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
            if self._is_development_mode():
                # Development mode - return mock template
                logger.info("Development mode: Mock template creation")
                now = datetime.utcnow()
                return TemplateResponse(
                    id="dev_template_123",
                    name=template_data.name,
                    subject=template_data.subject,
                    body=template_data.body,
                    user_id=template_data.user_id,
                    created_at=now,
                    updated_at=now,
                    is_active=True,
                    is_default=template_data.is_default
                )

            # Check subscription limits first
            limit_check = await self.subscription_service.check_template_limit(template_data.user_id)
            if not limit_check["allowed"]:
                upgrade_message = await self.subscription_service.get_upgrade_message(template_data.user_id, "templates")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"{limit_check['reason']}. {upgrade_message}"
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

            # If this template is being set as default, unset other defaults for this user
            if template_dict["is_default"]:
                await templates_collection.update_many(
                    {"user_id": template_data.user_id, "is_active": True},
                    {"$set": {"is_default": False, "updated_at": datetime.utcnow()}}
                )

            # Insert template into database
            result = await templates_collection.insert_one(template_dict)
            
            # Get the created template
            created_template = await templates_collection.find_one({"_id": result.inserted_id})
            
            return TemplateResponse(
                id=str(created_template["_id"]),
                name=created_template["name"],
                subject=created_template["subject"],
                body=created_template["body"],
                user_id=created_template["user_id"],
                created_at=created_template["created_at"],
                updated_at=created_template["updated_at"],
                is_active=created_template["is_active"],
                is_default=created_template["is_default"]
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating template: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Template creation failed: {str(e)}"
            )

    async def get_user_templates(self, user_id: str) -> List[TemplateResponse]:
        """Get all templates created by a user."""
        try:
            if self._is_development_mode():
                # Development mode - return mock templates
                logger.info("Development mode: Mock user templates")
                now = datetime.utcnow()
                return [
                    TemplateResponse(
                        id="template_1",
                        name="Welcome Email Template",
                        subject="Welcome to our service, {FIRST_NAME}!",
                        body="Dear {FIRST_NAME},\n\nWelcome to our service! We're excited to have you on board.\n\nBest regards,\nThe Team",
                        user_id=user_id,
                        created_at=now,
                        updated_at=now,
                        is_active=True,
                        is_default=True
                    ),
                    TemplateResponse(
                        id="template_2",
                        name="Newsletter Template",
                        subject="Monthly Newsletter - {MONTH}",
                        body="Hello {FIRST_NAME},\n\nHere's your monthly newsletter with the latest updates.\n\nBest regards,\nThe Newsletter Team",
                        user_id=user_id,
                        created_at=now,
                        updated_at=now,
                        is_active=True,
                        is_default=False
                    )
                ]

            templates_collection = self._get_templates_collection()
            cursor = templates_collection.find({
                "user_id": user_id,
                "is_active": True
            }).sort("created_at", -1)  # Sort by newest first
            
            templates = await cursor.to_list(length=None)
            
            return [
                TemplateResponse(
                    id=str(template["_id"]),
                    name=template["name"],
                    subject=template["subject"],
                    body=template["body"],
                    user_id=template["user_id"],
                    created_at=template["created_at"],
                    updated_at=template["updated_at"],
                    is_active=template["is_active"],
                    is_default=template.get("is_default", False)
                )
                for template in templates
            ]
        except Exception as e:
            logger.error(f"Error getting user templates: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving templates: {str(e)}"
            )

    async def get_template_by_id(self, template_id: str, user_id: str) -> TemplateResponse:
        """Get a specific template by ID (user can only access their own templates)."""
        try:
            if self._is_development_mode():
                # Development mode - return mock template
                logger.info("Development mode: Mock template by ID")
                now = datetime.utcnow()
                return TemplateResponse(
                    id=template_id,
                    name="Welcome Email Template",
                    subject="Welcome to our service, {FIRST_NAME}!",
                    body="Dear {FIRST_NAME},\n\nWelcome to our service! We're excited to have you on board.\n\nBest regards,\nThe Team",
                    user_id=user_id,
                    created_at=now,
                    updated_at=now,
                    is_active=True,
                    is_default=True
                )

            templates_collection = self._get_templates_collection()
            
            if not ObjectId.is_valid(template_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid template ID"
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
                body=template["body"],
                user_id=template["user_id"],
                created_at=template["created_at"],
                updated_at=template["updated_at"],
                is_active=template["is_active"],
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
            if self._is_development_mode():
                # Development mode - return mock updated template
                logger.info("Development mode: Mock template update")
                now = datetime.utcnow()
                return TemplateResponse(
                    id=template_id,
                    name=template_data.name or "Updated Template",
                    subject=template_data.subject or "Updated Subject",
                    body=template_data.body or "Updated body content",
                    user_id=user_id,
                    created_at=now,
                    updated_at=now,
                    is_active=True,
                    is_default=template_data.is_default or False
                )

            templates_collection = self._get_templates_collection()
            
            if not ObjectId.is_valid(template_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid template ID"
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

            # Prepare update data
            update_data = template_data.dict(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow()

            # If this template is being set as default, unset other defaults for this user
            if update_data.get("is_default", False):
                await templates_collection.update_many(
                    {"user_id": user_id, "is_active": True, "_id": {"$ne": ObjectId(template_id)}},
                    {"$set": {"is_default": False, "updated_at": datetime.utcnow()}}
                )

            # Update template
            await templates_collection.update_one(
                {"_id": ObjectId(template_id)},
                {"$set": update_data}
            )

            # Get updated template
            updated_template = await templates_collection.find_one({"_id": ObjectId(template_id)})

            return TemplateResponse(
                id=str(updated_template["_id"]),
                name=updated_template["name"],
                subject=updated_template["subject"],
                body=updated_template["body"],
                user_id=updated_template["user_id"],
                created_at=updated_template["created_at"],
                updated_at=updated_template["updated_at"],
                is_active=updated_template["is_active"],
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
            if self._is_development_mode():
                # Development mode - return mock success
                logger.info("Development mode: Mock template deletion")
                return {"message": "Template deleted successfully"}

            templates_collection = self._get_templates_collection()
            
            if not ObjectId.is_valid(template_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid template ID"
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
            await templates_collection.update_one(
                {"_id": ObjectId(template_id)},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
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
        """Set a template as the default template for the current user."""
        try:
            if self._is_development_mode():
                # Development mode - return mock success
                logger.info("Development mode: Mock set template as default")
                now = datetime.utcnow()
                return TemplateResponse(
                    id=template_id,
                    name="Default Template",
                    subject="Default Subject",
                    body="Default body content",
                    user_id=user_id,
                    created_at=now,
                    updated_at=now,
                    is_active=True,
                    is_default=True
                )

            templates_collection = self._get_templates_collection()
            
            if not ObjectId.is_valid(template_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid template ID"
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
            await templates_collection.update_one(
                {"_id": ObjectId(template_id)},
                {"$set": {"is_default": True, "updated_at": datetime.utcnow()}}
            )

            # Get updated template
            updated_template = await templates_collection.find_one({"_id": ObjectId(template_id)})

            return TemplateResponse(
                id=str(updated_template["_id"]),
                name=updated_template["name"],
                subject=updated_template["subject"],
                body=updated_template["body"],
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