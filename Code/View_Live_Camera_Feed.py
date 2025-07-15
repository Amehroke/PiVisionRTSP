import subprocess
import cv2
import tkinter as tk
import numpy as np 
from tkinter import simpledialog
from Ip_Scan import run_ip_scan

local_ip = run_ip_scan()

# Function to stream video using ffmpeg and display it using OpenCV
def stream_video(rtsp_url):
    # ffmpeg command to get the video stream as raw video frames
    command = [
        'ffmpeg',
        '-rtsp_transport', 'tcp',  # Use TCP for more reliable stream
        '-i', rtsp_url,             # Input RTSP URL
        '-f', 'rawvideo',           # Output raw video format
        '-pix_fmt', 'bgr24',        # Pixel format for OpenCV compatibility
        '-an',                      # Disable audio stream
        '-'                         # Output to stdout (pipe)
    ]
    
    # Run the ffmpeg process
    process = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=10**8)
    
    while True:
        # Read raw frame from ffmpeg
        raw_frame = process.stdout.read(3 * 1920 * 1080)  # Read raw video data as bytes
        
        if not raw_frame:
            print("Error: No more frames.")
            break
        
        # Convert raw byte data to numpy array (frame)
        frame = np.frombuffer(raw_frame, np.uint8).reshape((1080, 1920, 3))  # Assuming 1920x1080 resolution

        # Show the frame in OpenCV window
        cv2.imshow("Live Stream", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
            break
    
    process.stdout.close()
    process.wait()
    cv2.destroyAllWindows()

# Function to get user input for NVR login and start streaming
def start_streaming():
    # Ask user for NVR username and password
    username = simpledialog.askstring("Input", "Enter your NVR username:")
    password = simpledialog.askstring("Input", "Enter your NVR password:", show='*')
    channel = simpledialog.askinteger("Input", "Enter Camera Channel:")

    # Construct RTSP URL for the camera
    rtsp_url = f"rtsp://{username}:{password}@{local_ip[0]}:554/cam/realmonitor?channel={channel}&subtype=0"

    # rtsp_url = f"rtsp://admin:Asingh8101@192.168.1.138:554/cam/realmonitor?channel=3&subtype=0"
    
    # Stream video
    stream_video(rtsp_url)

# Create the main window
root = tk.Tk()
root.withdraw()  # Hide the root window as we only need the input dialog

# Start the streaming process
start_streaming()
