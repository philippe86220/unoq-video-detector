# unoq-video-detector
Détection vidéo + activation LED avec l’Arduino UNO Q
Ce projet montre comment utiliser l’Arduino UNO Q, une webcam USB et Arduino App Lab 0.2.0 pour :
- activer un pipeline de détection vidéo temps réel,
- repérer une personne ou un visage,
- déclencher l’allumage de la LED_BUILTIN sur le STM32 pendant 10 secondes,
- gérer la logique complète entre le cœur Linux (Python) et le cœur STM32 (C++).
  
Tout fonctionne sans code HTML, uniquement via :
✔️ Python (Linux)
✔️ C++ (STM32)
✔️ Brick Video Object Detection
✔️ Le Bridge interne entre les deux cœurs

---

## 🔧 1. Matériel utilisé
Placez le matériel comme ci-dessous :
![Materiel](Assets/hardware-setup.png)

**Liste du matériel**   
- Arduino UNO Q
- Webcam USB compatible Linux
- HUB USB-C (avec Power Delivery + USB-A)
- Câble USB-C ↔ USB-C
- Alimentation 5V / USB-C PD

## 📡 2. Connexion de la UNO Q à Arduino App Lab  
### 2.1. Brancher d’abord le matériel
➡️ La UNO Q s’allume  
➡️ Le hub alimente la caméra  
➡️ L’ensemble va être détecté par App Lab via Wi-Fi  

### 2.2. Lancer Arduino App Lab
L’icône Wi-Fi apparaît automatiquement.
![App](Assets/app-lab-wifi.png)

### 2.3. Cliquer sur la UNO Q détectée
App Lab affiche une boîte pour entrer le mot de passe Wi-Fi de la carte.
![App](Assets/app-lab-login.png)

Une fois validé, vous accédez à l’interface principale.

---

## 🆕 3. Créer un nouveau projet App Lab
Cliquer sur My Apps (barre de gauche)  
![App](Assets/app-lab-myapps.png)

Cliquer sur Create New App +
Donner un nom, par exemple :
unoQ-video-detector
L’arborescence du projet contient automatiquement :
