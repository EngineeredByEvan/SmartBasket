from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: Optional[str] = "user"

class UserCreate(UserBase):
    password: str

    class Config:
        extra = "allow"


class User(UserBase):
    id: int
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Transaction schemas
class TransactionBase(BaseModel):
    date: Optional[datetime] = None
    items: List[str]

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    user_id: int
    date: datetime

    class Config:
        orm_mode = True

# Prediction schemas
class Basket(BaseModel):
    items: List[str]

class PredictionItem(BaseModel):
    item: str
    probability: float

class Prediction(BaseModel):
    basket: List[str]
    predicted_items: List[PredictionItem]
    timestamp: datetime

class PredictionLog(BaseModel):
    id: int
    user_id: int
    timestamp: datetime
    input_data: List[str]
    output_data: List[str]
    probabilities: List[float]
    feedback: Optional[str] = None

    class Config:
        orm_mode = True

# Item schemas
class ItemBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int

    class Config:
        orm_mode = True

# Model management schemas
class ModelDeploymentCreate(BaseModel):
    model_version: str
    metrics: Dict[str, Any]

class ModelDeployment(ModelDeploymentCreate):
    id: int
    deployed_by: int
    deployment_time: datetime
    status: str

    class Config:
        orm_mode = True