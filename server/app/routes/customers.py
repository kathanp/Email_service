from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
from ..models.customer import CustomerCreate, Customer
from ..models.user import User
from ..services.customer_service import CustomerService
from ..api.deps import get_current_user
from ..db.mongodb import MongoDB

router = APIRouter()

# Initialize services
mongodb = MongoDB()
customer_service = CustomerService(mongodb)

@router.post("/", response_model=Customer)
async def create_customer(
    customer: CustomerCreate,
    current_user: User = Depends(get_current_user)
):
    return await customer_service.create_customer(customer, current_user.id)

@router.get("/", response_model=List[Customer])
async def get_customers(current_user: User = Depends(get_current_user)):
    return await customer_service.get_customers(current_user.id)

@router.post("/import")
async def import_customers(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    return await customer_service.import_customers(file, current_user.id) 