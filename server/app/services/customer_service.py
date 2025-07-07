import logging
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status, UploadFile
import pandas as pd
import io
from ..db.mongodb import MongoDB
from ..models.customer import CustomerCreate, Customer

logger = logging.getLogger(__name__)

class CustomerService:
    def __init__(self, db: MongoDB):
        self.db = db

    async def import_customers(self, file: UploadFile, user_id: str) -> List[Customer]:
        """Import customers from uploaded file"""
        try:
            # Read file content
            content = await file.read()
            
            # Determine file type and read accordingly
            if file.filename.endswith('.xlsx'):
                df = pd.read_excel(io.BytesIO(content))
            elif file.filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(content))
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unsupported file format. Please upload .xlsx or .csv files."
                )

            customers = []
            for _, row in df.iterrows():
                # Create customer from row data
                customer_data = {
                    "email": row.get('email', ''),
                    "name": row.get('name', ''),
                    "phone": row.get('phone', ''),
                    "company": row.get('company', ''),
                    "user_id": user_id,
                    "created_at": datetime.utcnow()
                }
                
                # Validate required fields
                if not customer_data["email"]:
                    continue
                
                customers.append(Customer(**customer_data))

            # Store in database (mock for now)
            logger.info(f"Imported {len(customers)} customers for user {user_id}")
            
            return customers

        except Exception as e:
            logger.error(f"Error importing customers: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error importing customers: {str(e)}"
            )

    async def get_customers(self, user_id: str) -> List[Customer]:
        """Get all customers for a user"""
        try:
            # Mock implementation for development
            return []
        except Exception as e:
            logger.error(f"Error getting customers: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving customers"
            )

    async def create_customer(self, customer: CustomerCreate, user_id: str) -> Customer:
        """Create a new customer"""
        try:
            customer_data = Customer(
                **customer.dict(),
                user_id=user_id,
                created_at=datetime.utcnow()
            )
            
            # Mock implementation for development
            return customer_data
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating customer"
            ) 