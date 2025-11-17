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






```python
# code ici
```
```python
# code ici
```
```python
# code ici
```
```python
# code ici
```
```python
# code ici
```
```python
# code ici
```
```python
# code ici
```
```python
# code ici
```
```python
# code ici
```
