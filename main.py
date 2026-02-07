
import os
import sys
import subprocess
import time
import math
import threading

# --- AUTO-INSTALL DEPENDENCIES ---
def install(package):
    print(f"[INFO] Installing {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

required_packages = ["opencv-python", "ultralytics", "winsound"] # winsound is windows only, handle gracefully
for package in required_packages:
    try:
        if package == "opencv-python":
            import cv2
        elif package == "ultralytics":
            from ultralytics import YOLO
        elif package == "winsound":
            if os.name == 'nt':
                 import winsound
    except ImportError:
        try:
            if package == "winsound" and os.name != 'nt':
                continue # Skip winsound on RPi
            install(package)
        except Exception as e:
            print(f"[WARN] Failed to install {package}: {e}")

# Re-import after install
import cv2
from ultralytics import YOLO

# Handle Platform Specifics
IS_WINDOWS = os.name == 'nt'
if IS_WINDOWS:
    import winsound

# --- CONFIGURATION (RPi Optimized) ---
MODEL_NAME = 'yolov8n.pt' # Nano model is invalid for RPi, best speed/acc tradeoff
INFERENCE_SIZE = 320     # 320x320 for max FPS. 640 is too slow on RPi 4 CPU.
CONF_THRESHOLD = 0.5     # High confidence to avoid false positives

# --- CAMERA STREAM (Threaded) ---
class CameraStream:
    def __init__(self, src=0):
        # Linux/RPi usually works best with default
        self.stream = cv2.VideoCapture(src)
        if IS_WINDOWS:
            self.stream = cv2.VideoCapture(src, cv2.CAP_DSHOW)
            
        # Set resolution to reasonable default (e.g. 640x480)
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

# --- ALERT SYSTEM (Simplified) ---
class AlertSystem:
    def __init__(self):
        self.alert_active = False

    def trigger_visual_alert(self, img, text="DRONE DETECTED"):
        h, w, _ = img.shape
        cv2.rectangle(img, (0, 0), (w, 50), (0, 0, 255), -1)  # Red banner
        cv2.putText(img, text, (int(w/2) - 150, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return img

    def trigger_audio_alert(self):
        if not self.alert_active:
            self.alert_active = True
            threading.Thread(target=self._play_sound).start()

    def _play_sound(self):
        try:
            if IS_WINDOWS:
                winsound.Beep(1000, 500)
            else:
                # RPi / Linux Sound - requires a beep utility or just print
                print('\a') # Terminal bell
        except Exception as e:
            print(f"[ERROR] Sound error: {e}")
        self.alert_active = False

    def log_alert(self, class_name, confidence):
        print(f"[ALERT] {class_name} detected with confidence {confidence}")

# --- HELPER FUNCTIONS ---
def draw_text_rect(img, text, pos, scale=1, thickness=1, colorT=(255, 255, 255), colorR=(255, 0, 255), offset=10):
    """
    Replica of cvzone.putTextRect using pure cv2
    """
    x, y = pos
    (w, h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, thickness)
    x1, y1, x2, y2 = x - offset, y + offset, x + w + offset, y - h - offset
    
    cv2.rectangle(img, (x1, y1), (x2, y2), colorR, cv2.FILLED)
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, colorT, thickness)
    return x1, y1, x2, y2

def is_overlap(box1, box2):
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2

    inter_x_min = max(x1_min, x2_min)
    inter_y_min = max(y1_min, y2_min)
    inter_x_max = min(x1_max, x2_max)
    inter_y_max = min(y1_max, y2_max)

    if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
        return False

    inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
    box1_area = (x1_max - x1_min) * (y1_max - y1_min)

    if box1_area == 0: return False
    return (inter_area / box1_area) > 0.5

# --- MAIN ---
def main():
    print("[INFO] Starting Drone Detection System (RPi Edition)...")
    
    alert_sys = AlertSystem()
    
    # Auto-download model if missing (Ultralytics handles this, but we ensure it's Nano)
    print(f"[INFO] Loading Model: {MODEL_NAME}...")
    model = YOLO(MODEL_NAME) 

    # Class names for COCO dataset
    classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
                  "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
                  "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
                  "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
                  "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
                  "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
                  "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
                  "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
                  "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
                  "teddy bear", "hair drier", "toothbrush"]

    screenClasses = ["tvmonitor", "laptop", "cell phone"]

    # Initialize Camera
    cap = CameraStream(0).start()
    time.sleep(2.0) # Warmup

    if not cap.stream.isOpened():
        print("Error: Could not open webcam.")
        return

    pTime = 0

    try:
        while True:
            img = cap.read()
            if img is None:
                continue

            # Inference
            results = model(img, stream=True, imgsz=INFERENCE_SIZE, conf=CONF_THRESHOLD)

            screen_boxes = []
            target_detections = [] 

            for r in results:
                boxes = r.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    
                    cls = int(box.cls[0])
                    currentClass = classNames[cls]
                    conf = math.ceil((box.conf[0] * 100)) / 100

                    if currentClass in screenClasses:
                        screen_boxes.append([x1, y1, x2, y2])

                    elif currentClass in ["bird", "aeroplane"]:
                        target_detections.append({
                            "bbox": [x1, y1, x2, y2],
                            "class": currentClass,
                            "conf": conf
                        })

            # Logic
            for target in target_detections:
                t_bbox = target["bbox"]
                t_cls = target["class"]
                t_conf = target["conf"]
                x1, y1, x2, y2 = t_bbox
                
                on_screen = False
                for s_bbox in screen_boxes:
                    if is_overlap(t_bbox, s_bbox):
                        on_screen = True
                        break
                
                if on_screen:
                    color = (255, 0, 0) # Blue
                    label = f"ON SCREEN ({t_cls})"
                    draw_text_rect(img, f'{label} {t_conf}', (max(0, x1), max(35, y1)), scale=1, thickness=1, colorR=color)
                    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                
                else:
                    if t_cls == "bird" and t_conf > 0.70: 
                        color = (0, 255, 0) # Green
                        draw_text_rect(img, f'{t_cls} {t_conf}', (max(0, x1), max(35, y1)), scale=1, thickness=1, colorR=color)
                        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                    
                    elif t_cls == "aeroplane" and t_conf > 0.5:
                        color = (0, 0, 255) # Red
                        alert_sys.log_alert("Drone", t_conf)
                        alert_sys.trigger_audio_alert()
                        img = alert_sys.trigger_visual_alert(img, "WARNING: DRONE DETECTED")

                        draw_text_rect(img, f'DRONE! {t_conf}', (max(0, x1), max(35, y1)), scale=1, thickness=1, colorR=color)
                        cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)

            # FPS
            cTime = time.time()
            fps = 0
            if (cTime - pTime) > 0:
                fps = 1 / (cTime - pTime)
            pTime = cTime
            cv2.putText(img, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

            cv2.imshow("Drone Detection (RPi)", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cap.stop()
                break
    except KeyboardInterrupt:
        pass
        
    cap.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
