# 🧠 Explication du code Python (UNO Q — Détection vidéo + LED)  
# README – Code Python : détection vidéo et pilotage de la LED (UNO Q)

Ce fichier décrit **ligne par ligne** le code Python utilisé dans `python/main.py` pour :

- analyser le flux vidéo avec la brique **VideoObjectDetection** ;
- détecter la présence d’une personne ;
- **allumer la LED_BUILTIN** du STM32 dès qu’une personne est vue ;
- **éteindre la LED 10 secondes** après la dernière détection.

---

## Code complet

```python
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
```

---

## Explication ligne par ligne

### Import des modules et briques

`from arduino.app_utils import App, Bridge`  
Importe depuis la librairie **Arduino UNO Q** deux composants essentiels :

- `App` : point d’entrée de l’application côté Linux.  
  C’est lui qui gère la **boucle principale**, la durée de vie de l’app et l’intégration avec App Lab.
- `Bridge` : fournit la **communication** entre le cœur Linux et le cœur STM32 (sketch C++).  
  On l’utilise plus bas avec `bridge.call("setLedState", ...)` pour appeler une fonction C++ exposée par `Bridge.provide(...)`.

---

`from arduino.app_bricks.video_objectdetection import VideoObjectDetection`  
Importe la brique modulaire **VideoObjectDetection** :

- gère la webcam (flux vidéo) ;
- applique un **modèle d’IA** côté Linux ;
- déclenche des **callbacks Python** dès qu’un objet est détecté (par ex. `"person"`).

---

`import time`  
Importe le module standard `time` :

- `time.time()` : donne l’heure actuelle (en secondes, float) ;
- `time.sleep()` : permet de faire une pause (en secondes).

On s’en sert pour :

- mémoriser **l’instant de la dernière détection** ;
- vérifier si **10 secondes** se sont écoulées ;
- temporiser dans le thread surveillant la LED.

---

`import threading`  
Importe le module standard `threading` :

- permet de créer des **threads** (tâches en parallèle) ;
- fournit aussi des **verrous** (`Lock`) pour protéger l’accès à des variables partagées.

On s’en sert pour :

- lancer un thread `led_watcher` qui tourne en arrière-plan ;
- synchroniser les accès à `LED_ON` et `LAST_DETECTION` avec `LOCK`.

---

### Création du détecteur vidéo

`# Détecteur vidéo`  
Commentaire : introduit le bloc de code qui initialise la brique de détection vidéo.

---

`video_detector = VideoObjectDetection(confidence=0.4, debounce_sec=1.5)`  
Crée l’instance **VideoObjectDetection** :

- `confidence=0.4` :  
  - seuil minimum de confiance (40 %) pour accepter une détection ;  
  - en dessous, la détection est ignorée.
- `debounce_sec=1.5` :  
  - anti-rebond temporel ;  
  - évite d’appeler le callback **trop souvent** pendant que la même personne reste dans le champ ;  
  - la brique attend 1,5 s entre deux déclenchements pour le même objet.

Cette instance va :

- se connecter au conteneur `ei-video-obj-detection-runner` ;
- recevoir les inférences de l’IA ;
- appeler nos callbacks `on_person_detected` et `on_all_detections`.

---

### Initialisation du Bridge vers le STM32

`# Bridge vers le STM32`  
Commentaire : annonce que le code suivant crée le lien avec le cœur STM32 (sketch .ino).

---

`bridge = Bridge()`  
Crée l’objet **Bridge** :

- côté C++, on a :  
  `Bridge.begin();` pour initialiser la communication ;  
  `Bridge.provide("setLedState", setLedState);` pour exposer une fonction C++.
- côté Python, on peut alors écrire :  
  `bridge.call("setLedState", True)` pour appeler `setLedState(true)` sur le STM32.

C’est **le canal** qui permet à la détection vidéo de **piloter la LED** du microcontrôleur.

---

### Variables d’état globales

`LED_ON = False`  
Variable globale qui mémorise **l’état logique de la LED** vu côté Python :

- `True` : Python considère que la LED est allumée (on a envoyé `setLedState(True)` au STM32) ;
- `False` : Python considère que la LED est éteinte.

Pourquoi ?  
Pour **éviter d’envoyer en boucle** des appels identiques :

- si la personne reste dans le champ, `on_person_detected()` serait appelé souvent ;
- avec `LED_ON`, on n’appelle `setLedState(True)` **que lors de la première détection** après une période sans personne.

---

`LAST_DETECTION = 0.0`  
Variable globale qui stocke **l’instant de la dernière détection** (en secondes, comme `time.time()`).

- mise à jour à chaque fois que `on_person_detected()` est appelé ;
- utilisée par `led_watcher()` pour savoir depuis combien de temps **on n’a plus vu de personne**.

Si `time.time() - LAST_DETECTION > 10.0`, cela signifie **plus de 10 s sans détection**.

---

`LOCK = threading.Lock()`  
Crée un **verrou (mutex)** :

- les variables `LED_ON` et `LAST_DETECTION` sont partagées entre :
  - le callback `on_person_detected()` (appelé par VideoObjectDetection, dans un thread interne) ;
  - le thread `led_watcher()` (créé par nous).
- pour éviter les **conditions de course**, on protège les accès avec :

```python
with LOCK:
    # accès / écriture thread-safe
```

---

### Callback de détection d’une personne

`# --- Callback quand une personne est détectée ---`  
Commentaire : introduit la fonction appelée lorsqu’un objet `"person"` est détecté dans l’image.

---

`def on_person_detected():`  
Déclare la fonction **callback** `on_person_detected` :

- appelée par `video_detector` quand une personne est détectée ;
- **ne prend pas d’arguments** : la signature est compatible avec `on_detect("person", ...)` de la brique.

---

`    global LED_ON, LAST_DETECTION`  
Indique à Python que l’on va **modifier** les variables globales `LED_ON` et `LAST_DETECTION` dans cette fonction.

Sans ce mot-clé `global`, Python créerait des variables locales de même nom, ce qui casserait notre logique.

---

`    now = time.time()`  
Lit l’heure actuelle (en secondes, float) :

- `now` représente le moment exact de cette détection ;
- on va l’utiliser pour mettre à jour `LAST_DETECTION`.

---

`    with LOCK:`  
Entre dans une **section critique** :

- garantit qu’un seul thread à la fois exécute le bloc ;
- protège l’accès et la mise à jour de `LAST_DETECTION` et `LED_ON`.

---

`        LAST_DETECTION = now`  
Met à jour l’instant de la dernière détection :

- chaque fois qu’une personne est vue, on remet `LAST_DETECTION` à `now` ;
- le thread `led_watcher()` s’en servira pour calculer le **temps écoulé** depuis la dernière personne.

---

`        print("🚨 Person detected in the video stream!")`  
Affiche un message dans la **console Python** :

- purement informatif ;
- utile pour vérifier que les callbacks fonctionnent bien et que les détections se déclenchent.

---

`        if not LED_ON:`  
Condition : “**si la LED n’est pas déjà allumée**”.

- évite d’appeler `setLedState(True)` à chaque frame où la personne reste dans le champ ;
- on ne fait qu’**une seule mise à ON** par séquence de présence.

---

`            try:`  
Début d’un bloc `try/except` :

- pour intercepter proprement d’éventuelles erreurs du Bridge ;
- évite de faire planter le programme Python si la communication échoue.

---

`                bridge.call("setLedState", True)`  
Appelle, via le Bridge, la fonction C++ exposée par le STM32 :

- côté C++ :  
  `Bridge.provide("setLedState", setLedState);`
- côté Python :  
  `bridge.call("setLedState", True)` équivaut à `setLedState(true)` sur le STM32.

Dans notre sketch .ino, on a :

```cpp
void setLedState(bool state) {
  digitalWrite(LED_BUILTIN, state ? LOW : HIGH);
}
```

Donc :

- `state == true` → `digitalWrite(LED_BUILTIN, LOW)` → LED allumée (logique active LOW sur UNO Q).

---

`                LED_ON = True`  
Met à jour l’état logique de la LED côté Python :

- indique qu’on vient de demander l’allumage de la LED ;
- la prochaine fois qu’une personne sera détectée, le `if not LED_ON:` sera faux, et on ne rappellera pas `setLedState(True)` inutilement.

---

`                print("LED ON")`  
Message de log :

- confirme dans la console que la commande d’allumage a été envoyée au STM32.

---

`            except Exception as e:`  
Début du bloc de gestion d’erreur :

- capture **toute exception** qui pourrait être levée dans le bloc `try` ;
- typiquement, problème de Bridge, communication, etc.

---

`                print("Bridge error:", e)`  
Affiche le message d’erreur du Bridge dans la console :

- utile pour le **debug** ;
- n’arrête pas le programme, juste une trace.

---

### Enregistrement du callback pour "person"

`video_detector.on_detect("person", on_person_detected)`  
Enregistre notre fonction comme callback **spécifique** à la classe `"person"` :

- `video_detector` : instance de `VideoObjectDetection` ;
- `"person"` : nom de la classe d’objet à surveiller ;
- `on_person_detected` : fonction à appeler quand l’IA détecte une personne.

En pratique : à chaque détection `"person"` avec une confiance ≥ 0.4, la brique appelle `on_person_detected()`.

---

### Callback générique pour toutes les détections

`# --- Callback pour toutes les détections (comme ton exemple) ---`  
Commentaire : introduit une fonction de log général pour **toutes** les classes détectées (personne, lit, souris, etc.).

---

`def on_all_detections(detections: dict):`  
Déclare une fonction qui reçoit **un dictionnaire** `detections` :

- typiquement de la forme :

```python
{
    "person": {"confidence": 0.86, "bounding_box_xyxy": (x1, y1, x2, y2)},
    "mouse":  {"confidence": 0.60, "bounding_box_xyxy": (...)}
}
```

C’est un callback plus **générique** que `on_person_detected`.

---

`    print("All detections:", detections)`  
Affiche toutes les détections brutes dans la console :

- très pratique pour **explorer** ce que renvoie le modèle d’IA ;
- permet de voir quelles classes sont reconnues (bed, mouse, tv, etc.).

---

`video_detector.on_detect_all(on_all_detections)`  
Enregistre ce callback pour recevoir **toutes** les détections :

- quel que soit l’objet (person, bed, mouse, tv, etc.) ;
- complémentaire de `on_detect("person", ...)` qui, lui, ne concerne que la classe `"person"`.

---

### Thread de surveillance de la LED

`# --- Thread qui éteint la LED 10 s après la DERNIÈRE détection ---`  
Commentaire : annonce que le bloc suivant gère l’extinction automatique de la LED, 10 secondes après la dernière personne vue.

---

`def led_watcher():`  
Déclare la fonction `led_watcher` :

- elle sera exécutée dans un **thread séparé** ;
- son rôle :  
  - surveiller périodiquement `LAST_DETECTION` ;  
  - éteindre la LED quand il n’y a plus eu de personne pendant plus de 10 s.

---

`    global LED_ON, LAST_DETECTION`  
Indique que cette fonction va **lire et modifier** les variables globales `LED_ON` et `LAST_DETECTION`.

---

`    while True:`  
Boucle infinie du thread de surveillance :

- ce thread tourne pendant toute la durée de l’application ;
- on sort uniquement quand l’application se termine.

---

`        time.sleep(0.5)`  
Pause de 0,5 seconde à chaque tour :

- évite de boucler en permanence et de consommer inutilement du CPU ;
- une résolution de 500 ms est largement suffisante pour un timer de 10 s.

---

`        with LOCK:`  
Section critique protégée par le verrou :

- garantit un accès **cohérent** à `LED_ON` et `LAST_DETECTION` ;
- évite les conflits avec le callback `on_person_detected`.

---

`            if LED_ON and (time.time() - LAST_DETECTION > 10.0):`  
Condition clé :

1. `LED_ON` est `True` → la LED est actuellement considérée comme allumée ;
2. `time.time() - LAST_DETECTION > 10.0` → plus de **10 secondes** se sont écoulées depuis la dernière détection de personne.

Si ces deux conditions sont réunies :

- cela signifie : **“LED allumée mais aucune personne vue depuis 10 s”** ;
- on décide donc de l’éteindre.

---

`                try:`  
Début du bloc `try` pour appeler le Bridge sans faire planter le programme en cas d’erreur.

---

`                    bridge.call("setLedState", False)`  
Envoie la commande au STM32 :

- appelle `setLedState(false)` côté C++ ;
- dans le sketch, `state == false` ⇒ `digitalWrite(LED_BUILTIN, HIGH)` ⇒ LED éteinte (logique active LOW).

---

`                    LED_ON = False`  
Met à jour l’état logique de la LED côté Python :

- indique que la LED est maintenant éteinte ;
- le prochain passage dans `on_person_detected()` pourra donc la rallumer si une personne réapparaît.

---

`                    print("LED OFF (10 s sans personne)")`  
Message de log clair :

- indique qu’on vient d’éteindre la LED **parce que 10 s se sont écoulées sans détection**.

---

`                except Exception as e:`  
Bloc de gestion d’erreur en cas de problème de communication via le Bridge.

---

`                    print("Bridge error:", e)`  
Affiche l’erreur dans la console Python sans interrompre l’application.

---

### Lancement du thread de surveillance

`threading.Thread(target=led_watcher, daemon=True).start()`  
Crée et démarre un **nouveau thread** :

- `target=led_watcher` : la fonction exécutée dans ce thread sera `led_watcher()` ;
- `daemon=True` :
  - le thread est marqué comme **daemon** ;
  - il s’arrête automatiquement quand le programme principal se termine (pas besoin de `join()`) ;
- `.start()` lance réellement le thread.

Ce thread tourne **en arrière-plan** pendant que `App.run()` gère la boucle principale et le flux vidéo.

---

### Lancement de l’application UNO Q

`# --- Lancement ---`  
Commentaire : signale le bloc final qui démarre l’application.

---

`App.run()`  
Point d’entrée de l’application côté Linux :

- démarre l’infrastructure App Lab ;
- connecte les briques (VideoObjectDetection, Bridge, WebUI si utilisé) ;
- gère la boucle principale (événements, threads, websockets…).

C’est un appel **bloquant** :

- tant que l’application est en cours d’exécution, on reste dans `App.run()` ;
- le thread `led_watcher` continue, lui, de tourner en parallèle grâce à `daemon=True`.

---

## Résumé global du comportement

- La brique **VideoObjectDetection** :
  - surveille la webcam ;
  - appelle `on_person_detected()` à chaque personne détectée ;
  - appelle `on_all_detections()` pour loguer toutes les classes d’objets vues.

- Le **Bridge** :
  - relie le code Python au sketch STM32 ;
  - permet d’appeler `setLedState(bool)` côté C++.

- Le callback `on_person_detected()` :
  - met à jour `LAST_DETECTION` (heure de la dernière personne vue) ;
  - allume la LED (via `setLedState(True)`) si elle était éteinte.

- Le thread `led_watcher()` :
  - toutes les 0,5 s :
    - regarde depuis combien de temps il n’y a plus eu de personne ;
    - si plus de 10 s et LED allumée → envoie `setLedState(False)` pour éteindre la LED.

- `App.run()` :
  - garde l’application en vie ;
  - assure le bon fonctionnement de tous les services UNO Q / App Lab.

Ce fichier constitue donc la **documentation détaillée** du comportement Python côté Linux dans ce projet.

## Vue sortie console côté STM32 :

![arduino](../../Assets/arduino-console-STM32.png)
