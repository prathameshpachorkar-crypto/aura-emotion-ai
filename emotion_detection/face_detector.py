import cv2
from config import HAAR_CASCADE_PATH

# Initialize Haar Cascade once to save memory overhead
face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)

def detect_faces(frame):
    """ Returns bounding boxes for faces in the frame. """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Tweak scaleFactor and minNeighbors if detection is too sensitive or missing faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(48, 48))
    return faces, gray