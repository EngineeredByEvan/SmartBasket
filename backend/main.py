from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import tensorflow as tf
import numpy as np
import pickle
import os
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from fastapi.logger import logger
import json
import logging
logging.basicConfig(level=logging.DEBUG)

# Import database models and schemas
from database import SessionLocal, engine
import models, schemas

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SmartBasket API",
    description="Intelligent shopping prediction system API",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = "your-secret-key-here" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication utilities
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# Load ML models and encoders
class PredictionModel:
    def __init__(self):
        self.model = None
        self.mlb = None
        self.unique_items = None
        self.load_model()

    def load_model(self):
        model_path = os.getenv("MODEL_PATH", "models/current")
        logger.info(f"Attempting to load model from: {model_path}")
        
        try:
            if not os.path.exists(f"{model_path}/grocery_predictor_model.h5"):
                logger.error(f"Model file not found at {model_path}/grocery_predictor_model.h5")
                return
                
            # Load without compilation
            self.model = tf.keras.models.load_model(f"{model_path}/grocery_predictor_model.h5", compile=False)
            logger.info("Model loaded successfully")
            
            if not os.path.exists(f"{model_path}/mlb_encoder.pkl"):
                logger.error(f"MultiLabelBinarizer file not found at {model_path}/mlb_encoder.pkl")
                return
            with open(f"{model_path}/mlb_encoder.pkl", "rb") as f:
                self.mlb = pickle.load(f)
            logger.info("MultiLabelBinarizer loaded successfully")
            
            if not os.path.exists(f"{model_path}/item_mapping.json"):
                logger.error(f"Item mapping file not found at {model_path}/item_mapping.json")
                return
            with open(f"{model_path}/item_mapping.json", "r") as f:
                self.unique_items = json.load(f)
            logger.info("Item mapping loaded successfully")
            logger.info(f"Loaded {len(self.unique_items)} unique items")
            
            # Temporarily comment out the sample prediction validation
            # sample_input = np.zeros((1, len(self.mlb.classes_)))
            # sample_prediction = self.model.predict(sample_input)
            # logger.info(f"Model validation successful: prediction shape {sample_prediction.shape}")
            
        except Exception as e:
            logger.error(f"Failed to load model components: {str(e)}")
            self.model = None
            self.mlb = None
            self.unique_items = None



prediction_model = PredictionModel()

# API Routes
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# User management endpoints
@app.post("/api/v1/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    logger.info(f"Incoming user payload: {user}")

    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role or "user"
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    print("✅ User created successfully:", db_user.username)
    return db_user

@app.get("/api/v1/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# Transaction endpoints
@app.post("/api/v1/transactions/", response_model=schemas.Transaction)
def create_transaction(
    transaction: schemas.TransactionCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_transaction = models.Transaction(
        user_id=current_user.id,
        date=transaction.date or datetime.now(),
        items=transaction.items
    )
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@app.get("/api/v1/transactions/", response_model=List[schemas.Transaction])
def read_transactions(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return transactions

# Prediction endpoints
@app.post("/api/v1/predictions/next-item", response_model=schemas.Prediction)
def predict_next_item(
    basket: schemas.Basket,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # First, check if model components are loaded
    if prediction_model.model is None or prediction_model.mlb is None or prediction_model.unique_items is None:
        logger.error("Prediction model components not loaded correctly")
        raise HTTPException(status_code=500, detail="Model components not available")
    
    try:
        # Log input data for debugging
        logger.info(f"Received basket items: {basket.items}")
        
        # Validate input items against known items
        unknown_items = [item for item in basket.items if item not in prediction_model.unique_items]
        if unknown_items:
            logger.warning(f"Unknown items in basket: {unknown_items}")
        
        # Transform items using the MultiLabelBinarizer
        try:
            basket_encoded = prediction_model.mlb.transform([basket.items])
            logger.debug(f"Successfully encoded basket: shape {basket_encoded.shape}")
        except Exception as e:
            logger.error(f"Error encoding basket items: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error encoding items: {str(e)}")
        
        # Make prediction
        try:
            prediction = prediction_model.model.predict(basket_encoded)
            logger.debug(f"Prediction made successfully: shape {prediction.shape}")
        except Exception as e:
            logger.error(f"Error during model prediction: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
        
        # Get top 5 predicted items
        try:
            top_indices = np.argsort(prediction[0])[-5:][::-1]
            logger.debug(f"Top indices from prediction: {top_indices}")
            
            # Create a reverse mapping from index to item name
            idx_to_item = {int(v): k for k, v in prediction_model.unique_items.items()}
            logger.debug(f"Created reverse mapping with {len(idx_to_item)} items")
            
            # Map indices to item names using the reverse mapping
            top_items = [idx_to_item.get(int(idx), f"Unknown-{idx}") for idx in top_indices]
            top_probabilities = [float(prediction[0][idx]) * 100 for idx in top_indices]
            
            logger.debug(f"Top items: {top_items}")
            logger.debug(f"Top probabilities: {top_probabilities}")
        except Exception as e:
            logger.error(f"Error processing prediction results: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing results: {str(e)}")
        
        # Create prediction result
        result = {
            "basket": basket.items,
            "predicted_items": [
                {"item": item, "probability": prob} 
                for item, prob in zip(top_items, top_probabilities)
            ],
            "timestamp": datetime.now()
        }
        
        # Log prediction to database (optional)
        try:
            db_prediction = models.PredictionLog(
                user_id=current_user.id,
                input_data=basket.items,
                output_data=top_items,
                probabilities=[float(p) for p in top_probabilities],
                timestamp=datetime.now()
            )
            db.add(db_prediction)
            db.commit()
        except Exception as e:
            logger.error(f"Error logging prediction to database: {str(e)}")
            # Don't fail the request if DB logging fails
        
        return result
    
    except Exception as e:
        # Catch-all for any other exceptions
        logger.error(f"Unexpected error in prediction endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

# Model management endpoints (admin only)
@app.post("/api/v1/models/deploy", response_model=schemas.ModelDeployment)
def deploy_model(
    model_info: schemas.ModelDeploymentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if user has admin rights
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # In a real implementation, this would handle model deployment
    # For now, just record the deployment request
    db_deployment = models.ModelDeployment(
        model_version=model_info.model_version,
        deployed_by=current_user.id,
        deployment_time=datetime.now(),
        status="successful",
        metrics=model_info.metrics
    )
    
    db.add(db_deployment)
    db.commit()
    db.refresh(db_deployment)
    
    # In production, you would trigger model reloading here
    # prediction_model.load_model()
    
    return db_deployment

# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)