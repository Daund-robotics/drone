import cv2
import threading
import time
import numpy as np
import platform

# Check if running on RPi to import picamzero
try:
    from picamzero import Camera
    HAS_PICAMZERO = True
except ImportError:
    HAS_PICAMZERO = False
    print("[WARN] 'picamzero' not found. Will try standard OpenCV VideoCapture (Webcam mode).")

class CameraStream:
    def __init__(self, src=0):
        self.stopped = False
        self.frame = None
        self.grabbed = False
        self.cam = None
        self.stream = None
        self.use_picam = False

        if HAS_PICAMZERO and platform.system() != 'Windows':
            try:
                print("[INIT] Initializing Picamzero...")
                self.cam = Camera()
                self.cam.start_preview() # Optional: might show HDMI preview
                self.use_picam = True
                print("[INIT] Picamzero started successfully.")
            except Exception as e:
                print(f"[ERROR] Picamzero init failed: {e}. Falling back to OpenCV.")
                self.use_picam = False

        if not self.use_picam:
            # Fallback for Windows or standard USB webcams
            if platform.system() == 'Windows':
                self.stream = cv2.VideoCapture(src, cv2.CAP_DSHOW)
            else:
                self.stream = cv2.VideoCapture(src)
            
            self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            (self.grabbed, self.frame) = self.stream.read()

    def start(self):
        threading.Thread(target=self.update, args=(), daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            if self.use_picam:
                # PICAMZERO MODE
                try:
                    # Capture frame as numpy array (RGB)
                    # Note: picamzero capture_array usually returns RGB. 
                    # OpenCV needs BGR.
                    image = self.cam.capture_array()
                    if image is not None:
                        # Convert RGB to BGR for OpenCV
                        self.frame = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                        self.grabbed = True
                    else:
                        time.sleep(0.01)
                except Exception as e:
                    print(f"[ERROR] Picam capture error: {e}")
                    time.sleep(0.1)
            else:
                # OPENCV/WEBCAM MODE
                if self.stream is None or not self.stream.isOpened():
                    self.stop()
                    continue
                
                (grabbed, frame) = self.stream.read()
                if grabbed:
                    self.grabbed = grabbed
                    self.frame = frame
                else:
                    self.stop()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        if self.use_picam and self.cam:
            try:
                self.cam.stop_preview()
                self.cam.close()
            except:
                pass
        if self.stream:
            self.stream.release()

