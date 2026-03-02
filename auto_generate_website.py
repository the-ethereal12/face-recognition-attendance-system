import os

# Your existing project folder
project_folder = "face_attendance"

# Create folders
os.makedirs(project_folder, exist_ok=True)
templates_folder = os.path.join(project_folder, "templates")
static_folder = os.path.join(project_folder, "static")
os.makedirs(templates_folder, exist_ok=True)
os.makedirs(static_folder, exist_ok=True)

# ---------------- app.py ----------------
app_py_content = '''from flask import Flask, render_template, Response, jsonify
import cv2
import pickle
import os

app = Flask(__name__)

# Load Haar cascade
face_cascade = cv2.CascadeClassifier('haarcascade/haarcascade_frontalface_default.xml')

# Load trained model (if exists)
model_path = os.path.join('models','trained_model.pkl')
if os.path.exists(model_path):
    with open(model_path,'rb') as f:
        model = pickle.load(f)
else:
    model = None

# Camera
cap = cv2.VideoCapture(0)
camera_on = True

# Attendance dictionary
attendance = {}

def generate_frames():
    global cap, camera_on, attendance
    while camera_on:
        success, frame = cap.read()
        if not success:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray,1.3,5)
        for (x,y,w,h) in faces:
            roi_gray = gray[y:y+h,x:x+w]
            if model:
                roi_resized = cv2.resize(roi_gray,(100,100)).flatten().reshape(1,-1)
                name = model.predict(roi_resized)[0]
                attendance[name] = "Present"
            else:
                name = "Unknown"
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.putText(frame,name,(x,y-10),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,0),2)
        ret, buffer = cv2.imencode('.jpg',frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\\r\\nContent-Type: image/jpeg\\r\\n\\r\\n'+frame_bytes+b'\\r\\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    if camera_on:
        return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "Camera is off"

@app.route('/toggle_camera')
def toggle_camera():
    global cap, camera_on
    if camera_on:
        camera_on = False
        cap.release()
        cv2.destroyAllWindows()
    else:
        cap = cv2.VideoCapture(0)
        camera_on = True
    return jsonify({'camera_on':camera_on})

@app.route('/attendance')
def get_attendance():
    data = [{"name":k,"status":v} for k,v in attendance.items()]
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
'''

# ---------------- index.html ----------------
index_html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>Face Attendance Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static',filename='style.css') }}">
</head>
<body>
<div class="d-flex">
    <div class="sidebar bg-dark text-white p-3">
        <h2>Dashboard</h2>
        <a href="#">Home</a>
        <a href="#">Attendance</a>
        <a href="#">Reports</a>
    </div>
    <div class="main flex-fill p-4">
        <h1 class="mb-4">Face Attendance System</h1>
        <div class="mb-4">
            <img id="video_feed" src="/video" class="img-fluid border">
            <button id="toggle_button" class="btn btn-danger mt-2">Stop Camera</button>
        </div>
        <div>
            <h3>Attendance Today</h3>
            <table class="table table-striped" id="attendance_table">
                <thead><tr><th>Name</th><th>Status</th></tr></thead>
                <tbody></tbody>
            </table>
        </div>
    </div>
</div>
<script src="{{ url_for('static', filename='script.js') }}"></script>
</body>
</html>'''

# ---------------- style.css ----------------
style_css_content = '''.sidebar { min-width:200px; }
.sidebar a { color:#fff; display:block; margin:10px 0; text-decoration:none; }
.sidebar a:hover { background-color:#495057; padding-left:10px; border-radius:5px; }
.present { background-color:#d4edda; }
.absent { background-color:#f8d7da; }'''

# ---------------- script.js ----------------
script_js_content = '''const button=document.getElementById('toggle_button');
const video=document.getElementById('video_feed');
button.addEventListener('click',()=>{
    fetch('/toggle_camera').then(res=>res.json()).then(data=>{
        if(data.camera_on){button.textContent='Stop Camera';video.src='/video?'+new Date().getTime();}
        else{button.textContent='Start Camera';video.src='';}
    });
});
function updateAttendance(){
    fetch('/attendance').then(res=>res.json()).then(data=>{
        const tbody=document.querySelector('#attendance_table tbody');
        tbody.innerHTML='';
        data.forEach(student=>{
            const row=document.createElement('tr');
            row.className=student.status==='Present'?'present':'absent';
            row.innerHTML=`<td>${student.name}</td><td>${student.status}</td>`;
            tbody.appendChild(row);
        });
    });
}
setInterval(updateAttendance,3000);
updateAttendance();'''

# ---------------- Write all files ----------------
files_to_create = {
    "app.py": app_py_content,
    "templates/index.html": index_html_content,
    "static/style.css": style_css_content,
    "static/script.js": script_js_content
}

for path, content in files_to_create.items():
    full_path = os.path.join(project_folder, path.replace("/", os.sep))
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"All website files created automatically in '{project_folder}'!")
print("Run 'python app.py' inside that folder to start the dashboard.")