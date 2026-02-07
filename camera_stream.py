import cv2
import threading
import time
import platform

class CameraStream:
    def __init__(self, src=0):
        # Check OS to determine backend
        if platform.system() == 'Windows':
            self.stream = cv2.VideoCapture(src, cv2.CAP_DSHOW)
        else:
            # Linux/RPi usually works best with default or V4L2
            self.stream = cv2.VideoCapture(src)
        
        # Set resolution to reasonable default (e.g. 640x480) to avoid RPi overloading on init
        # We process at 320 anyway.
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        threading.Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while True:
            if self.stopped:
                self.stream.release()
                return

            (grabbed, frame) = self.stream.read()
            if not grabbed:
                self.stop()
                return
            
            self.grabbed = grabbed
            self.frame = frame

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
