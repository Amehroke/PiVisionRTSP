# Optimized Person Detection with YOLO - Enhanced for IP Camera Streams

import subprocess
import cv2
import torch
import numpy as np
from ultralytics import YOLO
import tkinter as tk
from tkinter import simpledialog
from Ip_Scan import run_ip_scan
import time
import threading
from collections import deque

# Configuration for person detection
PERSON_CLASS_ID = 0  # COCO person class
CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence for person detection
NMS_THRESHOLD = 0.4  # Non-maximum suppression threshold
SKIP_FRAMES = 3  # Process every 3rd frame for better performance
MIN_PERSON_SIZE = 50  # Minimum bounding box area for person detection



def get_camera_credentials():
    """Get camera credentials with better error handling"""
    try:
        local_ip = run_ip_scan()
        if not local_ip:
            print("Error: No IP addresses found")
            return None, None, None, None
            
        # Initialize Tkinter root window (hidden)
        root = tk.Tk()
        root.withdraw()
        
        username = simpledialog.askstring("Input", "Enter your NVR username:")
        if not username:
            root.destroy()
            return None, None, None, None
            
        password = simpledialog.askstring("Input", "Enter your NVR password:", show='*')
        if not password:
            root.destroy()
            return None, None, None, None
            
        channel = simpledialog.askinteger("Input", "Enter Camera Channel:")
        if channel is None:
            root.destroy()
            return None, None, None, None
            
        root.destroy()
        return username, password, channel, local_ip[0]
        
    except Exception as e:
        print(f"Error getting credentials: {e}")
        return None, None, None, None

def setup_yolo_model():
    """Setup YOLO model with person detection optimizations"""
    try:
        MODEL_PATH = "Model_Weights/yolo11n.pt"
        model = YOLO(MODEL_PATH)
        
        # Set model parameters for person detection
        model.conf = CONFIDENCE_THRESHOLD
        model.iou = NMS_THRESHOLD
        model.classes = [PERSON_CLASS_ID]  # Only detect persons
        
        print(f"Model loaded successfully: {MODEL_PATH}")
        print(f"Confidence threshold: {CONFIDENCE_THRESHOLD}")
        print(f"Person detection only: Enabled")
        return model
        
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def setup_ffmpeg_stream(rtsp_url, width=1280, height=720):
    """Setup optimized FFmpeg stream for person detection"""
    frame_size = width * height * 3
    
    command = [
        "ffmpeg",
        "-rtsp_transport", "tcp",
        "-i", rtsp_url,
        "-fflags", "nobuffer",
        "-flags", "low_delay",
        "-strict", "experimental",
        "-vf", f"scale={width}:{height},format=bgr24",
        "-f", "rawvideo",
        "-pix_fmt", "bgr24",
        "-an",
        "-"
    ]
    
    try:
        process = subprocess.Popen(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.DEVNULL, 
            bufsize=10**8
        )
        return process, frame_size
    except Exception as e:
        print(f"Error setting up FFmpeg stream: {e}")
        return None, None


def process_person_detections(frame, results):
    """Process and visualize person detections with enhanced filtering"""
    person_detections = []
    
    for result in results:
        if result.boxes is not None:
            for box in result.boxes:
                # Get detection info
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                
                # Only process person detections
                if cls_id == PERSON_CLASS_ID and conf >= CONFIDENCE_THRESHOLD:
                    # Filter by minimum size
                    area = (x2 - x1) * (y2 - y1)
                    if area >= MIN_PERSON_SIZE:
                        person_detections.append((x1, y1, x2, y2, conf))
    
    # Draw detections with enhanced visualization
    for x1, y1, x2, y2, conf in person_detections:
        # Color based on confidence (green to red)
        color = (0, int(255 * conf), int(255 * (1 - conf)))
        
        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Draw confidence label with background
        label = f"Person {conf:.2f}"
        (label_width, label_height), _ = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
        )
        
        # Background rectangle for text
        cv2.rectangle(frame, 
                     (x1, y1 - label_height - 10), 
                     (x1 + label_width, y1), 
                     color, -1)
        
        # Text
        cv2.putText(frame, label, (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

def main():
    """Main person detection loop with optimizations"""
    
    # Get camera credentials
    credentials = get_camera_credentials()
    if not all(credentials):
        print("Failed to get camera credentials")
        return
    
    username, password, channel, ip = credentials
    rtsp_url = f"rtsp://{username}:{password}@{ip}:554/cam/realmonitor?channel={channel}&subtype=0"
    
    # Setup model
    model = setup_yolo_model()
    if model is None:
        return
    
    # Setup stream
    process, frame_size = setup_ffmpeg_stream(rtsp_url)
    if process is None:
        return
    
    print("Starting person detection stream...")
    print("Press 'q' to quit")
    
    frame_count = 0
    
    try:
        while True:
            raw_frame = process.stdout.read(frame_size)
            if not raw_frame:
                print("Stream ended or error reading frame.")
                break
            
            frame = np.frombuffer(raw_frame, np.uint8).reshape((720, 1280, 3)).copy()
            frame_count += 1
            
            # Frame skipping logic
            if frame_count % SKIP_FRAMES != 0:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue
            
            # Person detection
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = model(rgb, verbose=False)  # Disable verbose for performance
            
            # Process detections
            process_person_detections(frame, results)
            
            # Display frame
            cv2.imshow("Person Detection - YOLOv8", frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error in main loop: {e}")
    finally:
        # Cleanup
        process.stdout.close()
        process.wait()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
