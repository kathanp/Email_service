import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId
from fastapi import HTTPException, status
from ..db.mongodb import MongoDB
from ..models.contact import ContactCreate, ContactResponse, ContactInDB

logger = logging.getLogger(__name__)

class ContactService:
    def __init__(self):
        pass

    def _get_contacts_collection(self):
        return MongoDB.get_collection("contacts")

    async def create_contact(self, contact_data: ContactCreate) -> ContactResponse:
        """Create a new contact submission"""
        try:
            contacts_collection = self._get_contacts_collection()
            
            # Create contact document
            contact_dict = contact_data.dict()
            contact_dict["created_at"] = datetime.utcnow()
            contact_dict["updated_at"] = datetime.utcnow()
            contact_dict["status"] = "new"
            
            # Insert into database
            result = await contacts_collection.insert_one(contact_dict)
            
            if not result.inserted_id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create contact submission"
                )
            
            # Retrieve the created contact
            created_contact = await contacts_collection.find_one({"_id": result.inserted_id})
            
            if not created_contact:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to retrieve created contact"
                )
            
            # Convert ObjectId to string
            created_contact["_id"] = str(created_contact["_id"])
            
            logger.info(f"Contact submission created with ID: {created_contact['_id']}")
            
            return ContactResponse(**created_contact)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating contact submission: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create contact submission"
            )

    async def get_all_contacts(self, skip: int = 0, limit: int = 100) -> List[ContactResponse]:
        """Get all contact submissions (admin function)"""
        try:
            contacts_collection = self._get_contacts_collection()
            
            cursor = contacts_collection.find().sort("created_at", -1).skip(skip).limit(limit)
            contacts = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string for each contact
            for contact in contacts:
                contact["_id"] = str(contact["_id"])
            
            return [ContactResponse(**contact) for contact in contacts]
            
        except Exception as e:
            logger.error(f"Error retrieving contacts: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve contacts"
            )

    async def get_contact_by_id(self, contact_id: str) -> Optional[ContactResponse]:
        """Get a specific contact by ID"""
        try:
            contacts_collection = self._get_contacts_collection()
            
            contact = await contacts_collection.find_one({"_id": ObjectId(contact_id)})
            
            if not contact:
                return None
            
            contact["_id"] = str(contact["_id"])
            return ContactResponse(**contact)
            
        except Exception as e:
            logger.error(f"Error retrieving contact {contact_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve contact"
            )

    async def update_contact_status(self, contact_id: str, status: str) -> ContactResponse:
        """Update contact status (admin function)"""
        try:
            contacts_collection = self._get_contacts_collection()
            
            result = await contacts_collection.update_one(
                {"_id": ObjectId(contact_id)},
                {
                    "$set": {
                        "status": status,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.matched_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Contact not found"
                )
            
            # Return updated contact
            updated_contact = await self.get_contact_by_id(contact_id)
            return updated_contact
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating contact status: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update contact status"
            ) 