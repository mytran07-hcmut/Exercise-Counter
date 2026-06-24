import numpy as np
import mediapipe as mp
import cv2

# Khởi tạo module Pose của MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


def calculate_angle(a, b, c):
    """
    Tính góc tại điểm B, tạo bởi 3 điểm A - B - C.
    """
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    ba = a - b
    bc = c - b

    angle = np.degrees(
        np.arctan2(bc[1], bc[0]) - np.arctan2(ba[1], ba[0])
    )

    angle = abs(angle)
    if angle > 180:
        angle = 360 - angle

    return round(angle, 2)


class PoseCounter:
    def __init__(self):
        self.counter = 0
        self.stage = None
        # Khởi tạo model Pose của MediaPipe
        self.pose = mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def process_frame(self, frame):
        """
        Nhận vào một frame từ camera, trả về frame đã được vẽ landmarks
        và dictionary chứa tọa độ các điểm khớp.

        Tham số:
            frame: hình ảnh từ camera (dạng BGR — định dạng mặc định của OpenCV)

        Trả về:
            frame      : frame gốc đã vẽ thêm landmarks
            landmarks  : dictionary { tên_khớp: [x, y] } hoặc None nếu không thấy người
        """

        # Chuyển màu BGR → RGB vì MediaPipe yêu cầu ảnh RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Xử lý frame qua model MediaPipe
        results = self.pose.process(image)

        # Nếu không phát hiện người → trả về None
        if not results.pose_landmarks:
            return frame, None

        # Vẽ landmarks lên frame gốc để hiển thị
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

        # Lấy danh sách landmarks và kích thước frame
        lm = results.pose_landmarks.landmark
        h, w = frame.shape[:2]

        # Chuyển landmarks từ tọa độ tương đối (0-1) sang pixel thực tế
        landmarks = {
    # Chân — dùng cho Squat
    "left_hip"      : [lm[mp_pose.PoseLandmark.LEFT_HIP].x * w,
                       lm[mp_pose.PoseLandmark.LEFT_HIP].y * h],
    "left_knee"     : [lm[mp_pose.PoseLandmark.LEFT_KNEE].x * w,
                       lm[mp_pose.PoseLandmark.LEFT_KNEE].y * h],
    "left_ankle"    : [lm[mp_pose.PoseLandmark.LEFT_ANKLE].x * w,
                       lm[mp_pose.PoseLandmark.LEFT_ANKLE].y * h],
    "right_hip"     : [lm[mp_pose.PoseLandmark.RIGHT_HIP].x * w,
                       lm[mp_pose.PoseLandmark.RIGHT_HIP].y * h],
    "right_knee"    : [lm[mp_pose.PoseLandmark.RIGHT_KNEE].x * w,
                       lm[mp_pose.PoseLandmark.RIGHT_KNEE].y * h],
    "right_ankle"   : [lm[mp_pose.PoseLandmark.RIGHT_ANKLE].x * w,
                       lm[mp_pose.PoseLandmark.RIGHT_ANKLE].y * h],

    # Tay — dùng cho Push-up, Bicep Curl
    "left_shoulder" : [lm[mp_pose.PoseLandmark.LEFT_SHOULDER].x * w,
                       lm[mp_pose.PoseLandmark.LEFT_SHOULDER].y * h],
    "left_elbow"    : [lm[mp_pose.PoseLandmark.LEFT_ELBOW].x * w,
                       lm[mp_pose.PoseLandmark.LEFT_ELBOW].y * h],
    "left_wrist"    : [lm[mp_pose.PoseLandmark.LEFT_WRIST].x * w,
                       lm[mp_pose.PoseLandmark.LEFT_WRIST].y * h],
    "right_shoulder": [lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * w,
                       lm[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * h],
    "right_elbow"   : [lm[mp_pose.PoseLandmark.RIGHT_ELBOW].x * w,
                       lm[mp_pose.PoseLandmark.RIGHT_ELBOW].y * h],
    "right_wrist"   : [lm[mp_pose.PoseLandmark.RIGHT_WRIST].x * w,
                       lm[mp_pose.PoseLandmark.RIGHT_WRIST].y * h],
}

        return frame, landmarks

    def count(self, angle, down_threshold, up_threshold):
        """
        Cập nhật trạng thái và bộ đếm dựa trên góc hiện tại.
        """
        if angle < down_threshold:
            self.stage = "down"

        if angle > up_threshold and self.stage == "down":
            self.stage = "up"
            self.counter += 1

        return self.counter, self.stage

    def reset(self):
        """
        Reset bộ đếm về 0 khi bắt đầu set mới.
        """
        self.counter = 0
        self.stage = None

if __name__ == "__main__":
    import cv2

    cap = cv2.VideoCapture(1)  # Mở webcam (0 = camera mặc định)
    detector = PoseCounter()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Xử lý frame
        frame, landmarks = detector.process_frame(frame)

        # Hiển thị frame lên cửa sổ
        cv2.imshow("Pose Detection Test", frame)

        # Nếu landmarks phát hiện được → in ra terminal
        if landmarks:
            print("Phát hiện người! Đầu gối trái:", landmarks["left_knee"])

        # Nhấn Q để thoát
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()