from arduino.app_utils import App, Bridge
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
import time
import threading

# Détecteur vidéo
video_detector = VideoObjectDetection(confidence=0.4, debounce_sec=1.5)

# Bridge vers le STM32
bridge = Bridge()

LED_ON = False
LAST_DETECTION = 0.0
LOCK = threading.Lock()

# --- Callback quand une personne est détectée ---
def on_person_detected():
    global LED_ON, LAST_DETECTION
    now = time.time()
    with LOCK:
        LAST_DETECTION = now
        print("🚨 Person detected in the video stream!")
        if not LED_ON:
            try:
                bridge.call("setLedState", True)
                LED_ON = True
                print("LED ON")
            except Exception as e:
                print("Bridge error:", e)

video_detector.on_detect("person", on_person_detected)

# --- Callback pour toutes les détections (comme ton exemple) ---
def on_all_detections(detections: dict):
    print("All detections:", detections)

video_detector.on_detect_all(on_all_detections)

# --- Thread qui éteint la LED 10 s après la DERNIÈRE détection ---
def led_watcher():
    global LED_ON, LAST_DETECTION
    while True:
        time.sleep(0.5)
        with LOCK:
            if LED_ON and (time.time() - LAST_DETECTION > 10.0):
                try:
                    bridge.call("setLedState", False)
                    LED_ON = False
                    print("LED OFF (10 s sans personne)")
                except Exception as e:
                    print("Bridge error:", e)

threading.Thread(target=led_watcher, daemon=True).start()

# --- Lancement ---
App.run()

