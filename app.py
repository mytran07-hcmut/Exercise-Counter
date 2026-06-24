import cv2
import base64
import numpy as np
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from exercises.squat import SquatExercise
from exercises.pushup import PushupExercise
from pose_detector import PoseCounter

app = Flask(
    __name__,
    template_folder="../frontend",
    static_folder="../static"
)
CORS(app)

# Khởi tạo detector và tất cả bài tập
detector  = PoseCounter()
exercises = {
    "squat" : SquatExercise(),
    "pushup": PushupExercise()
}

# Bài tập đang được chọn — mặc định là squat
current_exercise = "squat"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/process_frame", methods=["POST"])
def process_frame():
    data        = request.get_json()
    image_data  = data["frame"].split(",")[1]
    image_bytes = base64.b64decode(image_data)
    np_array    = np.frombuffer(image_bytes, dtype=np.uint8)
    frame       = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    frame, landmarks = detector.process_frame(frame)

    result = {
        "count"   : 0,
        "stage"   : None,
        "angle"   : 0,
        "detected": False
    }

    if landmarks:
        exercise       = exercises[current_exercise]
        count, stage, angle = exercise.analyze(landmarks)
        result = {
            "count"   : count,
            "stage"   : stage,
            "angle"   : angle,
            "detected": True
        }

    _, buffer       = cv2.imencode(".jpg", frame)
    frame_base64    = base64.b64encode(buffer).decode("utf-8")
    result["frame"] = f"data:image/jpeg;base64,{frame_base64}"

    return jsonify(result)


@app.route("/set_exercise", methods=["POST"])
def set_exercise():
    """Đổi bài tập đang chạy."""
    global current_exercise
    data             = request.get_json()
    name             = data.get("exercise", "squat")

    if name not in exercises:
        return jsonify({"status": "error", "message": "Bài tập không tồn tại"}), 400

    current_exercise = name
    exercises[current_exercise].reset()
    return jsonify({"status": "ok", "exercise": current_exercise})


@app.route("/reset", methods=["POST"])
def reset():
    """Reset bộ đếm của bài tập hiện tại."""
    exercises[current_exercise].reset()
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)