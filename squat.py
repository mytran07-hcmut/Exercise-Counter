import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from pose_detector import calculate_angle, PoseCounter


class SquatExercise:
    def __init__(self):
        """
        Khởi tạo bài tập Squat với ngưỡng góc chuẩn.
        """
        self.counter = PoseCounter()

        # Ngưỡng góc cho Squat
        self.DOWN_THRESHOLD = 90   # Góc < 90° → tư thế "down" hợp lệ
        self.UP_THRESHOLD   = 160  # Góc > 160° → tư thế "up" hợp lệ

        # Góc hiện tại (để hiển thị lên màn hình)
        self.current_angle  = 0

    def analyze(self, landmarks):
        """
        Phân tích landmarks, tính góc đầu gối và cập nhật bộ đếm.

        Tham số:
            landmarks: dictionary tọa độ các khớp từ process_frame()

        Trả về:
            count : số lần squat hoàn thành
            stage : trạng thái hiện tại ("up" / "down")
            angle : góc đầu gối hiện tại
        """

        # Lấy tọa độ 3 điểm: Hông - Đầu gối - Cổ chân (bên trái)
        hip   = landmarks["left_hip"]
        knee  = landmarks["left_knee"]
        ankle = landmarks["left_ankle"]

        # Tính góc tại đầu gối
        self.current_angle = calculate_angle(hip, knee, ankle)

        # Cập nhật state machine và bộ đếm
        count, stage = self.counter.count(
            self.current_angle,
            down_threshold=self.DOWN_THRESHOLD,
            up_threshold=self.UP_THRESHOLD
        )

        return count, stage, self.current_angle

    def reset(self):
        """
        Reset bài tập về trạng thái ban đầu.
        """
        self.counter.reset()
        self.current_angle = 0

if __name__ == "__main__":
    import cv2
    import sys
    import os

    # Để Python tìm thấy pose_detector.py ở thư mục backend
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from pose_detector import PoseCounter
    
    cap = cv2.VideoCapture(1)

    # Dùng PoseCounter để lấy landmarks
    detector = PoseCounter()
    squat    = SquatExercise()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Lấy landmarks từ frame
        frame, landmarks = detector.process_frame(frame)

        if landmarks:
            count, stage, angle = squat.analyze(landmarks)

            # Hiển thị thông tin lên frame
            cv2.putText(frame, f"Goc: {angle}",
                        (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (255, 255, 255), 2)

            cv2.putText(frame, f"So lan: {count}",
                        (10, 100), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 0), 2)

            cv2.putText(frame, f"Trang thai: {stage}",
                        (10, 150), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 255), 2)

        cv2.imshow("Squat Counter Test", frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()