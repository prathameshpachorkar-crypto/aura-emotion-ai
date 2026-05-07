import os
import sys
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, AveragePooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping

# Append parent directory so we can import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.preprocessing import load_fer2013_data

def build_model():
    # Building a custom CNN optimized for 48x48 grayscale face images.
    model = Sequential([
        Conv2D(64, (3, 3), activation='relu', input_shape=(48, 48, 1)),
        BatchNormalization(),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),

        Conv2D(128, (3, 3), activation='relu'),
        BatchNormalization(),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),

        Conv2D(256, (3, 3), activation='relu'),
        BatchNormalization(),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),

        Flatten(),
        Dense(512, activation='relu'),
        BatchNormalization(),
        Dropout(0.5),
        Dense(7, activation='softmax') # 7 emotion classes
    ])
    
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

if __name__ == "__main__":
    print("Loading FER2013 dataset... This might take a minute.")
    X, y = load_fer2013_data('../dataset/fer2013.csv')
    
    model = build_model()
    
    # Save the best model during training
    checkpoint = ModelCheckpoint('../models/emotion_model.h5', monitor='val_accuracy', verbose=1, save_best_only=True, mode='max')
    early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    
    print("Starting training...")
    # Training for 50 epochs is usually enough for a baseline ~60-65% accuracy on FER2013
    model.fit(X, y, batch_size=64, epochs=50, validation_split=0.2, callbacks=[checkpoint, early_stop])
    print("Training complete. Model saved to models/emotion_model.h5")