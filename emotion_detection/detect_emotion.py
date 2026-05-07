import cv2
import numpy as np
import tensorflow as tf
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

def generate_frames():
    """ Generator function for Flask video streaming. """
    global LATEST_EMOTION, CAMERA_ACTIVE
    
    while True:
        if not CAMERA_ACTIVE:
            import time
            time.sleep(1)
            continue
            
        camera = cv2.VideoCapture(0) # 0 is usually the default laptop webcam
        while CAMERA_ACTIVE:
            success, frame = camera.read()
            if not success:
                break
                
            faces, gray_frame = detect_faces(frame)
            
            for (x, y, w, h) in faces:
                # Crop the face
                roi_gray = gray_frame[y:y+h, x:x+w]
                
                # Predict
                emotion = predict_emotion(roi_gray)
                LATEST_EMOTION = emotion # Update global state for the chatbot
                
                # Draw rectangle and text
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
                cv2.putText(frame, emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            # Yield in multipart format for continuous video stream
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                   
        if 'camera' in locals() and camera.isOpened():
            camera.release()