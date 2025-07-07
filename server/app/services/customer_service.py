import logging
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status, UploadFile
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
import io
from ..db.mongodb import MongoDB
from ..models.customer import CustomerCreate, Customer

logger = logging.getLogger(__name__)

class CustomerService:
    def __init__(self, db: MongoDB):
        self.db = db

    def _get_customers_collection(self):
        """Get the customers collection from MongoDB."""
        try:
            return MongoDB.get_collection("customers")
        except Exception as e:
            logger.warning(f"Database not available: {e}")
            return None

    async def import_customers(self, file: UploadFile, user_id: str) -> List[Customer]:
        """Import customers from uploaded file."""
        if not PANDAS_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="File import functionality not available"
            )
            
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
            customers_collection = self._get_customers_collection()
            
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
                
                # Insert into database
                result = await customers_collection.insert_one(customer_data)
                customer_data["id"] = str(result.inserted_id)
                customers.append(Customer(**customer_data))

            logger.info(f"Imported {len(customers)} customers for user {user_id}")
            
            return customers

        except Exception as e:
            logger.error(f"Error importing customers: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error importing customers: {str(e)}"
            )

    async def get_customers(self, user_id: str) -> List[Customer]:
        """Get all customers for a user."""
        try:
            customers_collection = self._get_customers_collection()
            cursor = customers_collection.find({"user_id": user_id}).sort("created_at", -1)
            customers = await cursor.to_list(length=None)
            
            return [
                Customer(
                    id=str(customer["_id"]),
                    email=customer["email"],
                    name=customer.get("name"),
                    phone=customer.get("phone"),
                    company=customer.get("company"),
                    user_id=customer["user_id"],
                    created_at=customer["created_at"]
                )
                for customer in customers
            ]
        except Exception as e:
            logger.error(f"Error getting customers: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving customers"
            )

    async def create_customer(self, customer: CustomerCreate, user_id: str) -> Customer:
        """Create a new customer."""
        try:
            customers_collection = self._get_customers_collection()
            
            customer_data = {
                **customer.dict(),
                "user_id": user_id,
                "created_at": datetime.utcnow()
            }
            
            result = await customers_collection.insert_one(customer_data)
            customer_data["id"] = str(result.inserted_id)
            
            return Customer(**customer_data)
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating customer"
            ) 