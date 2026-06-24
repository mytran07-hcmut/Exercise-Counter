function updateUI(result) {
    // Cập nhật hình ảnh camera đã có landmarks
    if (result.frame) {
        document.getElementById("videoFeed").src = result.frame;
    }

    // Cập nhật thông số
    document.getElementById("counter").textContent = result.count;
    document.getElementById("angle").textContent   = result.angle + "°";

    if (result.stage) {
        document.getElementById("stage").textContent =
            result.stage === "down" ? "⬇ Xuống" : "⬆ Lên";
    }

    // Ẩn/hiện thông báo "Không phát hiện người"
    document.getElementById("noDetection").style.display =
        result.detected ? "none" : "block";
}


async function resetCounter() {
    await fetch("http://127.0.0.1:5000/reset", { method: "POST" });
    document.getElementById("counter").textContent = "0";
    document.getElementById("stage").textContent   = "-";
    document.getElementById("angle").textContent   = "0°";
}