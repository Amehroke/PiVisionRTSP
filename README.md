# PiVisionRTSP

**PiVisionRTSP** is a lightweight, real-time computer vision pipeline for Raspberry Pi 5 using RTSP streams. It supports object detection via YOLOv8, optimized frame handling, and optional cloud alerting.

---

## 📡 Overview

This project enables real-time video streaming and object detection from IP cameras connected to a Network Video Recorder (NVR) using RTSP. It supports:

* YOLOv8-based object detection
* RTSP decoding via FFmpeg
* Frame skipping and multithreading for performance
* Optional AWS Lambda & SNS integration

---

## 🔌 Step 1: Ensure Network Connectivity

1. **Check Raspberry Pi IP Address**

   ```bash
   hostname -I
   ```

2. **Ensure NVR Is on the Same Subnet**
   Confirm both devices are on the same subnet (e.g., `192.xxx.x.xxx`).

3. **Assign a Static IP to the Raspberry Pi**
   Prevent IP changes due to reboots or outages.

4. **Open Required Ports**
   Manually open port `554` on the NVR and Raspberry Pi for RTSP communication.

---

## 🔍 Step 2: Discover Camera IPs on Network

1. **Install Nmap**

   ```bash
   sudo apt-get install nmap
   ```

2. **Get Your Network Range**

   ```bash
   hostname -I  # Example: 192.xxx.x.xxx
   ```

3. **Scan for Devices**

   ```bash
   sudo nmap -sn 192.xxx.x.0/24
   ```

> If camera IPs don’t appear, your NVR may proxy all streams through a single IP.

---

## 🌐 Step 3: Confirm Network Communication

1. **Ping the NVR from the Raspberry Pi**

   ```bash
   ping 192.xxx.x.xxx
   ```

2. **Ensure Both Devices Share the Same Subnet**
   Example: `192.168.1.xxx` on both NVR and Raspberry Pi.

---

## 🎥 Step 4: Test RTSP Streams

1. **Install FFmpeg & FFplay**

   ```bash
   sudo apt-get install ffmpeg ffplay
   ```

2. **Save a 10-Second Clip**

   ```bash
   ffmpeg -rtsp_transport tcp -i "rtsp://username:password@192.xxx.x.xxx:554/Streaming/Channels/101" -t 10 -f mp4 test.mp4
   ```

3. **Live Stream a Channel**

   ```bash
   ffplay -rtsp_transport tcp -i "rtsp://username:password@192.xxx.x.xxx:554/Streaming/Channels/101"
   ```

---

## 🚀 Step 5: Real-Time YOLOv8 Inference on RTSP

### Install Dependencies

```bash
pip install torch torchvision ultralytics opencv-python ffmpeg-python
```

### Inference Script

```python
import cv2
from ultralytics import YOLO
from tkinter import simpledialog, Tk

# Prompt user for object classes
root = Tk()
root.withdraw()
object_selection = simpledialog.askstring(
    "Select Objects", "Enter objects to detect (e.g., person,car,dog):"
)
selected_objects = [obj.strip().lower() for obj in object_selection.split(",")]

# Load YOLO model and RTSP stream
model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture("rtsp://username:password@192.xxx.x.xxx:554/Streaming/Channels/101", cv2.CAP_FFMPEG)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)
    for result in results:
        for box in result.boxes.xyxy:
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    cv2.imshow("YOLO RTSP Stream", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
```

---

## ⚙️ RTSP Inference Optimization Tips

### 🧠 Problem

High-resolution RTSP streams with YOLO can cause lag:

* Buffer buildup
* Multi-second delays
* Choppy output

### ✅ Solutions

1. **Skip Frames (Simplest)**

   * If YOLO runs at 10 FPS but stream is 30 FPS, skip 2 of every 3 frames.

2. **Two-Thread Approach with Dropping Queue**

   * Thread A captures frames and overwrites a shared variable.
   * Thread B performs inference only on the latest available frame.

3. **Reduce Resolution or Use Hardware Acceleration**

   * Use sub-streams (e.g., 640x480) or inference accelerators.

---

## ✅ Benefits

* 💡 Real-time object detection on edge devices
* 📉 Lower compute usage with class filtering
* ⚡️ Smooth RTSP decoding with FFmpeg backend
* ☁️ Optional integration with cloud notifications (AWS SNS)
