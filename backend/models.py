from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float, JSON, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")  # "user" or "admin"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    
    transactions = relationship("Transaction", back_populates="user")
    prediction_logs = relationship("PredictionLog", back_populates="user")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime, index=True)
    items = Column(JSON)  # List of purchased items
    
    user = relationship("User", back_populates="transactions")

class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, index=True)
    input_data = Column(JSON)  # Basket items
    output_data = Column(JSON)  # Predicted items
    probabilities = Column(JSON)  # Prediction probabilities
    feedback = Column(String, nullable=True)  # User feedback on prediction (if any)
    
    user = relationship("User", back_populates="prediction_logs")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    category = Column(String, index=True)
    description = Column(Text, nullable=True)
    attributes = Column(JSON, nullable=True)  # Additional item attributes

class ModelDeployment(Base):
    __tablename__ = "model_deployments"

    id = Column(Integer, primary_key=True, index=True)
    model_version = Column(String, index=True)
    deployed_by = Column(Integer, ForeignKey("users.id"))
    deployment_time = Column(DateTime)
    status = Column(String)  # "successful", "failed", etc.
    metrics = Column(JSON)  # Model performance metrics