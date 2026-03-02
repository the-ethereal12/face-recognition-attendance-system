from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

# Dummy data for dashboard
faces_detected = 5
camera_status = "Active"
start_time = datetime.now()

@app.route('/')
def index():
    # Calculate uptime
    now = datetime.now()
    uptime_seconds = int((now - start_time).total_seconds())
    h = uptime_seconds // 3600
    m = (uptime_seconds % 3600) // 60
    s = uptime_seconds % 60
    uptime = f"{h:02d}:{m:02d}:{s:02d}"

    data = {
        "faces_detected": faces_detected,
        "camera_status": camera_status,
        "uptime": uptime
    }
    return render_template('index.html', data=data)

if __name__ == '__main__':
    print("Dashboard Flask app running on http://127.0.0.1:5000")
    app.run(debug=True)