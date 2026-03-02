import cv2
import numpy as np
import os
from datetime import datetime

# =========================
# LOAD TRAINED MODEL
# =========================

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("face_model.xml")

# Load labels correctly
labels = np.load("labels.npy", allow_pickle=True).item()

# IMPORTANT: labels already in correct format
names = labels   # {0:'John',1:'Raina'}

# =========================
# LOAD FACE DETECTOR
# =========================

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# =========================
# START CAMERA
# =========================

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Camera not working")
    exit()

# =========================
# ATTENDANCE FILE
# =========================

attendance_file = "attendance.csv"

# Create file if not exists
if not os.path.exists(attendance_file):
    with open(attendance_file, "w") as f:
        f.write("Name,Time,Confidence\n")

# Track marked attendance
marked = set()

print("====================================")
print(" Face Attendance System Started")
print(" Press ESC to exit")
print("====================================")

# =========================
# MAIN LOOP
# =========================

while True:

    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=5,
        minSize=(50,50)
    )

    for (x,y,w,h) in faces:

        face = gray[y:y+h, x:x+w]

        label, confidence = recognizer.predict(face)

        confidence_percent = round(100 - confidence, 2)

        # Recognized face
        if confidence < 80 and label in names:

            name = names[label]

            display_text = f"{name} ({confidence_percent}%)"

            color = (0,255,0)

            # Mark attendance only once
            if name not in marked:

                marked.add(name)

                time_now = datetime.now().strftime("%H:%M:%S")

                with open(attendance_file, "a") as f:
                    f.write(f"{name},{time_now},{confidence_percent}%\n")

                print(f"Attendance marked: {name}")

        else:

            name = "Unknown"
            display_text = "Unknown"
            color = (0,0,255)

        # Draw rectangle
        cv2.rectangle(frame, (x,y), (x+w,y+h), color, 2)

        # Show name
        cv2.putText(
            frame,
            display_text,
            (x, y-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2
        )

    # Show window
    cv2.imshow("Face Attendance System", frame)

    # Exit on ESC key
    key = cv2.waitKey(1)

    if key == 27:
        break

# =========================
# CLEANUP
# =========================

cap.release()
cv2.destroyAllWindows()

print("System Closed")