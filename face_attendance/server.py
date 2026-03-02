print("UI VERSION ACTIVE")

from flask import Flask, render_template_string, request, jsonify
import cv2
import numpy as np
import base64

app = Flask(__name__)

# Load Haarcascade from OpenCV directly
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Face Attendance</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body{
    font-family: Arial, sans-serif;
    background: linear-gradient(135deg,#667eea,#764ba2);
    text-align:center;
    margin:0;
    color:white;
}
.container{
    margin-top:40px;
}
video{
    width:90%;
    max-width:350px;
    border-radius:15px;
    box-shadow:0 8px 20px rgba(0,0,0,0.3);
}
button{
    margin-top:20px;
    padding:12px 25px;
    border:none;
    background:#00c9a7;
    color:white;
    font-size:16px;
    border-radius:8px;
}
button:hover{
    background:#00a78e;
}
#result{
    margin-top:20px;
    font-size:20px;
    font-weight:bold;
}
</style>
</head>
<body>

<div class="container">
<h2>📸 Face Attendance System</h2>

<video id="video" autoplay playsinline></video>
<br>
<button onclick="capture()">Mark Attendance</button>

<div id="result"></div>
</div>

<script>
const video = document.getElementById("video");

// Open phone camera
navigator.mediaDevices.getUserMedia({video:true})
.then(stream => {
    video.srcObject = stream;
})
.catch(err => {
    alert("Camera permission required.");
});

function capture(){
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    const image = canvas.toDataURL("image/jpeg");

    fetch("/detect",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({image:image})
    })
    .then(res => res.json())
    .then(data=>{
        document.getElementById("result").innerText =
        "Faces Detected: " + data.count;
    });
}
</script>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/detect", methods=["POST"])
def detect():
    image_data = request.json["image"].split(",")[1]
    img_bytes = base64.b64decode(image_data)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    return jsonify({"count": len(faces)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)