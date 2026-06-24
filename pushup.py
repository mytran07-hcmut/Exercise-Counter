import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from pose_detector import calculate_angle, PoseCounter


class PushupExercise:
    def __init__(self):
        """
        Khởi tạo bài tập Push-up với ngưỡng góc chuẩn.
        """
        self.counter = PoseCounter()

        # Ngưỡng góc cho Push-up
        self.DOWN_THRESHOLD = 70    # Góc < 70° → tư thế "xuống" hợp lệ
        self.UP_THRESHOLD   = 160   # Góc > 160° → tư thế "lên" hợp lệ

        self.current_angle  = 0

    def analyze(self, landmarks):
        """
        Phân tích landmarks, tính góc khuỷu tay và cập nhật bộ đếm.

        Tham số:
            landmarks: dictionary tọa độ các khớp từ process_frame()

        Trả về:
            count : số lần push-up hoàn thành
            stage : trạng thái hiện tại ("up" / "down")
            angle : góc khuỷu tay hiện tại
        """

        # Lấy tọa độ 3 điểm: Vai - Khuỷu tay - Cổ tay (bên trái)
        shoulder = landmarks["left_shoulder"]
        elbow    = landmarks["left_elbow"]
        wrist    = landmarks["left_wrist"]

        # Tính góc tại khuỷu tay
        self.current_angle = calculate_angle(shoulder, elbow, wrist)

        # Cập nhật state machine và bộ đếm
        count, stage = self.counter.count(
            self.current_angle,
            down_threshold=self.DOWN_THRESHOLD,
            up_threshold=self.UP_THRESHOLD
        )

        return count, stage, self.current_angle

    def reset(self):
        """Reset bài tập về trạng thái ban đầu."""
        self.counter.reset()
        self.current_angle = 0