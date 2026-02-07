import cv2
import winsound
import threading

class AlertSystem:
    def __init__(self):
        self.alert_active = False

    def trigger_visual_alert(self, img, text="DRONE DETECTED"):
        """Draws a visual alert on the image."""
        h, w, _ = img.shape
        cv2.rectangle(img, (0, 0), (w, 50), (0, 0, 255), -1)  # Red banner
        cv2.putText(img, text, (int(w/2) - 150, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return img

    def trigger_audio_alert(self):
        """Plays a beep sound in a separate thread to avoid blocking."""
        if not self.alert_active:
            self.alert_active = True
            threading.Thread(target=self._play_sound).start()

    def _play_sound(self):
        # Frequency 1000Hz, Duration 500ms
        try:
            winsound.Beep(1000, 500)
        except AttributeError:
            print("[ERROR] winsound.Beep not found")
        except RuntimeError:
             print("[ERROR] Failed to play sound")
        self.alert_active = False

    def log_alert(self, class_name, confidence):
        """Logs the alert to console (could be extended to file/db)."""
        print(f"[ALERT] {class_name} detected with confidence {confidence}")
