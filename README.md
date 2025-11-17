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

🔧 1. Matériel utilisé
Placez le matériel comme ci-dessous :
