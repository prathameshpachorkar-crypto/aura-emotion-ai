import numpy as np
import pandas as pd

def load_fer2013_data(csv_path):
    # Note to self: FER2013 csv contains "emotion" and "pixels" columns.
    # Pixels are space-separated strings.
    data = pd.read_csv(csv_path)
    
    pixels = data['pixels'].tolist()
    faces = []
    
    for pixel_sequence in pixels:
        face = [int(pixel) for pixel in pixel_sequence.split(' ')]
        face = np.asarray(face).reshape(48, 48, 1)
        faces.append(face)
        
    faces = np.asarray(faces)
    faces = faces.astype('float32') / 255.0 # Always normalize!
    
    emotions = pd.get_dummies(data['emotion']).values
    return faces, emotions