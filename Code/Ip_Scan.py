import os
import getpass
import subprocess
import re

def get_local_ip():
    """Get the local IP address dynamically on macOS & Linux."""
    try:
        if os.uname().sysname == "Darwin":  # macOS
            local_ip = subprocess.getoutput("ipconfig getifaddr en0").strip()
        else:  # Linux
            local_ip = subprocess.getoutput("hostname -I").split()[0]

        if not local_ip:
            raise ValueError("Could not determine local IP.")
        return local_ip

    except Exception as e:
        print(f"[ERROR] Could not determine local IP: {e}")
        return None

def find_camera_ips(network_range):
    """Scans the network and identifies devices running RTSP (port 554)."""
    print("[INFO] Scanning network for cameras...")

    try:
        # Scan for all active devices
        scan_result = subprocess.check_output(f"nmap -sn {network_range}", shell=True, text=True)
        device_ips = re.findall(r'Nmap scan report for (\d+\.\d+\.\d+\.\d+)', scan_result)

        camera_ips = []

        for ip in device_ips:
            print(f"[INFO] Checking {ip} for RTSP service...")
            port_scan = subprocess.getoutput(f"nmap -p 554 {ip}")
            
            # Check if port 554 is open
            if "554/tcp open" in port_scan:
                camera_ips.append(ip)
                print(f"[INFO] Camera detected at {ip}")

        if camera_ips:
            print(f"[INFO] Cameras found: {camera_ips}")
        else:
            print("[ERROR] No cameras found.")

        return camera_ips

    except subprocess.CalledProcessError:
        print("[ERROR] Failed to scan the network. Check if nmap is installed.")
        return []

def run_ip_scan():
    print("=== NVR Camera Live Streamer ===")
    # Detect local IP and set network range
    local_ip = get_local_ip()
    if not local_ip:
        print("[ERROR] Could not determine local IP. Exiting.")
        return

    network_base = ".".join(local_ip.split(".")[:-1]) + ".0/24"
    print(f"[INFO] Scanning network range: {network_base}")

    # Scan network for cameras
    camera_ips = find_camera_ips(network_base)
    if not camera_ips:
        print("[ERROR] No cameras found on the network.")
        return

    print(f"[INFO] Found cameras: {camera_ips}")
    return camera_ips

if __name__ == "__main__":
    run_ip_scan()
