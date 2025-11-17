# 🧠 Explication du code Python (UNO Q — Détection vidéo + LED)  
Ce document explique chaque ligne du code Python utilisé dans l’application.  
Ce code tourne sur le cœur Linux de la UNO Q et communique avec le cœur STM32 grâce au module Bridge.  

## 🟦 1. Import des modules
```python
from arduino.app_utils import Bridge, App

```
- **Bridge** : permet de communiquer avec le cœur STM32 (sketch .ino) via bridge.call().
- **App** : lance l'application App Lab (boucle interne, services, gestion du runner vidéo, etc.).

```python
from arduino.app_bricks.video_objectdetection import VideoObjectDetection

```
- Importe la brique VideoObjectDetection.
- Analyse en temps réel le flux de la webcam USB.
- Fournit des callbacks lorsqu’un objet est détecté (ex : person, dog, car…).

```python
import threading
import time

```
- threading : lance un thread séparé pour surveiller l’état de la LED.
- time : mesure le temps (time.time()) et fait des pauses (time.sleep()).
  
---

 ## 🟦 2. Initialisation des objets principaux

```python
bridge = Bridge()

```
- Initialise la communication Linux → STM32.  
- Permet d’appeler la fonction C++ fournie par le sketch via :

```python
bridge.call("setLedState", True)
```

```python
detector = VideoObjectDetection(confidence=0.4, debounce_sec=1.0)

```
Crée l’instance de détection vidéo :
- confidence=0.4 : seuil minimum (40%) pour valider une détection.
- debounce_sec=1.0 : délai minimum entre deux détections du même type pour éviter les spams.

---

## 🟦 3. Variables globales pour la logique interne

```python
last_detection_time = 0
```
- Stocke le moment où une personne a été vue pour la dernière fois.
- Sert à éteindre la LED après 10 secondes sans détection.

---

## 🟦 4. On force la LED à OFF au lancement

```python
bridge.call("setLedState", False)

```
- Envoie une commande au STM32 pour éteindre la LED au démarrage.
- Assure un état initial propre.

---

## 🟦 5. Callback de détection de personne

```python
def on_person_detected():
    global last_detection_time

```
Fonction appelée automatiquement quand une personne est détectée.

```python
    last_detection_time = time.time()

```
- Met à jour le temps de dernière détection.

```python
    print("🚨 Person detected in the video stream!")
```
- Affichage dans la console Python (utile pour debug).

```python
    bridge.call("setLedState", True)

```
- Allume la LED côté STM32.
- Grâce au sketch .ino, True = LED ON.

```python
    print("LED ON")

```
- Confirme l’allumage dans la console.
  
---

## 🟦 6. Enregistrement du callback pour "person"

```python
detector.on_detect("person", on_person_detected)

```
Informe l'API vidéo :
> « Quand tu vois une personne, appelle on_person_detected() »

--- 

## 🟦 7. Callback générique pour loguer toutes les détections

```python
def on_all_detections(detections: dict):
    print("All detections:", detections)

```
Le paramètre detections contient par exemple :
```python
{
  "person": {"confidence": 0.86, "bounding_box_xyxy": (x1, y1, x2, y2)},
  "mouse":  {"confidence": 0.66, ...}
}

```
---

## 🟦 8. Thread de surveillance de la LED
```python
def led_watcher():
    global last_detection_time
```
Thread séparé dont le rôle est :
- surveiller le temps depuis la dernière détection,
- **éteindre la LED après 10 secondes sans personne.**

```python
    while True:
```
Boucle infinie tant que l'application tourne.  

```python
        now = time.time()
```
- Récupère l’heure actuelle.

```python
        if now - last_detection_time > 10:

```
- Plus de 10 secondes sans détection → il faut éteindre la LED.
```python
            bridge.call("setLedState", False)
            print("LED OFF (10 s sans personne)")

```
Extinction physique de la LED côté STM32.
Journal dans la console.
```python
        time.sleep(0.5)

```
- Vérifie toutes les 500 ms.
- Évite de gaspiller du CPU.

---

## 🟦 9. Lancement du thread
```python
threading.Thread(target=led_watcher, daemon=True).start()

```
- Lance led_watcher() dans un thread à part.
- daemon=True : s’arrête automatiquement lorsque l’application se termine.

---

 ## 🟦 10. Lancement de l’application UNO Q

```python
App.run()

```
- Démarre la boucle principale App Lab.
- Cette fonction est bloquante :
  - la caméra tourne,
  - la détection tourne,
  - le thread led_watcher tourne en parallèle.
  - 
---

## 🟩 Résumé global  
Voici ce que fait l’ensemble :
### 🎥 1. La brique VideoObjectDetection lit le flux vidéo
➡️ détecte "person".
### 💡 2. on_person_detected() est appelé
➡️ met à jour le timer,  
➡️ allume la LED par bridge.call().
### 🕒 3. Un thread surveille les 10 secondes d'inactivité
➡️ si aucune personne vue → LED OFF.
### 🔗 4. Le Bridge fait le lien
➡️ Linux → STM32 → LED_BUILTIN.
