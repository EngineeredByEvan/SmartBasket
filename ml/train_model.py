import pandas as pd
import numpy as np
import os
import pickle
import json
from datetime import datetime
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, TensorBoard
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import classification_report
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_data(file_path):
    """Load and preprocess transaction data"""
    logger.info(f"Loading data from {file_path}")
    
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Loaded {len(df)} transactions")
        return df
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise

def preprocess_data(df):
    """Preprocess the transaction data into sequence format"""
    logger.info("Preprocessing data")
    
    # Group transactions by member and date
    grouped = df.groupby(['Member_number', 'Date'])['itemDescription'].apply(list)
    
    # Filter out transactions with fewer than 2 items
    filtered = grouped[grouped.apply(len) > 1]
    logger.info(f"Found {len(filtered)} valid transactions after filtering")
    
    # Create sequences for training (previous items -> next item)
    X = []
    y = []
    
    for items in filtered:
        for i in range(1, len(items)):
            # Items bought so far
            X.append(items[:i])
            # Next item
            y.append(items[i])
    
    logger.info(f"Created {len(X)} training sequences")
    return X, y

def encode_data(X, y):
    """Encode the input sequences and output labels"""
    logger.info("Encoding data")
    
    # Encode input sequences (multiple items)
    mlb = MultiLabelBinarizer()
    X_encoded = mlb.fit_transform(X)
    
    # Encode output labels (single item)
    unique_items = list(set(y))
    item_to_index = {item: i for i, item in enumerate(unique_items)}
    y_encoded = np.array([item_to_index[item] for item in y])
    y_encoded = to_categorical(y_encoded, num_classes=len(unique_items))
    
    logger.info(f"Input shape: {X_encoded.shape}, Output shape: {y_encoded.shape}")
    logger.info(f"Number of unique items: {len(unique_items)}")
    
    return X_encoded, y_encoded, mlb, unique_items

def build_model(input_dim, output_dim, dropout_rate=0.2):
    """Build a neural network model for next item prediction"""
    logger.info(f"Building model with input_dim={input_dim}, output_dim={output_dim}")
    
    model = Sequential()
    model.add(Dense(256, input_dim=input_dim, activation='relu'))
    model.add(Dropout(dropout_rate))
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(dropout_rate))
    model.add(Dense(output_dim, activation='softmax'))
    
    model.compile(
        loss='categorical_crossentropy',
        optimizer='adam',
        metrics=['accuracy']
    )
    
    logger.info(f"Model compiled successfully")
    return model

def train_model(model, X_train, y_train, X_val, y_val, epochs=30, batch_size=32, model_dir="models"):
    """Train the model with early stopping and checkpoints"""
    logger.info(f"Training model with {len(X_train)} samples")
    
    # Create model directory if it doesn't exist
    os.makedirs(model_dir, exist_ok=True)
    
    # Set up callbacks
    callbacks = [
        EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True
        ),
        ModelCheckpoint(
            filepath=os.path.join(model_dir, "best_model.keras"),
            monitor='val_loss',
            save_best_only=True
        ),
        TensorBoard(
            log_dir=os.path.join(model_dir, "logs"),
            histogram_freq=1
        )
    ]
    
    # Train the model
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=1
    )
    
    logger.info("Model training completed")
    return model, history

def evaluate_model(model, X_test, y_test, unique_items):
    """Evaluate the model and generate classification report"""
    logger.info("Evaluating model")
    
    # Get model predictions
    y_prob = model.predict(X_test)
    y_pred = np.argmax(y_prob, axis=1)
    y_true = np.argmax(y_test, axis=1)
    
    # Convert indices back to item names for interpretability
    class_names = [unique_items[i] for i in range(len(unique_items))]
    
    # Generate classification metrics
    report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True)
    logger.info(f"Test accuracy: {report['accuracy']:.4f}")
    
    # Calculate Top-3 and Top-5 accuracy
    top3_accuracy = 0
    top5_accuracy = 0
    
    for i in range(len(y_true)):
        true_label = y_true[i]
        pred_probs = y_prob[i]
        top_indices = np.argsort(pred_probs)[::-1]
        
        if true_label in top_indices[:3]:
            top3_accuracy += 1
        if true_label in top_indices[:5]:
            top5_accuracy += 1
    
    top3_accuracy /= len(y_true)
    top5_accuracy /= len(y_true)
    
    logger.info(f"Top-3 accuracy: {top3_accuracy:.4f}")
    logger.info(f"Top-5 accuracy: {top5_accuracy:.4f}")
    
    # Add these metrics to the report
    report['top3_accuracy'] = top3_accuracy
    report['top5_accuracy'] = top5_accuracy
    
    return report

def save_model_artifacts(model, mlb, unique_items, metrics, model_dir="models", version=None):
    """Save the model and associated artifacts"""
    if version is None:
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    version_dir = os.path.join(model_dir, version)
    os.makedirs(version_dir, exist_ok=True)
    
    # Save model
    model_path = os.path.join(version_dir, "grocery_predictor_model.keras")
    model.save(model_path)
    logger.info(f"Model saved to {model_path}")
    
    # Save MultiLabelBinarizer
    mlb_path = os.path.join(version_dir, "mlb.pkl")
    with open(mlb_path, "wb") as f:
        pickle.dump(mlb, f)
    logger.info(f"MultiLabelBinarizer saved to {mlb_path}")
    
    # Save unique items
    items_path = os.path.join(version_dir, "unique_items.pkl")
    with open(items_path, "wb") as f:
        pickle.dump(unique_items, f)
    logger.info(f"Unique items saved to {items_path}")
    
    # Save metrics
    metrics_path = os.path.join(version_dir, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"Metrics saved to {metrics_path}")
    
    # Create 'current' symlink to latest version
    current_link = os.path.join(model_dir, "current")
    if os.path.exists(current_link) and os.path.islink(current_link):
        os.unlink(current_link)
    os.symlink(version_dir, current_link, target_is_directory=True)
    logger.info(f"Updated 'current' symlink to {version_dir}")
    
    return version_dir

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Train a grocery prediction model")
    parser.add_argument("--data", type=str, default="./data/Groceries_dataset.csv",
                      help="Path to the grocery dataset CSV")
    parser.add_argument("--model-dir", type=str, default="./models",
                      help="Directory to save model artifacts")
    parser.add_argument("--epochs", type=int, default=30,
                      help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=32,
                      help="Training batch size")
    parser.add_argument("--test-size", type=float, default=0.2,
                      help="Proportion of data to use for testing")
    parser.add_argument("--val-size", type=float, default=0.1,
                      help="Proportion of training data to use for validation")
    parser.add_argument("--dropout", type=float, default=0.2,
                      help="Dropout rate for regularization")
    
    return parser.parse_args()

def main():
    """Main training pipeline function"""
    args = parse_arguments()
    
    try:
        # Load and preprocess data
        df = load_data(args.data)
        X, y = preprocess_data(df)
        X_encoded, y_encoded, mlb, unique_items = encode_data(X, y)
        
        # Split data into train, validation, and test sets
        X_temp, X_test, y_temp, y_test = train_test_split(
            X_encoded, y_encoded, 
            test_size=args.test_size,
            random_state=42
        )
        
        # From the remaining data, create validation set
        val_ratio = args.val_size / (1 - args.test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp,
            test_size=val_ratio,
            random_state=42
        )
        
        logger.info(f"Training set: {X_train.shape[0]} samples")
        logger.info(f"Validation set: {X_val.shape[0]} samples")
        logger.info(f"Test set: {X_test.shape[0]} samples")
        
        # Build and train the model
        model = build_model(
            input_dim=X_train.shape[1],
            output_dim=y_train.shape[1],
            dropout_rate=args.dropout
        )
        
        trained_model, history = train_model(
            model,
            X_train, y_train,
            X_val, y_val,
            epochs=args.epochs,
            batch_size=args.batch_size,
            model_dir=args.model_dir
        )
        
        # Evaluate the model
        metrics = evaluate_model(trained_model, X_test, y_test, unique_items)
        
        # Save model artifacts
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_model_artifacts(
            trained_model,
            mlb,
            unique_items,
            metrics,
            model_dir=args.model_dir,
            version=version
        )
        
        logger.info(f"Model training and evaluation completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error in training pipeline: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)