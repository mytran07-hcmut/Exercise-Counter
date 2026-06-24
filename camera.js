let videoStream = null;
let isRunning = false;
let animationId = null;

// Tạo video element ẩn để lấy stream từ webcam
const hiddenVideo = document.createElement("video");
hiddenVideo.autoplay = true;
hiddenVideo.playsInline = true;

// Canvas ẩn để chụp frame từ video
const canvas = document.createElement("canvas");
const ctx = canvas.getContext("2d");


async function startCamera() {
    try {
        // Xin quyền truy cập camera
        videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
        hiddenVideo.srcObject = videoStream;

        // Chờ video sẵn sàng rồi bắt đầu gửi frame
        hiddenVideo.onloadedmetadata = () => {
            canvas.width  = hiddenVideo.videoWidth;
            canvas.height = hiddenVideo.videoHeight;
            isRunning = true;
            document.getElementById("videoFeed").style.display = "block";
            document.getElementById("startBtn").textContent = "⏹ Dừng";
            document.getElementById("startBtn").onclick = stopCamera;
            sendFrame();
        };

    } catch (err) {
        alert("Không thể truy cập camera: " + err.message);
    }
}


function stopCamera() {
    isRunning = false;
    if (animationId) cancelAnimationFrame(animationId);
    if (videoStream) videoStream.getTracks().forEach(t => t.stop());
    document.getElementById("videoFeed").style.display = "none";
    document.getElementById("startBtn").textContent = "▶ Bắt đầu";
    document.getElementById("startBtn").onclick = startCamera;
}


async function sendFrame() {
    if (!isRunning) return;

    // Chụp frame hiện tại từ video vào canvas
    ctx.drawImage(hiddenVideo, 0, 0, canvas.width, canvas.height);

    // Chuyển canvas thành base64 JPEG
    const frameData = canvas.toDataURL("image/jpeg", 0.8);

    try {
        // Gửi frame lên Flask server
        const response = await fetch("http://127.0.0.1:5000/process_frame", {
            method : "POST",
            headers: { "Content-Type": "application/json" },
            body   : JSON.stringify({ frame: frameData })
        });

        const result = await response.json();

        // Cập nhật hình ảnh và thông số lên giao diện
        updateUI(result);

    } catch (err) {
        console.error("Lỗi kết nối server:", err);
    }

    // Gửi frame tiếp theo
    animationId = requestAnimationFrame(sendFrame);
}