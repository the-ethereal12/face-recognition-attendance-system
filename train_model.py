import cv2
import os
import pickle
from pathlib import Path
import numpy as np

# Paths
dataset_path = "dataset"
model_path = "models/lbph_model.yml"
labels_path = "models/labels.pkl"

# Haar cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

faces = []  # list of 2D grayscale arrays
labels = [] # list of integers
label_dict = {}
label_counter = 0

print("Preparing dataset...")

for person_dir in os.listdir(dataset_path):
    person_path = os.path.join(dataset_path, person_dir)
    if os.path.isdir(person_path):
        print(f"Processing {person_dir}...")
        label_dict[label_counter] = person_dir
        for img_name in os.listdir(person_path):
            img_path = os.path.join(person_path, img_name)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            detected_faces = face_cascade.detectMultiScale(img, 1.3, 5)
            for (x, y, w, h) in detected_faces:
                roi = img[y:y+h, x:x+w]
                roi_resized = cv2.resize(roi, (100,100))
                roi_resized = np.array(roi_resized, dtype=np.uint8)  # <--- Force uint8
                faces.append(roi_resized)
                labels.append(label_counter)
        label_counter += 1

if len(faces) == 0:
    print("No faces found! Check your dataset.")
    exit()

# Convert labels only
labels = np.array(labels, dtype=np.int32)

# Train LBPH recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.train(faces, labels)  # faces=list of np.uint8, labels=np.int32

# Save model
Path("models").mkdir(exist_ok=True)
recognizer.save(model_path)

# Save label dict
with open(labels_path,"wb") as f:
    pickle.dump(label_dict, f)

print("Model trained successfully!")
print(f"Saved model at {model_path}")
print(f"Saved labels at {labels_path}")
