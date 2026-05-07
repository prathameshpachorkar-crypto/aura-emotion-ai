import cv2
import numpy as np
import tensorflow as tf
import base64
from config import MODEL_PATH, EMOTION_LABELS
from emotion_detection.face_detector import detect_faces

# Load model globally to avoid reloading on every frame
try:
    emotion_model = tf.keras.models.load_model(MODEL_PATH)
    print("Emotion model loaded successfully.")
except Exception as e:
    print(f"Warning: Could not load model. Did you run train_emotion_model.py? Error: {e}")
    emotion_model = None

# Global variable to store the latest detected emotion
LATEST_EMOTION = "Neutral"
CAMERA_ACTIVE = True

def set_camera_state(state):
    global CAMERA_ACTIVE
    CAMERA_ACTIVE = state

def predict_emotion(face_img):
    """ Runs CNN model on a 48x48 grayscale cropped face. """
    if emotion_model is None:
        return "Neutral"
        
    face_img = cv2.resize(face_img, (48, 48))
    face_img = np.expand_dims(face_img, axis=0)
    face_img = np.expand_dims(face_img, axis=-1)
    face_img = face_img.astype('float32') / 255.0 # Apply same normalization as training!
    
    predictions = emotion_model.predict(face_img, verbose=0)
    max_index = int(np.argmax(predictions))
    return EMOTION_LABELS[max_index]

def process_image_data(image_data):
    """ Processes a base64 encoded image string from the frontend. """
    global LATEST_EMOTION, CAMERA_ACTIVE
    
    if not CAMERA_ACTIVE:
        return LATEST_EMOTION

    try:
        # Decode base64 image
        encoded_data = image_data.split(',')[1] if ',' in image_data else image_data
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return LATEST_EMOTION

        faces, gray_frame = detect_faces(frame)
        
        if len(faces) > 0:
            # Predict emotion for the first face found
            (x, y, w, h) = faces[0]
            roi_gray = gray_frame[y:y+h, x:x+w]
            emotion = predict_emotion(roi_gray)
            LATEST_EMOTION = emotion
            
        return LATEST_EMOTION
    except Exception as e:
        print(f"Error processing image: {e}")
        return LATEST_EMOTION