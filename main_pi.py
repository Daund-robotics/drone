import os
import sys
import subprocess
import time
import threading
import math
import platform

# --- 1. AUTO-INSTALL DEPENDENCIES ---
def install_and_import(package, import_name=None):
    if import_name is None:
        import_name = package
    try:
        __import__(import_name)
    except ImportError:
        print(f"[INFO] Installing {package} for RPi compatibility...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"[INFO] Successfully installed {package}. Restarting script...")
            # Restart script to ensure new env vars are loaded
            os.execv(sys.executable, ['python'] + sys.argv)
        except Exception as e:
            print(f"[ERROR] Failed to install {package}: {e}")
            print("Please run: pip install opencv-python ultralytics")
            sys.exit(1)

# Check for crucial libraries
# 'cv2' comes from 'opencv-python' (or 'opencv-python-headless' on server Pis)
try:
    import cv2
except ImportError:
    install_and_import("opencv-python", "cv2")

try:
    from ultralytics import YOLO
except ImportError:
    install_and_import("ultralytics")

# --- 2. CONFIGURATION ---
# RPi 4 defaults
MODEL_NAME = 'yolov8n.pt'  # Nano is best for RPi 4 CPU
INFERENCE_SIZE = 320      # Lower ref allows faster inference (320 is good balance)
CONF_THRESHOLD = 0.5      # Avoid false positives
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480

# --- 3. CLASSES ---

class CameraStream:
    """
    Dedicated thread for grabbing frames from the camera.
    This prevents I/O blocking in the main loop.
    """
    def __init__(self, src=0):
        if platform.system() == 'Windows':
             self.stream = cv2.VideoCapture(src, cv2.CAP_DSHOW)
        else:
             self.stream = cv2.VideoCapture(src)
             
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)
        self.stream.set(cv2.CAP_PROP_FPS, 30)
        
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        
    def start(self):
        threading.Thread(target=self.update, args=(), daemon=True).start()
        return self

    def update(self):
        while True:
            if self.stopped:
                self.stream.release()
                return
            (grabbed, frame) = self.stream.read()
            if grabbed:
                self.grabbed = grabbed
                self.frame = frame
            else:
                self.stop()
                return

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True

class AlertSystem:
    def __init__(self):
        self.last_alert_time = 0
        self.cooldown = 2.0 # Seconds between alerts

    def trigger(self, frame, text="DRONE DETECTED"):
        current_time = time.time()
        
        # Visual Alert (Always draw)
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 50), (0, 0, 255), -1)
        cv2.putText(frame, text, (50, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Audio Alert (with cooldown)
        if current_time - self.last_alert_time > self.cooldown:
            self.last_alert_time = current_time
            threading.Thread(target=self._beep, daemon=True).start()
        
        return frame

    def _beep(self):
        # Portable beep
        try:
            if platform.system() == "Windows":
                import winsound
                winsound.Beep(1000, 500)
            else:
                # Linux/RPi method 1: Terminal bell
                print('\a') 
                # Linux/RPi method 2: beep command (if installed)
                # os.system('beep -f 1000 -l 500') 
        except:
            pass

# --- 4. MAIN LOGIC ---

def is_overlap(box1, box2):
    # Simple IoU or overlap check
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2
    
    inter_x_min = max(x1_min, x2_min)
    inter_y_min = max(y1_min, y2_min)
    inter_x_max = min(x1_max, x2_max)
    inter_y_max = min(y1_max, y2_max)
    
    if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
        return False
        
    return True

def main():
    print("------------------------------------------------")
    print("   RASPBERRY PI 4 DRONE DETECTION LAUNCHER      ")
    print("------------------------------------------------")
    print("[INIT] initializing camera...")
    
    # 1. Start Camera
    cam = CameraStream(0).start()
    time.sleep(2.0) # Warmup
    
    # 2. Load Model
    print(f"[INIT] Loading YOLO model ({MODEL_NAME})...")
    # This automatically downloads 'yolov8n.pt' if not present
    model = YOLO(MODEL_NAME)
    
    # 3. Setup
    alert_sys = AlertSystem()
    
    # Shared state for threading
    latest_frame = None
    latest_results = []
    lock = threading.Lock()
    running = True

    # Classes config
    SCREEN_CLASSES = [62, 63, 67] # TV, Laptop, Cell phone (COCO IDs)
    TARGET_CLASSES = [4, 14]      # Aeroplane, Bird (COCO IDs)
    # COCO Class reference: https://docs.ultralytics.com/datasets/detect/coco/
    
    # --- INFERENCE THREAD ---
    def inference_loop():
        nonlocal latest_results, running
        while running:
            if latest_frame is None:
                time.sleep(0.01)
                continue
                
            # Copy frame for inference to avoid tearing
            frame_to_process = latest_frame.copy()
            
            # Run YOLO (CPU bound)
            # stream=True is efficient, verbose=False reduces terminal spam
            results = model(frame_to_process, imgsz=INFERENCE_SIZE, conf=CONF_THRESHOLD, verbose=False, iou=0.45)
            
            # Parse results immediately to save main thread work
            parsed_targets = []
            parsed_screens = []
            
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    xyxy = box.xyxy[0].cpu().numpy().astype(int)
                    
                    if cls_id in SCREEN_CLASSES:
                        parsed_screens.append(xyxy)
                    elif cls_id in TARGET_CLASSES:
                        parsed_targets.append({'box': xyxy, 'conf': conf, 'id': cls_id})
            
            with lock:
                latest_results = (parsed_targets, parsed_screens)
            
            # RPi 4 might handle 2-5 FPS inference. 
            # We sleep slightly to give CPU back to video thread if needed, 
            # though YOLO usually maxes out a core.
            time.sleep(0.001)

    # Start Inference Thread
    inf_thread = threading.Thread(target=inference_loop, daemon=True)
    inf_thread.start()

    print("[INFO] System Ready. Press 'q' to exit.")

    # --- MAIN VIDEO LOOP ---
    try:
        p_time = 0
        while True:
            # 1. Get Visual Frame (High FPS)
            frame = cam.read()
            if frame is None: 
                continue
            
            # Update shared state for inference thread
            latest_frame = frame 
            
            # 2. Get Recent Detections (Thread Safe)
            with lock:
                curr_targets, curr_screens = latest_results
                
            # 3. Draw Detections
            # Draw Screens (Blue)
            for box in curr_screens:
                x1, y1, x2, y2 = box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(frame, "SCREEN", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

            # Check logic
            for target in curr_targets:
                t_box = target['box']
                t_conf = target['conf']
                t_id = target['id']
                
                # Check Overlap
                on_screen = False
                for s_box in curr_screens:
                    if is_overlap(t_box, s_box):
                        on_screen = True
                        break
                
                x1, y1, x2, y2 = t_box
                
                if on_screen:
                    # Ignore or mark safe
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2) # Blue
                    cv2.putText(frame, f"Safe {t_conf:.2f}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                else:
                    # REAL DETECTION
                    if t_id == 4: # Aeroplane/Drone
                        color = (0, 0, 255) # Red
                        label = "DRONE"
                        alert_sys.trigger(frame, f"WARNING: {label}")
                    else: # Bird
                        color = (0, 255, 0) # Green
                        label = "BIRD"
                        
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, f"{label} {t_conf:.2f}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

            # 4. FPS Calculation (Video FPS, not Inference FPS)
            c_time = time.time()
            fps = 1 / (c_time - p_time) if c_time > p_time else 0
            p_time = c_time
            cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # 5. Show
            cv2.imshow("RPi Drone Guard", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        pass
    finally:
        running = False
        cam.stop()
        cv2.destroyAllWindows()
        print("[INFO] Exiting...")

if __name__ == "__main__":
    main()
