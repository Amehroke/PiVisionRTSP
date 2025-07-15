# This code uses a thread to read the frames from the camera and a queue to store the frames.
# It then runs the YOLO inference on the latest frame in the queue.
# It then displays the frame with the bounding boxes drawn on it.


import subprocess
import cv2
import numpy as np
from ultralytics import YOLO  # YOLOv8 model
import threading
import queue
from tkinter import simpledialog
from Ip_Scan import run_ip_scan

def ffmpeg_reader(ffmpeg_cmd, frame_queue, frame_size, width, height):
    """
    Continuously read raw frames from FFmpeg's stdout and push into a queue.
    If the queue is full, drop the old frame to ensure near real-time.
    """
    process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10**8)
    
    while True:
        raw_frame = process.stdout.read(frame_size)
        if not raw_frame:
            print("[READER] Stream ended or error reading frame.")
            break

        # Convert raw bytes to a writable NumPy array
        frame = np.frombuffer(raw_frame, np.uint8).reshape((height, width, 3)).copy()
        
        # If queue is full, remove the old frame
        if frame_queue.full():
            try:
                frame_queue.get_nowait()  # discard old frame
            except queue.Empty:
                pass
        
        frame_queue.put(frame)

    # Cleanup
    process.stdout.close()
    process.wait()


# ---------------------- MAIN CODE ---------------------- #

# 1. Get user input
# local_ip = run_ip_scan()

# username = simpledialog.askstring("Input", "Enter your NVR username:")
# password = simpledialog.askstring("Input", "Enter your NVR password:", show='*')
# channel = simpledialog.askinteger("Input", "Enter Camera Channel:")

# 2. Load YOLO model
MODEL_PATH = "Model_Weights/yolov8n.pt"
model = YOLO(MODEL_PATH)

# 3. Construct RTSP URL
# rtsp_url = f"rtsp://{username}:{password}@{local_ip[0]}:554/cam/realmonitor?channel={channel}&subtype=0"
rtsp_url = f"rtsp://admin:Asingh8101@192.168.1.138:554/cam/realmonitor?channel=3&subtype=0"

# 4. Desired resolution (scales from camera’s main stream)
width, height = 1280, 720
frame_size = width * height * 3

# 5. FFmpeg command to read & decode frames in bgr24 at 1280×720
command = [
    "ffmpeg",
    "-rtsp_transport", "tcp",         # or "udp" if your network is stable
    "-i", rtsp_url,
    "-fflags", "nobuffer",
    "-flags", "low_delay",
    "-strict", "experimental",
    "-vf", "scale=1280:720,format=bgr24",
    "-f", "rawvideo",
    "-pix_fmt", "bgr24",
    "-an",
    "-",
]

# 6. Create a queue of size=1 to store frames
frame_queue = queue.Queue(maxsize=1)

# 7. Start the reading thread
reader_thread = threading.Thread(
    target=ffmpeg_reader,
    args=(command, frame_queue, frame_size, width, height),
    daemon=True  # daemon=True so it closes if main thread exits
)
reader_thread.start()

# 8. Main loop: get the latest frame from the queue, run YOLO, display
try:
    while True:
        # Block until a frame is available
        frame = frame_queue.get()

        # YOLO inference
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = model(rgb)

        # Draw boxes
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                label = f"{model.names[cls_id]} {conf:.2f}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
                cv2.putText(frame, label, (x1, y1-5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
        
        cv2.imshow("YOLOv8n - Threaded", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cv2.destroyAllWindows()
