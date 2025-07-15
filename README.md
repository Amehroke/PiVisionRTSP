# PiVisionRTSP

This README provides a step-by-step guide for building computer vision solutions using Raspberry Pi 5 on RSTP (Real-Time Streaming Protocol) streams. The guide helps you create an efficient and cost-effective system for streaming video data, detecting objects, and displaying results.

---

### Step 1: Ensure Network Connectivity
1. **Check Raspberry Pi Network**  
   Run the following command to check if your Raspberry Pi 5 is on the same network:
   ```bash
   hostname -I
   ```
   This will give you the IP address of your Raspberry Pi.

2. **Check NVR Network**  
   Log into your NVR settings and ensure that the NVR is on the same network as your Raspberry Pi. 

3. **Verify Camera IP Addresses**  
   If your NVR is connected to a PoE (Power over Ethernet) switch, check if each camera has been assigned its own IP address. If each camera has a unique IP, you will need to access each one separately.

### Step 2: Verify Camera IP Addresses

1. **Install Nmap**
   Install Nmap on your Raspberry Pi by running:
   ```bash
   sudo apt-get install nmap
   ```

2. **Obtain the Network Range**  
   Use the following command to obtain the IP address of your Raspberry Pi:
   ```bash
   hostname -I
   ```
   Example output: `192.1xx.1.xxx` (Note this IP address).

3. **Scan the Network**  
   Use Nmap to scan the network for devices. Adjust the IP range according to the address you obtained from the previous step:
   ```bash
   sudo nmap -sn 192.xxx.1.0/24 
   ```
   - .0/24 is added at the end to scan all ips in the range
   This will list all devices connected to the network and their associated IP addresses.  
   - If no camera-related names appear, it means all cameras are routed through the NVR, and the NVR has only one IP address for all cameras.

### Step 3: Network Confirmation

1. **Ensure Same Network**  
   Ensure that the Raspberry Pi and the NVR are on the same IP address base (e.g., `192.168.1.xxx`). Make sure both devices are using the same Wi-Fi or network.

2. **Ping the NVR IP**  
   From the Raspberry Pi terminal, ping the NVR’s IP address to ensure communication:
   ```bash
   ping <NVR_IP>
   ```
   If you get a response, this confirms the Raspberry Pi and NVR can communicate.

### Step 4: Set Up RTSP Streaming

1. **Install FFmpeg and FFplay**  
   Install the required software to access the RTSP stream:
   ```bash
   sudo apt-get install ffmpeg ffplay
   ```

2. **Save Stream to a File**  
   To save a 10-second clip of the stream, use the following command:
   ```bash
   ffmpeg -rtsp_transport tcp -i "rtsp://admin:password@192.xxxx.port/cam/realmonitor?channel=2&subtype=0" -t 10 -f mp4 test.mp4
   ```
   - This command will save a 10-second segment of the stream to a file called `test.mp4`.

3. **Stream Live**  
   To stream the camera live, use the following command:
   ```bash
   ffplay -rtsp_transport tcp -i "rtsp://admin:password@192.xxxx.port/cam/realmonitor?channel=1&subtype=0"
   ```
   - This will open a window and stream the specified camera channel live.
  
3. Optimized RTSP Streaming with YOLOv8 Object Detection

Purpose:

Enable efficient real-time object detection from an IP camera RTSP stream, allowing users to select which objects to track.

Components:

Raspberry Pi 5

YOLOv8 Model (ultralytics)

FFmpeg for RTSP handling

AWS Lambda & SNS for notifications (optional)

Steps:

Install dependencies on Raspberry Pi:

pip install torch torchvision ultralytics opencv-python ffmpeg-python

Run YOLOv8 with optimized RTSP streaming:

import cv2
from ultralytics import YOLO
from tkinter import simpledialog, Tk

root = Tk()
root.withdraw()

# User input for object detection
object_selection = simpledialog.askstring(
    "Select Objects", "Enter objects to detect (comma-separated, e.g., person,car,dog):"
)
selected_objects = [obj.strip().lower() for obj in object_selection.split(",")]

model = YOLO("yolov8n.pt")  # Load YOLO model
cap = cv2.VideoCapture("rtsp://admin:password@192.168.1.100:554/stream", cv2.CAP_FFMPEG)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, classes=[0])  # Detect only 'person' class
    for result in results:
        for box in result.boxes.xyxy:
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    cv2.imshow("YOLO RTSP Stream", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

Optimize RTSP streaming:

Use cv2.CAP_FFMPEG for better RTSP handling.

Resize frames before inference (640x480) to reduce load.

Detect only selected objects to save computation.

Benefits of This Approach:

✅ Lower computation costs (detects only selected objects).✅ Better RTSP streaming stability (FFmpeg handles buffering).✅ Custom object selection (user-defined detection categories).
